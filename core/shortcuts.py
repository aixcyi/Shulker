"""
快捷函数工具库。
"""
from typing import TypeVar, Callable, Any, NoReturn

import click

T = TypeVar('T')


def ask(tips: str,
        mapper: type[T] | Callable[[Any], T] = str,
        default: T = '',
        newline: bool = False) -> T:
    """
    请求输入。

    :param tips: 输入前的提示。
    :param mapper: 类型，或者一个返回目标类型的函数。
    :param default: 默认值。使用 mapper 转换后出现异常时返回。
    :param newline: 是否在新的一行提示输入。
    :return: 转换后的值。
    :raise KeyboardInterrupt: 输入被 Ctrl-C 中断。
    """
    click.secho(tips, err=True, nl=newline, fg='cyan')
    value = input()
    try:
        return mapper(value) if callable(mapper) else value
    except:
        return default


def warning(*lines, color='yellow', newline=True) -> NoReturn:
    """
    打印警告。

    :param lines: 要打印的消息。
    :param color: 字体颜色。
    :param newline: 是否另起一行再打印。
    :return: 无。
    """
    click.secho('\n'.join(lines), nl=newline, err=True, fg=color)


def printif(anything: Any) -> NoReturn:
    """
    当为 ``None`` 时提示没有输出，当为空字符串时也进行相关提示。
    """
    if anything is None:
        click.secho('（没有任何输出）', err=True, fg='yellow')
    elif anything == '':
        click.echo('')
        click.secho('（输出了空字符串）', err=True, fg='magenta')
    else:
        print(anything)
