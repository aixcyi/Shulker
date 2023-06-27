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
- 屏幕前的你开发的所有特性

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

## 配置

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

## 配置 Plus Pro Max

你可以将仓库目录添加到环境变量 `PATH` 中，以便让你随时随地调用脚本。

## 用法

> 目前的指令都是使用 `-h` 和 `--help` ，没有用 `/?` （但很容易适配）。

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

## 定制

你需要在项目根目录下创建 Python 文件，因为在全局环境中不容易访问子目录。

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

