"""
Manage shebang of scripts which in same folder.
管理相同目录下所有Python脚本的shebang。

Usage: chint [-h|--help|/?]
"""

import sys
from pathlib import Path
from typing import Optional, Iterable, List

ego = Path(__file__).absolute()  # 当前文件
root = ego.parent  # 项目根目录


def get_sources() -> Iterable:
    """
    获取相同目录下除自身外的所有非符号链接的python源文件。
    """
    return (
        src for src in root.glob('*.py')
        if src != ego and src.is_file() and not src.is_symlink()
    )


def get_interpreter(src: Path) -> Optional[str]:
    """
    获取某个python脚本的shebang，没有则返回 None。
    """
    with src.open('r', encoding='UTF-8') as f:
        for line in f:
            return line.rstrip('\r\n') if line.startswith('#!') else None


def set_interpreter(src: Path, interpreter: str) -> str:
    """
    修改某个python脚本的shebang，若失败则返回字符信息，成功时返回空字符串。
    """
    with src.open('r+', encoding='UTF-8') as f:
        f.seek(0)
        if f.readline().startswith('#!'):
            f.seek(0)
            lines = f.readlines()
            lines[0] = '#!' + interpreter + '\n'
            f.seek(0)
            f.writelines(lines)
            f.truncate()
            return ''
        else:
            # TODO
            pass


def print_table(table: List[tuple], top=1, right=0, bottom=1, left=1):
    if not table:
        return
    widths = [
        max(len(table[row][col]) for row in range(len(table))) + 2
        for col in range(len(table[0]))
    ]
    print('\n' * top, end='')
    for row in table:
        line = ''.join(p[0].ljust(p[1]) for p in zip(row, widths))
        print(' ' * left + line + ' ' * right)
    print('\n' * bottom, end='')


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] in ('-h', '--help', '/?'):
        print(__doc__)
        exit(0)

    sheet = []
    for source in get_sources():
        itp = get_interpreter(source)
        itp = itp[2:] if isinstance(itp, str) else '\033[36m(未设置)\033[39m'
        sheet.append((source.name, itp))

    print_table(sheet)
    print(' 以上是基于', str(root))
    print(' (非递归)目录下所有脚本及对应的shebang。')
    print()
    print('输入新的shebang，或按 Ctrl-C 键终止：\n#!', end='')
    try:
        itp = input()
    except KeyboardInterrupt:
        itp = ''
    if not itp:
        exit(0)

    for source in get_sources():
        print('正在修改', source.name, '...', end=' ')
        result = set_interpreter(source, itp)
        print(('\x1b[31m%s\x1b[39m' % result) if result else '\x1b[32m成功\x1b[39m')
    print('完毕\n')
