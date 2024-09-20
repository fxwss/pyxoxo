from dataclasses import dataclass
from enum import Enum
from threading import Thread
import time
from typing import Callable, TypeVar

from process import offsets, ComplexProcessHandle, find_module_by_name, has_active_window, read_memory


ModuleUpdateFn = Callable[[ComplexProcessHandle], None]


class ModuleStatus(Enum):
    ACTIVE = 1
    INACTIVE = 2
    PAUSED = 3
    ERROR = 4


@dataclass(eq=True)
class CheatModule:
    name: str

    update: ModuleUpdateFn

    interval: float = 1 / 1000
    status: ModuleStatus = ModuleStatus.INACTIVE

    def run(self, process: ComplexProcessHandle):

        if self.status == ModuleStatus.ERROR:
            raise Exception('Cannot start errored module')

        self.status = ModuleStatus.ACTIVE

        def loop():
            while self.status != ModuleStatus.INACTIVE:
                time.sleep(self.interval)


                if self.status == ModuleStatus.PAUSED or not has_active_window(process):
                    continue

                self.update(process)

        def wrapper():
            nonlocal self

            try:
                loop()
            except Exception as e:
                self.status = ModuleStatus.ERROR
                raise e

        thread = Thread(target=wrapper, daemon=True)
        thread.start()

        return self

    def stop(self):
        self.status = ModuleStatus.INACTIVE
        return self

    def resume(self):
        if self.status == ModuleStatus.ERROR:
            raise Exception('Cannot resume errored module')

        if self.status == ModuleStatus.INACTIVE:
            raise Exception('Cannot resume inactive module')

        self.status = ModuleStatus.ACTIVE

        return self

    def pause(self):
        if self.status == ModuleStatus.ERROR:
            raise Exception('Cannot pause errored module')

        if self.status == ModuleStatus.INACTIVE:
            raise Exception('Cannot pause inactive module')

        self.status = ModuleStatus.PAUSED

        return self
