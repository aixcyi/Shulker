from collections import defaultdict
from typing import Any, Callable, NamedTuple, NoReturn

from rich.console import Console
from rich.table import Table


class CommandInfo(NamedTuple):
    func: Callable
    hidden: bool
    deprecated: bool
    description: str


class Shell:
    prompt: str = '(shell)> '
    intro: str = ''
    cache: defaultdict[str, Any] = defaultdict(lambda: None)
    commands: dict[str, CommandInfo] = {}
    exitcode: int | None = None
    stdin = None
    stdout = None
    stderr = None

    def __init__(self, stdin=None, stdout=None, stderr=None):
        """
        一个简单的命令行解释器，用于通过面向对象的方式编写指令。

        这个类的实现与标准库的 `Cmd <https://docs.python.org/zh-cn/3/library/cmd.html#cmd.Cmd>`_ 相仿，
        但结合了 `rich <https://rich.readthedocs.io/en/latest/>`_ 框架，
        并为使用 `click <https://click.palletsprojects.com/en/8.1.x/>`_ 通过面向对象方式编写的指令作了兼容措施。

        分为两个大阶段：

        - 载入指令 ``reload()`` ，仅在类对象初始化时调用一次，手动调用以实现动态加载。
            - 准备 ``preload()``
            - 载入 ``load()``
            - 收尾 ``postload()``
        - 解析和运行 ``run()`` ，手动调用来进入主循环。
            - 开场 ``preloop()``
            - 循环 ``loop()``
            - 落幕 ``postloop()``

        :param stdin: 标准输入。该参数将会覆盖类的 stdin 值，若都为空则默认为一个 Console() 对象。
        :param stdout: 标准输出。该参数将会覆盖类的 stdout 值，若都为空则使用 stdin 。
        :param stderr: 标准错误。该参数将会覆盖类的 stderr 值，若都为空则默认为一个 Console(stderr=True) 对象。
        """
        self.stdin = stdin or self.stdin or Console()
        self.stdout = stdout or self.stdout or self.stdin
        self.stderr = stderr or self.stderr or Console(stderr=True)
        self.line: str = ''
        self.reload()

    def input(self, *args, **kwargs) -> str:
        """
        调用 stdin 的 input() 请求输入，所有参数都将原样传递。所有方法都通过此方法请求输入。
        """
        return self.stdin.input(*args, **kwargs)

    def output(self, *args, **kwargs) -> NoReturn:
        """
        调用 stdin 的 print() 进行输出，所有参数都将原样传递。所有方法都通过此方法进行输出。
        """
        self.stdout.print(*args, **kwargs)

    def warning(self, *args, **kwargs) -> NoReturn:
        """
        调用 stderr 的 print() 输出警告信息，所有参数都将原样传递。所有方法都通过此方法输出警告信息。
        """
        self.stderr.print(*args, **kwargs)

    def parse(self) -> tuple[str, tuple[str, ...]]:
        if not self.line:
            return '', ()
        args = self.line.strip().split(' ')

        def refix():
            buffer = ''
            for arg in args:
                if buffer:
                    buffer += arg
                    if arg.endswith('"'):
                        yield buffer
                        buffer = ''
                else:
                    if arg.startswith('"'):
                        buffer += arg
                    else:
                        yield arg
            else:
                if buffer:
                    yield buffer

        cmd, *args = refix()  # self.line 必定有字符，所以生成器至少有一个返回值
        return cmd, args

    def address(self, command: str) -> Callable[..., Any] | None:
        try:
            return getattr(self, 'do_' + command)
        except AttributeError:
            pass
        try:
            return self.commands[command][0]
        except KeyError:
            pass
        return None

    def preload(self):
        self.commands = {}

    def postload(self):
        self.commands = {k: self.commands[k] for k in sorted(self.commands.keys())}

    def load(self):
        for name in dir(type(self)):
            if not name.startswith('do_'):
                continue
            func = getattr(self, name)
            self.commands[name[3:]] = CommandInfo(
                func=func,
                hidden=False,
                deprecated=False,
                description=func.__doc__.strip(' \r\n'),
            )
        self.commands['?'] = self.commands['help']

    def reload(self):
        self.preload()
        self.load()
        self.postload()

    def invoke(self, cmd: Callable, argv: tuple) -> NoReturn:
        cmd(*argv)

    def dispatch(self):
        cmd, *argv = self.parse()
        func = self.address(cmd)
        try:
            if callable(func):
                self.invoke(func, argv)
            else:
                self.default()
        except self.ExitShell as e:
            self.exitcode = e.exit_code

    def preloop(self) -> NoReturn:
        self.output(self.intro)

    def postloop(self) -> NoReturn:
        exit(self.exitcode)

    def loop(self):
        try:
            while self.exitcode is None:
                self.output(self.prompt, end='')

                try:
                    self.line = self.input()
                except (KeyboardInterrupt, EOFError):
                    self.exitcode = 0
                    self.warning('')
                    continue

                if self.line is None:
                    continue
                self.line = self.line.rstrip('\r\n')
                if not self.line:
                    continue
                self.dispatch()
        finally:
            pass

    def run(self):
        self.preloop()
        self.loop()
        self.postloop()

    class ExitShell(RuntimeError):
        __slots__ = ("exit_code",)

        def __init__(self, code: int = 0) -> None:
            self.exit_code = code

    def default(self) -> NoReturn:
        self.output(f'找不到命令 {self.line}\n')

    def do_exit(self, *argv, **kwargs) -> NoReturn:
        """
        退出命令行
        """
        raise self.ExitShell(0)

    def do_help(self, *argv, **kwargs) -> NoReturn:
        """
        列出所有指令及帮助信息
        """
        table = Table(box=None, show_footer=True)
        for name, cmd in self.commands.items():
            table.add_row(name, cmd.description)

        self.output(table)
