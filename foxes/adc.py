from __future__ import annotations

import json
import re
from pathlib import Path
from typing import NamedTuple, Pattern

import click
from rich import box
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from core.param_types import Regex
from fox import FoxLoop

root = Path(__file__).absolute().parent.parent
datapack = root / 'dataset' / 'codes'
encoding = 'GB18030'


def get_files(shell: FoxLoop, filename: str | None) -> tuple[str]:
    """
    根据文件名选择数据集文件。

    应确保 ``shell.contexts['ADC']`` 的值一定是 ``dict`` 。

    :param shell: Shell命令行，用于输出错误提示。
    :param filename: 文件名。
    :return: 所有已载入的文件名。
    :raise RuntimeError:
    """
    if filename is None:
        if shell.contexts['ADC']:
            return tuple(shell.contexts['ADC'].keys())
        shell.warning('未载入任何数据。')
        raise
    else:
        if filename in shell.contexts['ADC']:
            return (filename,)
        shell.warning(f'{filename}.json 未载入或不存在。')
        raise


class DivisionCode(NamedTuple):
    """
    统计用行政区划代码。
    """
    province: str
    prefecture: str = '00'
    county: str = '00'
    township: str = '000'
    village: str = '000'

    def __str__(self):
        return ''.join(self)

    @classmethod
    def fromcode(cls, code: str) -> DivisionCode:
        adc = code.ljust(12, '0')
        return cls(adc[:2], adc[2:4], adc[4:6], adc[6:9], adc[9:12])

    def code(self, level: int) -> str:
        return ''.join(self[:level]).ljust(12, '0')


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
    shell.contexts.setdefault('ADC', {})
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
    shell.contexts.setdefault('ADC', {})
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
@click.option('-c', '--code', multiple=True, help='搜索区划代码。')
@click.option('-C', '--code-reg', multiple=True, type=Regex(), help='使用正则表达式搜索区划代码。')
@click.option('-n', '--name', multiple=True, help='搜索区划名称。')
@click.option('-N', '--name-reg', multiple=True, type=Regex(), help='使用正则表达式搜索区划名称。')
@click.option('-A/-a', '--all/--any', 'op', default=False, help='串联还是并联所有条件。默认是 -a 并联。')
@click.option('-f', '--filename', help='将搜索限定在某一份数据集中。')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
@click.pass_obj
def searcher(shell: FoxLoop,
             code: tuple[str],
             name: tuple[str],
             code_reg: tuple[Pattern[str]],
             name_reg: tuple[Pattern[str]],
             filename: str | None,
             op: bool):
    """
    当 FILENAME 是纯ASCII时搜索编码，否则搜索地名。
    """
    shell.contexts.setdefault('ADC', {})
    if not any([*code, *code_reg, *name, *name_reg]):
        shell.warning(f'没有搜索条件。')
        return
    try:
        files = get_files(shell, filename)
    except RuntimeError:
        return

    ope = all if op else any

    with shell.stdout.status('正在搜索...', spinner='bouncingBar'):
        for f in files:
            for k, v in shell.contexts['ADC'][f]['data'].items():
                hits = [
                    *[c in k for c in code],
                    *[n in v for n in name],
                    *[re.match(rc, k) for rc in code_reg],
                    *[re.match(rn, v) for rn in name_reg],
                ]
                if ope(hits):
                    shell.output(f'{f}.json | {k}\t{v}')


@manager.command('parse', short_help='解析一个代码')
@click.argument('code')
@click.option('-f', '--filename', help='将搜索限定在某一份数据集中。')
@click.pass_obj
def parser(shell: FoxLoop, code: str, filename: str | None):
    """
    解析一个行政区划代码，并列出每一个层级的信息。
    """
    shell.contexts.setdefault('ADC', {})
    if not code.isdigit():
        shell.warning('代码只应包含纯数字。')
        return
    try:
        files = get_files(shell, filename)
    except RuntimeError:
        return

    adc = DivisionCode.fromcode(code)
    tree = Tree('│')
    parts = [
        (c := adc.code(1), c[:0], adc[0], c[2:]),
        (c := adc.code(2), c[:2], adc[1], c[4:]),
        (c := adc.code(3), c[:4], adc[2], c[6:]),
        (c := adc.code(4), c[:6], adc[3], c[9:]),
        (c := adc.code(5), c[:9], adc[4], c[12:]),
    ]
    items = [
        (
            area,
            Text().join([
                Text(head, 'dim'),
                Text(mid, 'magenta3'),
                Text(tail, 'dim'),
            ]),
        )
        for area, head, mid, tail in parts
    ]
    for area, title in items:
        third = tree.add(title)

        for i in range(len(files) - 1):
            file = files[i]
            name = shell.contexts['ADC'][file]['data'].get(area, '')
            path = f'（{file}.json）'
            line = Text().join([Text(name), Text(path, 'dim')])
            third.add(line)
        else:
            file = files[-1]  # 从上文保证 files 有至少一个元素
            name = shell.contexts['ADC'][file]['data'].get(area, '')
            path = f'（{file}.json）\n'
            line = Text().join([Text(name), Text(path, 'dim')])
            third.add(line)

    shell.output(tree)
