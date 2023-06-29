<h1 align="center" style="padding-top: 32px">Shulker&nbsp;<sup><sup>Py 3.11</sup></sup></h1>

<div align="center">
    <i>来自深界七层的潜影盒，有终末嗟叹之诗刻于其上，藏着银狼那奇技淫巧般的指令</i>
</div>

## 特性

- 使用命令行接口定义与解析框架 [Click](https://click.palletsprojects.com/en/8.1.x/api/) ，面向对象设计命令行接口，妈妈再也不用担心我秃头
- 使用花里胡哨但非常好看的命令行富文本打印工具 [Rich](https://github.com/Textualize/rich) ，就一个字：巴适
- 从接口到配置全程使用 Python，一套功夫打包带走
- Python 最新版！兼容性？那啥玩意儿
- 本地的命令集，适合联动自己写的加密工具或者编码工具，或者直接基于此开发，肥肠氨醛
- 蒸馍？泥不扶？不扶就[撸](#定制)！

## 安装

> 需要安装 Python 3.11 版本，没有以上。如果有，那一定是README没有更新。

首先，克隆仓库：

```shell
git clone git@github.com:aixcyi/Shulker.git "shulker"
```

或者使用 HTTPS 克隆：

```shell
git clone https://github.com/aixcyi/Shulker.git "shulker"
```

然后创建虚拟环境：

```shell
cd ./shulker
python -m venv ./venv
```

接着，切换到虚拟环境中：

```shell
cd ./venv/Scripts
activate
```

最后安装依赖：

```shell
cd ../../
pip install -r ./requirements.txt
```

## 设置

> 主要是让你可以在命令行中直接调用 Python 脚本。

### Windows

离开虚拟环境后，直接运行：

```shell
"./shulker.py" --help
```

如果没有出现错误，则配置结束。  
如果出现 `ImportError` 这样的导入错误，需要修改文件关联：

（为了防止误操作，最好先看看原来的关联）

```shell
reg query HKCR\.py /ve
reg query HKCR\py_auto_file\shell\open\command /ve
```

（然后再）

```shell
reg add HKCR\.py /ve /d "py_auto_file"
reg add HKCR\py_auto_file\shell\open\command /ve /d "\"C:\Windows\py.exe\" \"%1\" %*"
```

没有 `C:\Windows\py.exe` 的话，那应该是  
`C:\Users\<你的用户名>\AppData\Local\Programs\Python\Launcher\py.exe`

如果这两个文件都没有，请重新安装 Python，并勾选 **py.exe** 那个选项。

### Linux

*TODO：没有环境。等待补充。*

### Mac

*TODO：没有环境。等待补充。*

## 设置 Plus Pro Max

墙裂建议！！将仓库目录添加到环境变量 `PATH` 中，以便随时随地调用脚本。

## 用法

> 目前的指令都是使用 `-h` 和 `--help` 风格，没有用 `/?` 风格，因为 ~~整体迁移比较麻烦~~ 懒。

主命令是下面这个：

```shell
shulker --help
```

它可以列出当前目录下所有指令（非递归），包括不在版本管理里的自定义的

```shell
shulker list
```

如果虚拟环境迁移了，可以先修改 `shulker.py` 的 shebang，然后

列出所有指令的 shebang：

```shell
shulker shebang
```

修改所有已经有 shebang 的源文件的 shebang：

```shell
shulker shebang -s
```

## 配置

> 配置指的是指令读取的预先设置的东西，以一个 Python 包的形式存放在项目根目录下，其名为 "configs" ，鲲之大，一锅装不下。

### FILES

文件记录。被指令 `edit` 用于打开文件。

##### 烹饪指南

```python
from typing import NamedTuple

# NamedTuple的子类不能继承，所以需要重新定义
# 可以定义多个，以提供不同的默认值。但结构必须与 FileShortcut 一致
class VSCodeShortcut(NamedTuple):
    name: str
    path: str
    editor: str = 'code'  # 默认值，应当是可以直接在命令行执行的字符串

FILES = [
    VSCodeShortcut('shulker', r'C:\Users\MyName\Desktop\shulker\configs\__init__.py'),
    VSCodeShortcut('frpc', '/myusername/frp/frpc.ini'),
]
```

##### 食用指南

```python
from configs import FILES
from core.configurators import FileShortcut

FILES: list[FileShortcut]
```

### COMMANDS

命令配置。被指令 `yudo` 用于运行程序／项目／脚本等。

##### 烹饪指南

```python
from core.configurators import Command

class CompanyProject(Command):
    name = 'abc.d'
    main = 'python -X utf8 ./manage.py'
    note = '公司项目'
    before = [
        'title xxx后台管理系统',
        r'cd C:\Users\MyName\companyABC\abc-xxx-server',
        'call ./venv/Scripts/activate.bat',
    ]
    actions = {
        'mkms': 'makemigrations',
        'migrate': 'migrate',
        'run': 'runserver 127.0.0.1:6666',
    }

COMMANDS = [
    CompanyProject,
]
```

##### 食用指南

```python
from configs import COMMANDS
from core.configurators import Command

COMMANDS: list[type[Command]]
```

```shell
yudo abc.d mkms  # python -X utf8 ./manage.py makemigrations
yudo abc.d migrate  # python -X utf8 ./manage.py migrate
yudo abc.d run  # python -X utf8 ./manage.py runserver 127.0.0.1:6666
yudo abc.d runserver 0.0.0.0:6666  # python -X utf8 ./manage.py runserver 0.0.0.0:6666
yudo abc.d --help  # python -X utf8 ./manage.py --help
```

### STATUSES

环境信息。被指令 `shulker status` 用来列出相关环境信息，但其实……你完全可以把它当成一个备忘录。

##### 烹饪指南

```python
# 不要问我为什么不定义成一个dict，谁也不知道以后会不会有更多列
STATUSES = [
    (),  #  空一行
    ('标准编码', 'https://docs.python.org/zh-cn/3/library/codecs.html#standard-encodings'),
]
```

##### 食用指南

```python
from configs import STATUSES
from rich.console import ConsoleRenderable, RichCast

STATUSES: list[tuple | tuple[str, None | ConsoleRenderable | RichCast | str]]
```

### charsets

自定义字符集。被指令 `mkstr` 按照不同字符集生成随机字符串，使用指令 `char set` 可以浏览这里配置的所有字符集。

##### 烹饪指南

```python
# 所有符号都会被当作字符集，所以如果实在需要导入其它符号，记得完事之后用 del 删除
# 因为 mkstr 的很多选项都需要用到下面的字符集，所以直接搬走就好了

digit = '0123456789'
upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lower = 'abcdefghijklmnopqrstuvwxyz'
alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
digit_safe = '23456789'
upper_safe = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
lower_safe = 'abcdefghijklmnpqrstuvwxyz'
symbol = ''.join(c for c in map(chr, range(33, 127)) if not c.isalpha() and not c.isdigit())
symbol_normal = r"`-=[]\;',./"
symbol_shift = r'~!@#$%^&*()_+{}|:"<>?'
base16 = '0123456789ABCDEF'
base64 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/'
base36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXY'
base62 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
# print(''.join(sorted(symbol)))
# print(''.join(sorted(symbol_normal + symbol_shift)))
assert sorted(symbol) == sorted(symbol_normal + symbol_shift)
# 空一行方便你选择文本。爱护大小熊猫，坚决抵制夺笋

```

##### 食用指南

```python
from configs import charsets
import typing

charsets: type(typing)  # 意思就是说 charsets 是一个 Python 包
```

## 定制

需要在项目根目录下创建 Python 文件，因为在全局环境中不容易访问子目录。

模板大致如下：

```python
#!./venv/Scripts/python.exe
# -*- coding: UTF-8 -*-
import sys
import click

@click.command(__name__, short_help='我的指令')
@click.argument('yourname')
@click.option('-u', '--upper', is_flag=True, help='输出全大写的句子。')
def invoker(yourname: str, upper: bool):
    """
    这是我的第一个指令。
    """
    message = f'Hello, {yourname}.'
    if upper:
        message = message.upper()

    print(message)


if __name__ == '__main__':
    invoker(sys.argv[1:])
```

保存到名为 `meow.py` 的文件中之后调用（非Windows用户记得加一下执行权限）

```shell
meow --help
```

它会输出

```
Usage: meow.py [OPTIONS] YOURNAME

  这是我的第一个指令。

Options:
  -u, --upper  输出全大写的句子。
  --help       Show this message and exit.
```

## 指引

- [Click 8.1.x API 英文文档](https://click.palletsprojects.com/en/8.1.x/api/)
- [Rich 最新版 API 英文文档](https://rich.readthedocs.io/en/latest/)
- [Rich 中文 README - GitHub](https://github.com/textualize/rich/blob/master/README.cn.md)，主要用来看效果

