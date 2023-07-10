#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import click
from rich import box
from rich.panel import Panel
from rich.table import Column, Table
from rich.text import Text

from configs import charsets
from core.console import HydroConsole


@click.group(__name__, short_help='字符工具')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def character():
    """
    字符、字符串、字符集、HEX相关工具。

    HEX是一种基于16个可打印字符的二进制数据表示方法，每个字节使用两个十六进制的字符表示。

    标准编码：
    https://docs.python.org/zh-cn/3/library/codecs.html#standard-encodings
    """


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


@character.command('encode', short_help='将字符串转换为HEX')
@click.option('-e', '--encoding', default='UTF-8', help='字符串编码，默认是 UTF-8。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def encoder(encoding):
    """
    将字符串按照指定编码转换为HEX。
    """
    console = HydroConsole(stderr=True)
    try:
        string = console.ask('输入任意字符串：', style='cyan')
    except KeyboardInterrupt:
        exit(0)
    try:
        binary = string.encode(encoding)
    except LookupError:
        console.warning('无法识别的编码', encoding)
    except:
        console.print_exception()
        exit(-1)
    else:
        print(binary.hex())


@character.command('decode', short_help='将HEX转换为字符串')
@click.option('-e', '--encoding', default='UTF-8', help='字符串编码，默认是 UTF-8。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def decoder(encoding):
    """
    按照指定编码将HEX转换为字符串。
    """
    console = HydroConsole(stderr=True)
    try:
        raw = console.ask('输入HEX：', style='cyan')
        print()
    except KeyboardInterrupt:
        exit(0)
    try:
        data = bytes.fromhex(raw)
    except ValueError:
        console.warning('HEX格式错误。')
        exit(-1)
    try:
        string = data.decode(encoding)
    except LookupError:
        console.warning('无法识别的编码', encoding)
    except:
        console.print_exception()
    else:
        print(string)


@character.command('map', short_help='绘制HEX字节分布表', no_args_is_help=False)
@click.option('-e', '--encoding', default='UTF-8', help='解析字符串时使用的编码，默认是 UTF-8。')
@click.option('-x', '--hex', 'hexs', is_flag=True, help='输入并解析HEX，而不是字符串。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def mapper(encoding: str, hexs: bool):
    """
    映射字符串或HEX，并绘制HEX字节分布表。

    输出结果的
    b 指的是比特数目 bits，
    B 指的是字节数目 bytes，
    C 指的是字符个数 characters。
    """
    console = HydroConsole()
    if hexs:
        try:
            string = console.ask('输入HEX：', style='cyan')
            binary = bytes.fromhex(string)
        except KeyboardInterrupt:
            exit(0)
        except ValueError:
            console.warning('HEX格式错误。')
            exit(-1)
    else:
        try:
            string = console.ask('输入字符串：', style='cyan')
            binary = string.encode(encoding)
        except KeyboardInterrupt:
            exit(0)
        except LookupError:
            console.warning('无法识别的编码。', encoding)
            exit(-1)
        except UnicodeEncodeError:
            console.warning(f'{encoding} 解码失败。')
            exit(-1)

    bs = set(binary)
    status = Text().join([
        Text(str(len(binary) * 8), 'bright_cyan'), Text('b, '),
        Text(str(len(binary)), 'bright_cyan'), Text('B, '),
        Text(str(len(string)), 'bright_cyan'), Text('C, '),
        Text(f'<{encoding or "HEX"}>'),
    ])
    body = Text('\n').join(
        Text(',', 'bright_black').join(
            Text(
                f'{(b := j * 16 + i):02x}',
                'white' if b in bs else 'bright_black'
            )
            for i in range(16)
        )
        for j in range(16)
    )
    panel = Panel(body, expand=False, subtitle=status, border_style="dim")
    console.print(panel)


@character.command('repeat', short_help='重复生成输入的字符串')
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


character.add_command(encoder, 'enc')
character.add_command(decoder, 'dec')
character.add_command(repeater, 'rep')

if __name__ == '__main__':
    character()
