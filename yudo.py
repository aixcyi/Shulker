#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
"""
Usage: yudo.py help|-h|--help
       yudo.py [list|-l|--list]
       yudo.py [debug|-d|--debug] <command> <action>
       yudo.py [debug|-d|--debug] <command> [<option> ...]

  运行预设的指令（程序／项目／脚本）。

Arguments:
  command       指令名称。
  action        指令的快速动作。不存在时会传递给指令本身。
  option        直接传递给指令的参数。
  debug         同 --debug
  list          同 --list
  help          同 --help

Options:
  -l, --list    列出所有预设的目标及相应的配置。
  -d, --debug   解析配置并形成脚本，但不执行，而是直接输出。
  -h, --help    列出这份帮助信息。
"""
import os

import click
from rich import box
from rich.table import Table, Column

from core.configurators import Command
from core.console import HydroConsole

try:
    from configs import COMMANDS
except ImportError:
    HydroConsole(stderr=True).warning(
        '使用此命令前需要在 ./configs/__init__.py 中配置 COMMANDS'
    )
    exit(-1)

# 让 shulker 检测到
interface = click.Command(__name__, short_help='运行预设的指令（程序／项目／脚本）')

# 配置里的所有指令
commands: dict[str, type[Command]] = {v.name: v for v in COMMANDS}


def show_help():
    print(__doc__)
    exit(0)


def list_commands():
    table = Table('指令', '描述／备注', '动作', box=box.SIMPLE_HEAD)
    for cmd in COMMANDS:
        table.add_row(cmd.name, cmd.note, '、'.join(cmd.actions.keys()))

    console = HydroConsole()
    console.print(table)
    exit(0)


def execute(name, *options, debug=False):
    monitor = HydroConsole(stderr=True)
    console = HydroConsole()
    if name is None:
        monitor.warning('未调用任何指令')
        exit(-1)
    if name not in commands:
        monitor.warning('未找到指令', name)
        exit(-1)

    command = commands[name](*options)

    if debug:
        table = Table(
            Column(justify='right'),
            Column(),
            Column(),
            box=None,
            padding=(0, 0, 0, 1),
        )
        for index, line in enumerate(command.scripts, start=1):
            table.add_row(str(index), '│', line)
        console.print(table)
        exit(0)
    try:
        os.system(command.script)
    except KeyboardInterrupt:
        pass
    exit(0)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        list_commands()

    myself, exe, *argv = sys.argv

    if exe in ('-h', '--help', 'help'):
        show_help()
    elif exe in ('-l', '--list', 'list'):
        list_commands()
    elif exe in ('-d', '--debug', 'debug'):
        exe, *argv = argv or [None]
        execute(exe, *argv, debug=True)
    else:
        execute(exe, *argv, debug=False)
