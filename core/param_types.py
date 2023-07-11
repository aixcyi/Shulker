import re
from typing import Pattern

import click


class Regex(click.ParamType):
    name = 'regex'

    def convert(self,
                value: str,
                param: click.Option,
                ctx: click.Context) -> Pattern[str]:
        try:
            return re.compile(value)
        except re.error:
            self.fail(f'无法解析正则表达式 {value}', param, ctx)
