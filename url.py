#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
from urllib.parse import urlsplit, quote_plus, quote, unquote_plus, unquote, parse_qsl

import click
from rich import box
from rich.style import Style
from rich.table import Table, Column
from rich.text import Text

from core.console import HydroConsole

PORTS = {
    'http': 80, 'https': 443, 'ftp': 21, 'ssh': 22,
    'postgresql': 5432, 'postgres': 5432,
    'mysql': 3306, 'redis': 6379,
}


@click.group('url', short_help='URL解析、编码、解码')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def operator():
    """
    解析URL各个部件、进行URL编码及URL解码。
    """


@operator.command('parse', short_help='解析一条URL')
@click.option('-e', '--encoding', default='UTF-8', help='用何种编码解析。默认是UTF-8。')
@click.option('-p', '--path', 'only_path', is_flag=True, help='单独获取路径（path）。')
@click.option('-q', '--query', 'only_query', help='单独获取某个查询参数的值，当参数不存在时返回整个query。')
@click.option('-f', '--skip-fragment', is_flag=True,
              help='禁止解析片段（fragment）。当#出现在URL路径中导致结果错误时使用，但可能导致query受污染。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def splitter(encoding, only_path, only_query, skip_fragment):
    """
    请求输入并解析一条URL。支持http、ftp等相似格式的字符串。
    """
    console = HydroConsole()
    try:
        url = console.ask('输入一条URL：', style='cyan')
    except KeyboardInterrupt:
        exit(0)
    info = urlsplit(url, allow_fragments=not skip_fragment)
    query = dict(parse_qsl(info.query, encoding=encoding)) if info.query else {}
    query: dict[str, str]

    # 单独输出
    if only_path:
        console.print(info.path)
        return
    elif only_query:
        console.print(query[only_query] if only_query in query else info.query)
        return

    # 渲染协议部分
    match info.scheme:
        case 'https':
            scheme = Text(info.scheme, Style(color='green'))
        case _:
            scheme = info.scheme

    # 渲染端口部分
    if info.port:
        port = Text(str(info.port), 'bright_cyan')
    else:
        port = PORTS.get(info.scheme, None)
        port = Text(('%d (默认)' % port) if port else '(默认)', 'bright_magenta')

    # 主表
    tb_main = Table('组件', Column('值', overflow='fold'), box=box.SIMPLE_HEAD)
    tb_main.add_row('协议', scheme)
    tb_main.add_row('主机地址', info.hostname)
    tb_main.add_row('端口号', port)
    tb_main.add_row('用户名', info.username)
    tb_main.add_row('密码', info.password)
    tb_main.add_row('路径', info.path)
    tb_main.add_row('fragment', info.fragment)

    # Query参数表
    tb_query = Table(
        '参数',
        Column('查询值', overflow='fold'),
        box=box.SIMPLE_HEAD,
        row_styles=["dim", ""],
    )
    for k, v in query.items():
        tb_query.add_row(k, v)

    console.print(tb_main)
    console.print(tb_query)


@operator.command('encode', no_args_is_help=False, short_help='URL编码')
@click.option('-e', '--encoding', default='UTF-8', help='字符串编码，默认是 UTF-8。')
@click.option('-p', '--plus', is_flag=True, help='将空格转义为 + 号，而不是直接编码为 %20 。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def encoder(encoding, plus):
    """
    对字符串进行URL编码，将非ASCII字符、保留字符等转换为 "%3A" 这种格式的字符串。
    """
    console = HydroConsole()
    try:
        string = console.ask('输入任意字符串：', style='cyan')
    except KeyboardInterrupt:
        string = ''
    if not string:
        exit(0)
    translate = quote_plus if plus else quote
    result = translate(string, encoding=encoding)
    print('\n', result, sep='')


@operator.command('decode', no_args_is_help=False, short_help='URL解码')
@click.option('-e', '--encoding', default='UTF-8', help='解析字符串时使用的编码，默认是 UTF-8。')
@click.option('-p', '--plus', is_flag=True, help='将 + 号转义为空格。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def decoder(encoding, plus):
    """
    对字符串进行URL解码，将 "%3A" 这种格式的字符串还原成原本的字符。
    """
    console = HydroConsole()
    try:
        string = console.ask('输入URL编码后的字符：', style='cyan')
    except KeyboardInterrupt:
        string = ''
    if not string:
        exit(0)
    translate = unquote_plus if plus else unquote
    result = translate(string, encoding=encoding)
    print('\n', result, sep='')


operator.add_command(encoder, 'enc')
operator.add_command(decoder, 'dec')

if __name__ == '__main__':
    operator()
