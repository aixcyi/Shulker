<h1 align="center" style="padding-top: 32px">Shulker&nbsp;<sup><sup>Py 3.11</sup></sup></h1>

<div align="center">
    <i>来自深界七层的潜影盒，有终末嗟叹之诗刻于其上，藏着银狼那奇技淫巧般的指令</i>
</div>

一套（省略八百字）命令集。

## 特性

- 使用命令行接口定义与解析框架 [Click](https://click.palletsprojects.com/en/8.1.x/api/) ，面向对象设计命令行接口，妈妈再也不用担心我秃头
- 使用花里胡哨但非常好看的命令行富文本打印工具 [Rich](https://github.com/Textualize/rich) ，就一个字：巴适
- 从接口到配置全程使用 Python，一套功夫打包带走
- Python 最新版！兼容性？那啥玩意儿
- 本地的命令集，适合联动自己写的加密工具或者编码工具，或者直接基于此开发，肥肠氨醛
- 蒸馍？泥不扶？不扶就[撸](#定制)！

## 安装

> 需要 Python 3.11 或以上版本。

直接克隆仓库：

```shell
git clone https://github.com/aixcyi/Shulker.git "shulker"
```

或者

```shell
git clone https://gitee.com/aixcyi/shulker.git "shulker"
```

### Windows

创建虚拟环境并安装依赖包：

```shell
cd ./shulker
python -m venv ./venv
"./venv/Scripts/activate.bat"
pip install -r ./requirements.txt
```

离开虚拟环境后试着运行一下主命令：

```shell
deactivate
"./shulker.py" --help
```

如果出现 `ImportError` 这样的导入错误，那么需要修改注册表的两条文件关联：

```shell
"./venv/Scripts/activate.bat"
python ./shulker.py fixreg > restore.reg
```

- 若提示 py.exe 不存在，请尝试修复或重新安装 Python。
- 若两条都提示修改成功，则完毕。
- 若出现其它错误，请双击 `restore.reg` 文件，还原文件关联！！！！！！！！！！

最后，将仓库目录添加到环境变量 `PATH` 中，以便随时随地调用仓库里的命令。

### Linux

去到刚刚克隆的仓库中，直接安装依赖：（因为我在WSL中没有使用虚拟环境）

```shell
pip3 install -r ./requirements.txt
```

看一下python3装到哪里去了（如果用虚拟环境要看虚拟环境的python3），一般是 `#!/usr/bin/python3.11`

```shell
which python3
```

然后修改所有py文件的 shebang、添加执行权限、创建符号链接：

```shell
python3 ./shulker.py migrate
```

最后，在 `.bashrc` 里将仓库目录添加到PATH中：

```shell
PATH=你的仓库目录:$PATH
```

之后，你就可以在其它任何地方直接调用命令了。

### Mac

*没有环境。哪位好心的大佬愿意轻抬小手挥挥衣袖帮俺补上*

## 更新

直接更新仓库：

```shell
git fetch
git pull
```

如果网络比较差，可以：

```shell
git remote set-url origin https://gitee.com/aixcyi/shulker.git
git fetch
git pull
```

### Windows

如果解释器也是 `./venv/Scripts/python.exe` 的话那么就没有后续操作。

如果不是，那么需要使用 **你的解释器** 运行迁移来修改所有源文件的 shebang ：

```shell
python ./shulker.py migrate
```

### Linux／Mac

修改所有源文件的 shebang（一般是 `#!/usr/bin/python3.11`，具体看你装到哪里去了）：

```shell
python3 ./shulker.py shebang --set
```

然后给所有 Python 源码添加执行权限：

```shell
chmod +x ./*.py
```

## 用法

> 目前的命令都是使用 `-h` 和 `--help` 风格，没有用 `/?` 风格，因为 ~~整体迁移比较麻烦~~ 懒。

主命令是 `shulker` ，你可以通过它来浏览所有命令，包括弃用的：

```shell
shulker list
```

查看隐藏的命令：

```shell
shulker list -a
```

## 配置

> 配置指的是命令读取的预先设置的东西，以一个 Python 包的形式存放在项目根目录下，其名为 "configs" ，鲲之大，一锅装不下。

### FILES

文件记录。被命令 `edit` 用于打开文件。

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

命令配置。被命令 `yudo` 用于运行程序／项目／脚本等。

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
        'run': 'runserver 127.0.0.1:7777',
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
yudo abc.d run  # python -X utf8 ./manage.py runserver 127.0.0.1:7777
yudo abc.d runserver 0.0.0.0:80  # python -X utf8 ./manage.py runserver 0.0.0.0:80
yudo abc.d --help  # python -X utf8 ./manage.py --help
```

### STATUSES

环境信息。被命令 `shulker status` 用来列出相关环境信息，但其实……你完全可以把它当成一个备忘录。

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

自定义字符集。被命令 `mkstr` 按照不同字符集生成随机字符串，使用命令 `char set` 可以浏览这里配置的所有字符集。

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

@click.command(__name__, short_help='我的命令')
@click.argument('yourname')
@click.option('-u', '--upper', is_flag=True, help='输出全大写的句子。')
def invoker(yourname: str, upper: bool):
    """
    这是我的第一个命令。
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

  这是我的第一个命令。

Options:
  -u, --upper  输出全大写的句子。
  --help       Show this message and exit.
```

## 指引

- [Click 8.1.x API 英文文档](https://click.palletsprojects.com/en/8.1.x/api/)
- [Rich 最新版 API 英文文档](https://rich.readthedocs.io/en/latest/)
- [Rich 中文 README - GitHub](https://github.com/textualize/rich/blob/master/README.cn.md)，主要用来看效果

## 附录

### Ubuntu

#### 安装 python3

确定本机有没有安装 python3.11 ：

```shell
which python3.11
which python3
```

没有的话，安装之前搜索一下看看有没有 3.11：

```shell
apt search python3 | grep ^python3.11
```

有就直接安装好了。  
没有的话可以通过 PPA 来安装 Python（安装之后应该是 `/usr/bin/python3.11`）：

```shell
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
```

然后在当前用户 Home 目录的 `.bashrc` 里设置别名：

- 如果原本就有 `python3` 那么尽量避免覆盖，因为 Ubuntu 很多库都依赖 python

```sh
alias py3='python3.11'
```

- 否则可以设置比较常用的别名

```shell
alias python3='python3.11'
```

别忘了

```shell
source ~/.bashrc
```

#### 安装 pip3

确定本机有没有安装 pip3，有的话看一下版本是不是对应了 Python 3.11

```shell
which pip3
pip3 -V
```

如果没有或者不是，需要另外安装 pip3 并在 `.bashrc` 里设置别名：
（从这里往后都假设你设置的别名是 <font color="red"><b>python3</b></font> 和 <font color="red"><b>pip3</b></font> ）

```shell
wget https://bootstrap.pypa.io/pip/get-pip.py
python3 ./get-pip.py
```

（由于我用的是WSL，不太需要虚拟环境，所以没有攻略）
