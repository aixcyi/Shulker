import json
import re
from pathlib import Path

import click
from rich import box
from rich.table import Table

from fox import FoxLoop

root = Path(__file__).absolute().parent.parent
datapack = root / 'dataset' / 'codes'
encoding = 'GB18030'


@click.group(__name__, short_help='行政区划代码相关')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def manager():
    """
    行政区划代码相关功能。
    """


@manager.command('list', short_help='列出所有已载入的数据')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
@click.pass_obj
def lister(shell: FoxLoop):
    if type(shell.contexts['ADC']) is not dict:
        shell.contexts['ADC'] = {}
    if not datapack.is_dir():
        shell.warning(f'数据目录不存在：{datapack!s}')
        return

    table = Table('文件', '年份', '标题', '数据量', box=box.SIMPLE_HEAD)
    for k, v in shell.contexts['ADC'].items():
        table.add_row(
            f'{k}.json',
            str(v['year']),
            v['title'],
            str(len(v['data'])),
        )
    for fp in datapack.glob('*.json'):
        if fp.stem in shell.contexts['ADC']:
            continue
        table.add_row(
            fp.name,
            '(未载入)',
            '(未载入)',
            '(未载入)',
        )
    shell.output(table)


@manager.command('load', short_help='载入某一份数据集')
@click.argument('filename')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
@click.pass_obj
def loader(shell: FoxLoop, filename: str):
    if type(shell.contexts['ADC']) is not dict:
        shell.contexts['ADC'] = {}
    if not datapack.is_dir():
        shell.warning(f'数据目录不存在：{datapack!s}')
        return

    is_reload = filename in shell.contexts['ADC']

    filename += '.json'
    try:
        target = next(datapack.glob(filename))
    except StopIteration:
        shell.warning(f'文件 {filename} 不存在。')
        return

    with shell.stderr.status('正在载入...', spinner='bouncingBar'):
        try:
            data = json.load(target.open('r', encoding=encoding))
        except Exception as e:
            shell.stderr.print_exception(e)
        shell.contexts['ADC'][target.stem] = data
        shell.info(f'已重新载入 {filename}' if is_reload else f'{filename} 载入完毕。')


@manager.command('search', short_help='搜索编码或地名')
@click.argument('text')
@click.option('-r', '--regex', is_flag=True, help='启用正则表达式。')
@click.option('-n', '--filename', help='将搜索限定在某一份数据集中。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
@click.pass_obj
def searcher(shell: FoxLoop, text: str, regex: bool, filename: str | None):
    """
    当 FILENAME 是纯ASCII时搜索编码，否则搜索地名。
    """
    if type(shell.contexts['ADC']) is not dict:
        shell.contexts['ADC'] = {}
    if not datapack.is_dir():
        shell.warning(f'数据目录不存在：{datapack!s}')
        return

    just_name = any(ord(c) > 128 for c in text)

    if regex:
        try:
            text = re.compile(text)
        except ValueError:
            shell.warning('正则表达式不正确。')
            return

    if filename is None:
        files = tuple(shell.contexts['ADC'].keys())
        if not files:
            shell.warning('未载入任何数据。')
            return
    else:
        files = (filename,)
        if filename not in shell.contexts['ADC']:
            shell.warning(f'{filename}.json 未载入。')
            return

    for f in files:
        for k, v in shell.contexts['ADC'][f]['data'].items():
            if just_name:
                # 只搜索地名
                result = re.match(text, v) if regex else (text in v)
            else:
                # 只搜索编码
                result = re.match(text, k) if regex else (text in k)

            if result:
                shell.output(f'{f}.json | {k}\t{v}')
