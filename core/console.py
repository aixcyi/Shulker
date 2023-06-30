from typing import Optional, TextIO, TypeVar, Callable, Any

from rich.console import Console
from rich.text import TextType

T = TypeVar('T')


class HydroConsole(Console):

    def warning(self, *objects, **kwargs):
        self.print(*objects, style='yellow', **kwargs)

    def ask(
            self,
            prompt: TextType = "",
            *,
            style: str = '',
            newline: bool = False,
            mapper: type[T] | Callable[[Any], T] = str,
            default: T = '',
            markup: bool = True,
            emoji: bool = True,
            password: bool = False,
            stream: Optional[TextIO] = None,
    ) -> T:
        if any([style, newline]):
            self.print(
                prompt,
                style=style,
                end='\n' if newline else '',
            )
            value = self.input(
                markup=markup,
                emoji=emoji,
                password=password,
                stream=stream,
            )
        else:
            value = self.input(
                prompt,
                markup=markup,
                emoji=emoji,
                password=password,
                stream=stream,
            )
        try:
            return mapper(value) if callable(mapper) else value
        except:
            return default
