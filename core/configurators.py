from typing import NamedTuple


class Command:
    name: str
    main: str
    note: str
    before: list[str]
    actions: dict[str, str]

    def __init__(self, *argv, delimiter=' && '):
        if len(argv) == 1 and argv[0] in self.actions:
            script = f'{self.main} {self.actions[argv[0]]}'
        else:
            script = ' '.join([self.main, *argv])

        self.scripts = [*self.before, script]
        self.script = delimiter.join([*self.before, script])


class FileShortcut(NamedTuple):
    name: str
    path: str
    editor: str
