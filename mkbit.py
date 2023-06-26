#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
from base64 import b64encode, b85encode, b32encode
from math import ceil
from random import getrandbits

import click

from core.features import HydroConsole


@click.command(__name__, short_help='随机生成 BITS 比特二进制数据', no_args_is_help=True)
@click.argument('bits', type=int)
@click.option('--base64', is_flag=True, help='输出base64编码结果。')
@click.option('--base85', is_flag=True, help='输出base85编码结果。')
@click.option('--base32', is_flag=True, help='输出base32编码结果。')
@click.option('-b', metavar='BASE', type=int, help='输出base64/85/32编码结果。')
@click.option('-i', '--integer', is_flag=True, help='输出一个十进制有符号整数。')
@click.option('-a', '--array', is_flag=True, help='以十进制无符号整数数组形式输出。')
@click.option('-o', '--once', is_flag=True, help='一次性输出所有，而不是一行行输出。')
@click.option('-q', '--qty', metavar='LINES', type=int, default=1, help='生成多少行。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def generator(
        bits, base64, base85, base32, b, integer, array, once, qty,
):
    """
    随机生成 BITS 比特的二进制数据，并以某种格式输出为文本。默认输出HEX。
    """
    console = HydroConsole(stderr=True)

    if bits < 1:
        console.warning('BITS 必须是一个正整数')
        exit(-1)

    byteqty = ceil(bits / 8)
    dataset = (getrandbits(bits) for _ in range(qty))
    byteset = (d.to_bytes(byteqty, 'big') for d in dataset)
    if integer:
        dataset = map(str, dataset)
    elif array:
        dataset = (','.join(map(str, d)) for d in byteset)
    elif base64 or b == 64:
        dataset = (b64encode(d).decode('ASCII') for d in byteset)
    elif base85 or b == 85:
        dataset = (b85encode(d).decode('ASCII') for d in byteset)
    elif base32 or b == 32:
        dataset = (b32encode(d).decode('ASCII') for d in byteset)
    else:
        dataset = (d.hex() for d in byteset)

    if once:
        print('\n'.join(dataset))
    else:
        for d in dataset:
            print(d)


if __name__ == '__main__':
    import sys

    generator(sys.argv[1:])
