import ctypes
from math import ceil
import os
import struct

from ctypes import wintypes
from dataclasses import dataclass
from typing import Any, Generator

from logger import logger
from process.interfaces import ComplexProcessHandle, MemoryPattern, MemoryPiece, ProcessModule, SimpleProcessHandle

libc = ctypes.CDLL("libc.so.6")

def get_process_base(process: SimpleProcessHandle):
    lines = filter(
        lambda line: process.name in line,
        [
            line for line in 
            # TODO: probably needs to be closed?
            open('/proc/' + str(process.pid) + '/maps')
        ]
    )

    bases = map(
        lambda line: int(line[:line.index('-')], 16),
        lines
    )

    return min(bases)

def get_all_processes() -> Generator[SimpleProcessHandle, Any, None]:
  for pid in os.listdir("/proc/"):
    try:
      name = os.readlink(f'/proc/{pid}/exe').split('/')[-1]
      handle = os.open(f'/proc/{pid}/mem', os.O_RDWR)

      yield SimpleProcessHandle(name, int(pid), ctypes.c_void_p(handle))

    except GeneratorExit:
        return

    except:
      continue

def fill_process_with_modules(process: SimpleProcessHandle):
    return ComplexProcessHandle(
        name=process.name,
        pid=process.pid,
        handle=process.handle,
        modules=set(get_all_modules(process))
    )

def find_process_by_name(name: str, fill_modules=True):
    process = next((p for p in get_all_processes() if p.name == name), None)

    if process == None:
        raise Exception("Process not found")

    if fill_modules:
        return fill_process_with_modules(process)

    return process

def ensure_complex(process: SimpleProcessHandle):
    if not isinstance(process, ComplexProcessHandle):
        raise Exception("Process is not complex")

    return process

def ensure_simple(process: SimpleProcessHandle):
    if not isinstance(process, SimpleProcessHandle):
        raise Exception("Process is not simple")

    return process

def get_all_modules(process: SimpleProcessHandle) -> Generator[ProcessModule, Any, None]:
    maps = open(f'/proc/{process.pid}/maps')

    included = set()

    for line in maps:
        if not '/' in line: continue

        base_address = int(line[:line.index('-')], 16)        
        final_address = int(line[line.index('-')+1:line.index(' ')], 16)
        
        size = final_address - base_address

        name = line[line.index('/'):len(line) - 1]

        if name in included:
            continue

        included.add(name)

        yield ProcessModule(
            name.split('/')[-1],
            base_address,
            size
        )

# we can memoize modules info as it doesn't change
_modules_memoize: dict[int, dict[str, ProcessModule]] = {}


def find_module_by_name(process: SimpleProcessHandle | ComplexProcessHandle, name: str):

    if not process.handle.value:
        raise Exception("Process handle is not valid")

    # use process handle as key
    if process.handle.value not in _modules_memoize:
        _modules_memoize[process.handle.value] = {}

    # use module name as key
    if name not in _modules_memoize[process.handle.value]:
        if isinstance(process, SimpleProcessHandle):
            process = fill_process_with_modules(process)

        module = next(
            (m for m in process.modules if m.name == name), None)

        if not module:
            raise Exception("Module not found")

        if not process.handle.value:
            raise Exception("Process handle is not valid")

        _modules_memoize[process.handle.value][name] = module

    return _modules_memoize[process.handle.value][name] # type: ignore

def has_active_window(process: SimpleProcessHandle):
    return True

def read_memory(process: SimpleProcessHandle, address: int, format: str = 'i'):
    # create a buffer to store the data
    size = struct.calcsize(format)
    buffer = ctypes.create_string_buffer(size)

    libc.pread(process.handle, 
               ctypes.pointer(buffer), 
               size, 
               ctypes.c_long(address))

    return MemoryPiece(
        process=process,
        address=address,
        data=buffer.raw,
        format=format
    )

def write_memory(process: SimpleProcessHandle, address: int, data: bytes | int | float):
    raise NotImplementedError('linux::write_memory is not implemented')

def ensure_bytes(t: Any) -> bytes:
    if isinstance(t, bytes):
        return t

    if isinstance(t, int):
        return t.to_bytes(4, 'little')

    if isinstance(t, float):
        return struct.pack('f', t)

    raise TypeError

def pattern_compare(pattern: MemoryPattern, memory: MemoryPiece) -> bool:
    signature = pattern.signature.replace(' ', '')

    if memory.process.pid != pattern.process.pid:
        logger.error('Memory piece and pattern are from different processes')
        return False
    
    memory_as_bytes = ensure_bytes(memory.unwrap())

    # each byte is represented by two characters in the signature
    # so we need to divide by 2
    for i in range(len(signature) // 2):

        if signature[i*2:i*2+2] == '??':
            continue

        sig_byte = bytes.fromhex(signature[i*2:i*2+2])
        mem_byte = memory_as_bytes[i*2:i*2+1]

        if sig_byte != mem_byte:
            return False

    return True


def pattern_scan(pattern: MemoryPattern):
    module = pattern.module

    # example input: '83 FB ?? 75 ?? 48 8D 05 ?? ?? ?? ?? 48 8B 00'
    signature = pattern.signature.replace(' ', '')
    # -> '83FB??75??488D05????????488B00'

    # each pair of characters is a byte
    # so we need to divide by 2
    size = len(signature) // 2
    
    # current address to read
    address = module.base_address

    pages = ceil(module.size / size)

    logger.info(f'Signature scan started: {module.name} -> {signature} | size: {size} bytes | {hex(address)} - {hex(module.base_address + module.size)} / {pages}')

    while address < module.base_address + module.size:

        if pattern_compare(pattern, read_memory(pattern.process, address, f'{size}s')):
            return address

        address += size
    
    return None

