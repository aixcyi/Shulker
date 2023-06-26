#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
from base64 import b64encode, b64decode

import click

from core.features import HydroConsole


@click.group(__name__, short_help='Base64编解码')
@click.help_option('-h', '--help', help='列出这份帮助信息。')
def converter():
    """
    Base64 是一种基于64个可打印字符的二进制数据表示方法。
    每 6 比特对应一个 Base64 字符，即 3 个字节折合 4 个字符；
    编码结果长度不是4的非负整数倍时使用 "=" 填充。

    默认编码表为：
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    """


@converter.command('encode', short_help='对HEX进行base64编码')
@click.option('-a', '--alter', help='使用其它字符代替 "+/" ，比如 "-_" 。')
@click.option('-p', '--skip-padding', is_flag=True, help='跳过长度填充过程。')
def encoder(alter, skip_padding):
    """
    对HEX进行base64编码。
    """
    console = HydroConsole()
    if alter and len(alter) != 2:
        console.warning('--alter 参数提供的字符必须且只能有两个。')
        exit(0)
    try:
        string = console.ask('输入HEX：', style='cyan')
    except KeyboardInterrupt:
        exit(0)
    try:
        data = bytes.fromhex(string)
        data = b64encode(data, altchars=alter) if alter else b64encode(data)
    except ValueError:
        console.warning('请输入纯HEX')
    else:
        print(
            data.decode('ASCII').strip('=')
            if skip_padding else
            data.decode('ASCII')
        )


@converter.command('decode', short_help='将base64解码为HEX')
@click.option('-a', '--alter', help='使用其它字符代替 "+/" ，比如 "-_" 。')
def decoder(alter):
    """
    base64解码为HEX。
    """
    console = HydroConsole()
    if alter and len(alter) != 2:
        console.warning('--alter 参数提供的字符必须且只能有两个。')
        exit(0)
    try:
        string = console.ask('输入base64：', style='cyan')
    except KeyboardInterrupt:
        exit(0)
    else:
        string += ('', '===', '==', '=')[len(string) % 4]
    try:
        data = b64decode(string, altchars=alter) if alter else b64decode(string)
    except ValueError:
        console.warning('请输入正确的base64字符串')
        exit(-1)
    else:
        print(data.hex())


converter.add_command(encoder, 'enc')
converter.add_command(decoder, 'dec')

if __name__ == '__main__':
    import sys

    converter(sys.argv[1:])
