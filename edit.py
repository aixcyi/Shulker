#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import os

import click
from rich.table import Table

from core.configurators import FileShortcut
from core.console import HydroConsole

try:
    from configs import FILES
except ImportError:
    HydroConsole(stderr=True).warning(
        '使用此命令前需要在 ./configs/__init__.py 中配置 FILES'
    )
    exit(-1)

shortcuts: dict[str, FileShortcut] = {f.name: f for f in FILES}


@click.command(__name__, short_help='用编辑器打开文件', no_args_is_help=False)
@click.argument('filename', required=False)
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def opener(filename):
    """
    用预设的编辑器打开预设的文件。

    若不提供 FILENAME 可以列出所有预设文件及相应的编辑器。
    """
    console = HydroConsole()
    monitor = HydroConsole(stderr=True)

    if filename is None:
        table = Table(box=None)
        for f in FILES:
            table.add_row(f.name, f.path)
            table.add_row('', f.editor, style='dim')
            table.add_row()
        console.print(table)
        exit(0)

    if filename not in shortcuts:
        monitor.warning('未配置文件', filename)
        exit(-1)

    shortcut = shortcuts[filename]

    os.system(f'{shortcut.editor} {shortcut.path}')


if __name__ == '__main__':
    import sys

    opener(sys.argv[1:])
