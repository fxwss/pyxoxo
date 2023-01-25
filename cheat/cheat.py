import os
import time
from dataclasses import dataclass

from cheat.module import CheatModule
from input.input import Keyboard
from offsets import Offsets
from offsets import get as get_offsets
from process import ensure_complex, find_process_by_name


@dataclass(eq=True, frozen=True)
class Cheat:
    executable: str
    modules: list[CheatModule]
    offsets: Offsets = get_offsets()

    def get_module(self, id: str):
        for module in self.modules:
            if module.name == id:
                return

    def start_modules(self):
        process = ensure_complex(find_process_by_name(self.executable))

        for module in self.modules:
            module.run(process, self.offsets)
            print(module)

        return self

    def wait(self):
        one_millisecond = 1 / 1000

        try:
            while True:
                Keyboard.listen()
                time.sleep(one_millisecond)
        except KeyboardInterrupt:
            ...

        return self
