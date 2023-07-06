#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import click
from rich import box
from rich.table import Table, Column

from configs import charsets
from core.console import HydroConsole


@click.group(__name__, short_help='字符及字符串相关工具')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def character():
    pass


@character.command('set', short_help='列出所有预设的字符集')
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


@character.command('rep', short_help='重复生成输入的字符串')
@click.argument('times', type=int)
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def repeater(times):
    console = HydroConsole()
    try:
        string = console.ask('输入需要重复的字符串：', style='cyan')
    except KeyboardInterrupt:
        exit(0)

    string *= times
    print(string)


@character.command('len', short_help='测量字符个数')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def measurer():
    console = HydroConsole()
    try:
        string = console.ask('输入任意字符串：', style='cyan')
    except KeyboardInterrupt:
        exit(0)

    console.print('字符个数：', len(string))


if __name__ == '__main__':
    character()
