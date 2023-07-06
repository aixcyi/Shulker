#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import os
from pathlib import PureWindowsPath, PurePosixPath

import click

from core.console import HydroConsole


@click.command(__name__, short_help='WSL挂载路径转换')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def converter():
    r"""
    提供 Windows 路径与 WSL 挂载路径的互相转换。

    例如把 "C:\Users\mine\Pictures\camera\20230623-102400.jpg"
    转换为 "/mnt/c/Users/mine/Pictures/camera/20230623-102400.jpg"
    """
    console = HydroConsole(stderr=True)
    try:
        path = console.ask('输入绝对路径：', style='cyan')
    except KeyboardInterrupt:
        exit(0)

    path = path or os.getcwd()

    if '\\' in path:
        path = PureWindowsPath(path)
        parts = ['/mnt', *list(map(lambda p: p.name, path.parents[::-1])), path.name]
        parts[1] = path.drive[:-1].lower()  # 去除Windows的盘符尾缀的冒号，并转换为小写
        result = PurePosixPath(*parts)
        print(str(result))
    elif '/' in path:
        path = PurePosixPath(path)
        parts = [*list(map(lambda p: p.name, path.parents[::-1])), path.name]
        if str(parts[1]) != 'mnt':
            console.warning('不是 Windows 在 WSL 中的挂载路径。')
            exit(-1)
        parts = parts[2:]
        parts[0] = f'{parts[0]}:\\'.upper()
        result = PureWindowsPath(*parts)
        print(str(result))


if __name__ == '__main__':
    converter()
