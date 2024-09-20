from dataclasses import dataclass

from process import read_memory
from process.interfaces import ComplexProcessHandle


@dataclass(eq=True, frozen=True)
class BaseEntity:
    id: int
    address: int
    process: ComplexProcessHandle

    def get(self, offset: int, format: str = 'i'):
        return read_memory(self.process, self.address + offset, format)

    def valid(self):
        return self.address != 0
