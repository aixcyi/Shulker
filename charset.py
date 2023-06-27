#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import click
from rich import box
from rich.table import Table, Column

from configs import charsets
from core.console import HydroConsole


@click.command(__name__, short_help='列出所有预设的字符集')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def shower():
    table = Table(
        Column('名称'),
        Column('字符集', overflow='ignore'),
        box=box.SIMPLE_HEAD,
    )
    for attr in charsets.__dict__:
        if attr.startswith('_'):
            continue
        table.add_row(attr, charsets.__dict__[attr])

    console = HydroConsole()
    console.print(table)


if __name__ == '__main__':
    import sys

    shower(sys.argv[1:])
