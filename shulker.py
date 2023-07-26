#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import sys

try:
    import importlib.util
    from pathlib import Path
    from typing import Iterable, Generator, Any

    import click
    from rich import box
    from rich.panel import Panel
    from rich.style import Style
    from rich.table import Table, Column
    from rich.text import Text
except ImportError as exc_info:
    raise ImportError(
        'YOU ARE USING THIS PYTHON:\n' + str(sys.executable)
    ) from exc_info

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
                return '未有shebang，不作修改'
    except Exception as e:
        return str(e)


@click.group(__name__, short_help='指令管理')
@click.version_option(version, '-v', '--version', prog_name='shulker', help='显示版本信息。')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def cli():
    """
    来自深界七层的潜影盒，有终末嗟叹之诗刻于其上，藏着银狼那奇技淫巧般的指令
    """
    pass


@cli.command('list', short_help='列出项目下所有脚本提供的指令')
@click.option('-a', '--all', 'fully', is_flag=True, help='显示所有指令，包括隐藏的。')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def scanner(fully):
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
    for cmd in commands if fully else (c for c in commands if not c.hidden):
        table.add_row(
            Text(cmd.name, 'yellow' if cmd.deprecated else 'magenta' if cmd.hidden else ''),
            cmd.short_help
        )

    console = HydroConsole()
    if table.row_count > 0:
        console.print(table)
    else:
        console.warning('未找到任何命令。')


@cli.command('migrate', short_help='迁移到Linux／MacOS')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def migrator():
    """
    迁移到Linux／MacOS，一次性搞定：自定义shebang，添加执行权限，创建符号链接。
    """
    table = Table('文件', 'Shebang', box=box.SIMPLE_HEAD)
    for src in get_sources():
        src: Path
        lnk: Path = src.with_suffix('')

        if lnk.is_symlink() and lnk.readlink() == src:
            filename = Text(lnk.name, Style(color='cyan', bold=True)) + Text(' -> ', 'white')
        else:
            filename = Text()
        if src.stat().st_mode & 0o0111 > 0:
            filename += Text(src.name, Style(color='bright_green', bold=True)) + Text('*', 'white')
        else:
            filename += Text(src.name)

        shebang = get_shebang(src) or Text('(未设置)', style='magenta')

        table.add_row(filename, shebang)

    console = HydroConsole()
    console.print(table)
    console.print(' ', Text(str(root / '*.py')), '\n')

    try:
        shebang = console.ask('输入新的shebang，或按 Ctrl-C 键终止：\n#!')
    except KeyboardInterrupt:
        shebang = ''
    if not shebang:
        console.warning('\n终止。未作修改。')
        exit(0)

    console.print()
    for src in get_sources():
        console.print(Text(str(src)), end='  ')

        result = set_shebang(src, shebang)
        console.print(Text(result or 'shebang已修改', style='bright_red' if result else 'green'), end='  ')

        mode = src.stat().st_mode | 0o111
        src.chmod(mode)
        console.print(Text('执行权限已添加', style='green'), end='  ')

        lnk = src.with_suffix('')
        if lnk.is_symlink() and lnk.readlink() == src:
            console.print(Text('符号链接已存在', style='green'))
        else:
            existed = lnk.exists()
            try:
                lnk.symlink_to(src)
            except OSError:
                console.print(Text('不创建符号链接', style='green'))
                continue
            if existed:
                console.print(Text('符号链接已覆盖', style='yellow'))
            else:
                console.print(Text('符号链接已创建', style='green'))

    console.print('完毕')


@cli.command('unlink', short_help='删除项目根目录下所有符号链接')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def unlinker():
    console = HydroConsole()
    symlinks = (lnk for lnk in root.glob('*') if lnk.is_symlink() and lnk.is_file())

    with console.status('正在删除...', spinner='bouncingBar'):
        for lnk in symlinks:
            lnk: Path
            try:
                lnk.unlink()
            except FileNotFoundError:
                console.print(str(lnk), Text('不存在', style='yellow'))
            else:
                console.print(str(lnk), Text('完毕', style='green'))
    console.print('完毕')


