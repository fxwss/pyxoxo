import ctypes
import struct

from dataclasses import dataclass
from typing import Any

import process


@dataclass(eq=True, frozen=True)
class ProcessModule:
    name: str
    base_address: int
    size: int

    def __add__(self, other):
        if isinstance(other, int):
            return self.base_address + other

        raise TypeError

    def __int__(self):
        return self.base_address


@dataclass(eq=True, frozen=True)
class SimpleProcessHandle:
    name: str
    pid: int
    handle: ctypes.c_void_p


@dataclass(eq=True, frozen=True)
class ComplexProcessHandle(SimpleProcessHandle):
    modules: set[ProcessModule]


@dataclass(eq=True, frozen=True)
class MemoryPiece:
    process: SimpleProcessHandle
    address: int
    data: bytes
    format: str

    # uses struct to parse bytes to a data type
    def into(self, data_type: str | None = None) -> Any:
        if data_type is None:
            data_type = self.format

        unpacked = struct.unpack(data_type, self.data)

        if len(unpacked) == 1:
            return unpacked[0]

        return unpacked
    
    def unwrap(self):
        return self.into()

    def read(self, format = 'i', offset = 0):
        return process.read_memory(self.process, self.address + offset, format)

    def write(self, data: bytes | int | float, offset = 0):
        return process.write_memory(self.process, self.address + offset, data)

    def __add__(self, other):
        if isinstance(other, int):
            return MemoryPiece(self.process, self.address + other, self.data, self.format)

        raise TypeError

@dataclass
class MemoryPattern:
    process: SimpleProcessHandle
    module: ProcessModule
    signature: str
