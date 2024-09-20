import time

from dataclasses import dataclass

import ui

from cheat.module import CheatModule
from process import ensure_complex, find_process_by_name
from logger import logger
from taks import TaskPool
from utils import create_thread

@dataclass(eq=True, frozen=True)
class Cheat:
    executable: str
    modules: list[CheatModule]

    options = {
        'should_render_gui': False,
    }

    def get_module(self, id: str):
        for module in self.modules:
            if module.name == id:
                return

    def start_modules(self):
        process = ensure_complex(find_process_by_name(self.executable))

        for module in self.modules:
            module.run(process)
            logger.info(module)

        return self

    def render_gui(self):
        create_thread(ui.main)

        return self

    def wait(self):
        one_millisecond = 1 / 1000

        try:
            while True:
                time.sleep(one_millisecond)
                TaskPool.run()

        except KeyboardInterrupt:
            ...

        return self