@cli.command('fixreg', short_help='修复文件关联并导出注册表原配置')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def fixer():
    r"""
    将 [HKEY_CLASSES_ROOT\.py] 指向 py_auto_file，同时配置
    [HKEY_CLASSES_ROOT\py_auto_file\shell\open\command]
    为 "C:\Windows\py.exe" "%1" %*
    """
    import winreg

    console = HydroConsole(no_color=True)
    monitor = HydroConsole(stderr=True)
    p1 = Path(r'C:\Windows\py.exe')
    p2 = p1.home() / r'AppData\Local\Programs\Python\Launcher\py.exe'

    if p1.exists():
        py_auto_file = f'"{p1!s}" "%1" %*'
    elif p2.exists():
        py_auto_file = f'"{p2!s}" "%1" %*'
    else:
        monitor.warning(
            '以下路径都不存在，请尝试重新安装 Python 并勾选 py.exe 选项。',
            str(p1), str(p2), sep='\n',
        )
        exit(-1)

    def read(ancestor: int, path: str, name: str = ''):
        try:
            with winreg.OpenKeyEx(ancestor, path) as h:
                value, type_id = winreg.QueryValueEx(h, name)
                return value
        except FileNotFoundError:
            return ...

    # reg query HKCR\.py /ve
    # reg query HKCR\py_auto_file\shell\open\command /ve
    old_dot_py = read(winreg.HKEY_CLASSES_ROOT, '.py')
    old_py_auto_file = read(winreg.HKEY_CLASSES_ROOT, r'py_auto_file\shell\open\command')

    console.print('Windows Registry Editor Version 5.00')
    console.print()
    console.print(r'[HKEY_CLASSES_ROOT\.py]')
    console.print('@=', '(UNSET)' if old_dot_py is ... else old_dot_py, sep='')
    console.print()
    console.print(r'[HKEY_CLASSES_ROOT\py_auto_file\shell\open\command]')
    console.print('@=', '(UNSET)' if old_py_auto_file is ... else old_py_auto_file, sep='')

    def write(ancestor: int, path: str, name: str, value) -> str:
        try:
            with winreg.CreateKeyEx(ancestor, path) as h:
                winreg.SetValue(h, name, winreg.REG_SZ, value)
                return ''
        except OSError as e:
            return e.args[1] if len(e.args) >= 2 else str(e)

    # reg add HKCR\.py /ve /d "py_auto_file"
    # reg add HKCR\py_auto_file\shell\open\command /ve /d "\"C:\Windows\py.exe\" \"%1\" %*"
    err1 = write(winreg.HKEY_CLASSES_ROOT, '.py', '', 'py_auto_file')
    err2 = write(winreg.HKEY_CLASSES_ROOT, r'py_auto_file\shell\open\command', '', py_auto_file)
    monitor.print()
    monitor.print('-' * 32, style='bright_cyan')
    monitor.print(r'[HKEY_CLASSES_ROOT\.py]',
                  Text(err1 or '修改成功', 'red' if err1 else 'green'))
    monitor.print(r'[HKEY_CLASSES_ROOT\py_auto_file\shell\open\command]',
                  Text(err2 or '修改成功', 'red' if err2 else 'green'))


@cli.command('ref', short_help='列出参考信息')
@click.help_option('-h', '--help', help='显示此帮助信息。')
def explorer():
    console = HydroConsole()

    # noinspection SpellCheckingInspection
    references = [
        ('项目目录', str(root)),
        ('解释器', str(sys.executable)),
        ('解释器版本', sys.version),
        (),
        ('Python 字符编码', 'https://docs.python.org/zh-cn/3/library/codecs.html#standard-encodings'),
        ('RFC 4648', 'https://datatracker.ietf.org/doc/html/rfc4648.html'),
        ('Base64 码表', 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz123456789+/'),
        ('Safe Base64 码表', 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz123456789-_'),
        ('Base32 码表', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'),
        ('HEX Base32 码表', '0123456789ABCDEFGHIJKLMNOPQRSTUV'),
    ]

    try:
        from configs import REFERENCES
    except ImportError:
        # noinspection PyPep8Naming
        REFERENCES = []

    table = Table(Column(justify='right'), Column(overflow='fold'), box=None, show_header=False)

    for reference in references + REFERENCES:
        if not isinstance(reference, tuple | list):
            continue
        if not reference:
            table.add_row(end_section=True)
        else:
            table.add_row(*reference)

    console.print(Panel(table, expand=False, border_style='dim'))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        cli(['list'])
    else:
        cli(sys.argv[1:])
