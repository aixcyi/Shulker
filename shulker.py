#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import importlib.util
import platform
import sys
from pathlib import Path
from typing import Iterable, Any, Generator

import click
from rich import box
from rich.table import Table
from rich.text import Text

from core import version
from core.console import HydroConsole

ego: Path = Path(__file__).absolute()  # 当前文件
root: Path = ego.parent  # 项目根目录


def get_sources() -> Iterable:
    """
    获取相同目录下除自身外的所有非符号链接的python源文件。
    """
    return (
        src for src in root.glob('*.py')
        if src.is_file() and not src.is_symlink()
    )


def get_shebang(src: Path) -> str | None:
    """
    获取某个python脚本的shebang，没有则返回 None。
    """
    with src.open('r', encoding='UTF-8') as f:
        for line in f:
            return line.rstrip('\r\n') if line.startswith('#!') else None


def set_shebang(src: Path, interpreter: str) -> str:
    """
    修改某个python脚本的shebang，若失败则返回字符信息，成功时返回空字符串。
    """
    try:
        with src.open('r+', encoding='UTF-8') as f:
            f.seek(0)
            if f.readline().startswith('#!'):
                f.seek(0)
                lines = f.readlines()
                lines[0] = '#!' + interpreter + '\n'
                f.seek(0)
                f.writelines(lines)
                f.truncate()
                return ''
            else:
                # TODO
                return '未有shebang，不作修改'
    except Exception as e:
        return str(e)


@click.group(__name__, short_help='指令管理')
@click.version_option(version, '-v', '--version', prog_name='shulker', help='显示版本信息。')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def cli():
    """
    来自末地之城的潜影盒，藏着不为人知的魔法指令。
    """
    pass


@cli.command('list', short_help='列出项目下所有脚本提供的指令')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def scanner():
    """
    扫描根目录下不在子目录中的所有python脚本，动态导入后执行以获取所有指令。

    当存在基于 click.Group 的类时只获取它，否则获取所有基于 click.Command 的类。
    """

    def enum_commands() -> Generator[click.Command, None, None]:
        """
        枚举变量 "module" 中出现的所有继承 click.Command 的符号。
        """
        for v in module.__dict__.values():
            if isinstance(v, click.Command):
                # 命令名默认是被装饰的函数名，这里改成文件名做到调用与声明一致
                v.name = str(v.name).replace('.py', '', 1)
                yield v

    commands = []
    for src in get_sources():
        # 根据绝对路径导入源码并运行
        # 相当于 from (src.parent) import (src) as module
        spec = importlib.util.spec_from_file_location(src.name, src)
        module = importlib.util.module_from_spec(spec)
        sys.modules[src.name] = module
        spec.loader.exec_module(module)

        # 获取源码中 click.Command 的所有子类，
        # 然后过滤出 click.Group 的子类，
        # 最后，如果有后者就选择后者，否则选择前者。
        # 因为如果使用了 click.Group ，
        # click是不会再将 click.Command 显示出来的。
        cmds = list(enum_commands())
        groups = [v for v in cmds if isinstance(v, click.Group)]
        commands.extend(groups if groups else cmds)

    # table = Table('指令', '说明', box=box.SIMPLE_HEAD, row_styles=["dim", ""])
    table = Table('指令', '说明', box=box.SIMPLE_HEAD)
    for cmd in (c for c in commands if not c.hidden):
        table.add_row(
            Text(cmd.name, 'yellow') if cmd.deprecated else cmd.name,
            cmd.short_help
        )

    console = HydroConsole()
    if table.row_count > 0:
        console.print(table)
    else:
        console.warning('未找到任何命令。')


@cli.command('shebang', short_help='管理项目下所有脚本的shebang')
@click.option('-s', '--set', 'change', is_flag=True, help='修改所有脚本的shebang')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def manager(change):
    """
    列出或修改项目下所有python脚本的shebang。
    """
    table = Table('文件名', 'Shebang', box=box.SIMPLE_HEAD)
    for src in get_sources():
        table.add_row(
            get_shebang(src) or Text('(未设置)', style='magenta'),
            Text(src.name, 'cyan' if src == ego else ''),
        )

    console = HydroConsole()
    console.print(table)
    console.print(' ', root / '*.py', '\n')

    if not change:
        return
    try:
        shebang = console.ask('输入新的shebang，或按 Ctrl-C 键终止：\n#!')
    except KeyboardInterrupt:
        shebang = ''
    if not shebang:
        console.warning('\n完毕。未作修改。')
        exit(0)

    with console.status('正在修改shebang...', spinner='bouncingBar'):
        for src in get_sources():
            console.print(src.name, end='  ')
            result = set_shebang(src, shebang)
            console.print(
                result or '成功',
                style='bright_magenta' if result else 'green',
            )
    console.print('完毕\n')


@cli.command('status', short_help='列出Python环境信息')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def explorer():
    console = HydroConsole()
    console.print('\n项目目录：')
    console.print(' ', str(root))
    console.print('\n当前解释器：')
    console.print(' ', sys.executable)
    if platform.system() != 'Windows':
        return

    import winreg

    def read_reg(key: int, subkey: str, name='') -> Any:
        with winreg.OpenKeyEx(key, subkey) as h:
            _value, _type = winreg.QueryValueEx(h, name)
            return _value

    console.print('\n注册表相关：')
    console.print(r'  [HKEY_CLASSES_ROOT\py_auto_file\shell\open\command]')
    console.print('  @=' + read_reg(winreg.HKEY_CLASSES_ROOT, r'py_auto_file\shell\open\command'))
    console.print()
    console.print(r'  [HKEY_CLASSES_ROOT\.py]')
    console.print(r'  @=' + read_reg(winreg.HKEY_CLASSES_ROOT, r'.py'))


if __name__ == '__main__':
    cli(sys.argv[1:])
