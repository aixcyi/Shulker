#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
from random import choices

import click

from core.console import HydroConsole

try:
    from configs import charsets
except ImportError:
    HydroConsole(stderr=True).warning(
        '请先配置 ./configs/charsets.py'
    )
    exit(-1)


@click.command(__name__, short_help='随机生成 LENGTH 个字符', no_args_is_help=True)
@click.argument('length', type=int)
@click.option('-d', '--digit', is_flag=True, help='向字符集加入阿拉伯数字。')
@click.option('-D', '--digit-safe', is_flag=True, help='向字符集加入0和1之外的所有阿拉伯数字。')
@click.option('-u', '--upper', is_flag=True, help='向字符集加入大写英文字母。')
@click.option('-U', '--upper-safe', is_flag=True, help='向字符集加入I和O之外的所有大写英文字母。')
@click.option('-l', '--lower', is_flag=True, help='向字符集加入小写英文字母。')
@click.option('-L', '--lower-safe', is_flag=True, help='向字符集加入l之外的所有小写英文字母。')
@click.option('-s', '--symbol', is_flag=True, help='向字符集加入不用按Shift键就能输入的符号。')
@click.option('-S', '--symbol-shift', is_flag=True, help='向字符集加入必须按Shift键才能输入的符号。')
@click.option('-x', '--hex', is_flag=True, help='向字符集加入十六进制所有字符。')
@click.option('-c', '--charset', 'names', metavar='NAME', multiple=True, help='向字符集添加预设的字符集。可多选。')
@click.option('-o', '--once', is_flag=True, help='一次性输出所有，而不是一行行输出。')
@click.option('-q', '--qty', metavar='LINES', type=int, default=1, help='生成多少行。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def generator(length: int, names: tuple[str], once: bool, qty: int, **csn: bool):
    """
    随机生成 LENGTH 个字符。

    使用 char set 命令查看所有预设的字符集。

    通常来说，如果要生成按比特数计的字符串，更建议用 mkbin 或 mkbit 命令。
    """
    csn['symbol_normal'] = csn.pop('symbol')
    names += tuple(k for k, v in csn.items() if v)
    chars = ''.join(getattr(charsets, name, '') for name in names)

    console = HydroConsole(stderr=True)
    if not chars:
        console.warning('字符集空空如也。请使用 -c 参数指定一些字符集。')
        exit(-1)

    dataset = (''.join(choices(chars, k=length)) for _ in range(qty))
    if once:
        print('\n'.join(dataset))
    else:
        for d in dataset:
            print(d)


if __name__ == '__main__':
    import sys

    generator(sys.argv[1:])
