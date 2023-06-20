#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import importlib.util
import platform
import sys
from pathlib import Path
from typing import Iterable, Any

import click
from rich import box
from rich.console import Console
from rich.style import Style
from rich.table import Table
from rich.text import Text

ego: Path = Path(__file__).absolute()  # 当前文件
root: Path = ego.parent  # 项目根目录


def get_sources() -> Iterable:
    """
    获取相同目录下除自身外的所有非符号链接的python源文件。
    """
    return (
        src for src in root.glob('*.py')
        if src != ego and src.is_file() and not src.is_symlink()
    )


def get_commands() -> list[click.Command]:
    """
    扫描根目录下非子目录中所有python源码里包含的基于 click.Command 的符号。
    """
    interfaces = []

    def list_commands():
        """
        枚举变量 "module" 中出现的所有继承 click.Command 的符号。
        """
        for v in module.__dict__.values():
            if isinstance(v, click.Command):
                # 命令名默认是被装饰的函数名，这里改成文件名做到调用与声明一致
                v.name = str(v.name).replace('.py', '', 1)
                yield v

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
        cmds = list(list_commands())
        groups = [v for v in cmds if isinstance(v, click.Group)]
        interfaces.extend(groups if groups else cmds)
    return interfaces


@click.group(__file__)
@click.help_option('-h', '--help', help='显示此帮助信息。')
def cli():
    """
    来自末地之城的潜影盒，藏着不为人知的魔法指令。
    """
    pass


@cli.command('list', short_help='列出项目下所有命令。')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def show_commands():
    console = Console()
    table = Table(
        '指令', '说明',
        box=box.SIMPLE_HEAD,
        # row_styles=['white', 'bright_white'],
    )
    for cmd in (c for c in get_commands() if not c.hidden):
        name = Text(cmd.name, Style(color='yellow')) if cmd.deprecated else cmd.name
        table.add_row(name, cmd.short_help)

    if table.row_count > 0:
        console.print(table)
    else:
        console.print(Text('未找到任何命令。', 'yellow'))


@cli.command('status', short_help='展示Python环境信息。')
def show_status():
    print('\n项目目录：')
    print(' ', str(root))
    print('\n当前解释器：')
    print(' ', sys.executable)
    if platform.system() == 'Windows':
        show_registry()


def show_registry():
    import winreg

    def read_reg(key: int, subkey: str, name='') -> Any:
        with winreg.OpenKeyEx(key, subkey) as h:
            _value, _type = winreg.QueryValueEx(h, name)
            return _value

    console = Console()
    console.print('\n注册表相关：')
    console.print(r'  [HKEY_CLASSES_ROOT\py_auto_file\shell\open\command]')
    console.print('  @=' + read_reg(winreg.HKEY_CLASSES_ROOT, r'py_auto_file\shell\open\command'))
    console.print()
    console.print(r'  [HKEY_CLASSES_ROOT\.py]')
    console.print(r'  @=' + read_reg(winreg.HKEY_CLASSES_ROOT, r'.py'))


if __name__ == '__main__':
    cli(sys.argv[1:])
