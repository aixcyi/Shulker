#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import pkgutil
from typing import Callable, Generator, NoReturn

import click
from rich.text import Text

import foxes
from core.console import HydroConsole
from core.shell import CommandInfo, Shell


def load_foxes() -> list[click.Command]:
    def enum_commands() -> Generator[click.Command, None, None]:
        """
        枚举变量 "module" 中出现的所有继承 click.Command 的符号。
        """
        for v in module.__dict__.values():
            if isinstance(v, click.Command):
                # 原名（foxes.adc.py）包含了父包名和后缀，故需去除
                v.name = str(v.name).replace('.py', '', 1)
                _, _, v.name = v.name.rpartition('.')
                yield v

    commands = []
    for importer, name, is_pkg in pkgutil.iter_modules(foxes.__path__, f'{foxes.__name__}.'):
        module = importer.find_module(name).load_module(name)
        cmds = list(enum_commands())
        groups = [v for v in cmds if isinstance(v, click.Group)]
        commands.extend(groups if groups else cmds)

    return commands


class FoxLoop(Shell):
    intro = 'Welcome to shulker fox shell.\n'
    prompt = Text('fox> ', style='cyan')
    stdin = HydroConsole()
    stdout = stdin
    stderr = HydroConsole(stderr=True)

    def postload(self):
        self.commands |= {
            cmd.name: CommandInfo(
                func=cmd,
                hidden=cmd.hidden,
                deprecated=cmd.deprecated,
                description=cmd.short_help,
            )
            for cmd in load_foxes()
        }
        super().postload()

    def invoke(self, cmd: Callable, argv: tuple) -> NoReturn:
        cmd(*argv, obj=self.cache, standalone_mode=False)

    def do_cls(self, *argv: str, **kwargs) -> NoReturn:
        """清空屏幕上的内容"""
        self.stdout.clear()


@click.command(__name__, short_help='进入可维持上下文的foxloop执行指令', no_args_is_help=False)
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def looper():
    """
    进入能够维持上下文及内存状态的命令行循环中执行指令。
    """


if __name__ == '__main__':
    import sys

    # 循环内的 click 指令的 Exit 异常会在 standalone_mode=False 时抛给外面的 click 指令，
    # 所以这里避免在 click 指令内部进行循环。
    if sys.argv[1:]:
        looper()
    else:
        fox = FoxLoop()
        fox.run()
