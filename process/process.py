import ctypes
import struct
from ctypes import wintypes
from dataclasses import dataclass
from typing import Any

from process.structs import MEMORY_BASIC_INFORMATION


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

    def read(self):
        return read_memory(self.process, self.address, self.format)

    def write(self):
        write_memory(self.process, self.address, self.data)

    def __add__(self, other):
        if isinstance(other, int):
            return MemoryPiece(self.process, self.address + other, self.data, self.format)

        raise TypeError


def get_all_processes():

    # get the handle to the process
    handle: int = ctypes.windll.kernel32.CreateToolhelp32Snapshot(
        0x00000002, 0)

    if ctypes.windll.kernel32.GetLastError() or handle == -1:
        raise Exception("Failed to get process handle")

    # create a class to store the process info
    class ProcessEntry32(ctypes.Structure):
        _fields_ = [
            ('dwSize', ctypes.c_ulong),
            ('cntUsage', ctypes.c_ulong),
            ('th32ProcessID', ctypes.c_ulong),
            ('th32DefaultHeapID', ctypes.POINTER(ctypes.c_ulong)),
            ('th32ModuleID', ctypes.c_ulong),
            ('cntThreads', ctypes.c_ulong),
            ('th32ParentProcessID', ctypes.c_ulong),
            ('pcPriClassBase', ctypes.c_ulong),
            ('dwFlags', ctypes.c_ulong),
            ('szExeFile', ctypes.c_char * wintypes.MAX_PATH)
        ]

    def parse_process(process: ProcessEntry32):
        name = process.szExeFile.decode('utf-8')
        pid = process.th32ProcessID
        process_handle = ctypes.windll.kernel32.OpenProcess(
            0xFFFF, False, pid)

        if ctypes.windll.kernel32.GetLastError() not in (0, 5, 87) or process_handle == -1:
            raise Exception("Failed to get process handle")
        ctypes.windll.kernel32.SetLastError(0)

        yield SimpleProcessHandle(name, pid, process_handle)

    process = ProcessEntry32()
    process.dwSize = ctypes.sizeof(ProcessEntry32)

    if ctypes.windll.kernel32.Process32First(handle, ctypes.byref(process)):
        yield from parse_process(process)

    while ctypes.windll.kernel32.Process32Next(handle, ctypes.byref(process)):
        yield from parse_process(process)

    # Process32Next should throw a error 18 if there are no more processes
    if ctypes.windll.kernel32.GetLastError() != 18:
        raise Exception("Failed to get process handle")

    ctypes.windll.kernel32.SetLastError(0)
    ctypes.windll.kernel32.CloseHandle(handle)


def fill_process_with_modules(process: SimpleProcessHandle):
    return ComplexProcessHandle(
        name=process.name,
        pid=process.pid,
        handle=process.handle,
        modules=set(get_all_modules(process))
    )


def find_process_by_name(name: str, fill_modules=True):
    process = next((p for p in get_all_processes() if p.name == name), None)

    if not process:
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


def get_all_modules(process: SimpleProcessHandle, buffer_size=1024):
    handle: int = ctypes.windll.kernel32.OpenProcess(
        0xFFFF, False, process.pid)

    if ctypes.windll.kernel32.GetLastError() not in (0, 5, 87) or handle == -1:
        raise Exception("Failed to get process handle")
    ctypes.windll.kernel32.SetLastError(0)

    class MODULEINFO(ctypes.Structure):
        _fields_ = [
            ("lpBaseOfDll", ctypes.c_void_p),
            ("SizeOfImage", ctypes.c_ulong),
            ("EntryPoint", ctypes.c_void_p),
        ]

    modules = (ctypes.c_void_p * 1024)()
    ctypes.windll.kernel32.SetLastError(0)

    def get_module_name(module: MODULEINFO):
        name = ctypes.create_string_buffer(buffer_size)
        ctypes.windll.psapi.GetModuleBaseNameA(
            handle,
            ctypes.c_void_p(module.lpBaseOfDll),
            ctypes.byref(name),
            ctypes.sizeof(name)
        )
        return name.value.decode('utf-8')

    if ctypes.windll.psapi.EnumProcessModulesEx(
        handle,
        ctypes.byref(modules),
        ctypes.sizeof(modules),
        ctypes.byref(ctypes.c_ulong()),
        0x03
    ):
        for module in modules:

            if not module:
                continue

            module_info = MODULEINFO()
            ctypes.windll.psapi.GetModuleInformation(
                handle,
                ctypes.c_void_p(module),
                ctypes.byref(module_info),
                ctypes.sizeof(module_info)
            )

            yield ProcessModule(
                name=get_module_name(module_info),
                base_address=module_info.lpBaseOfDll,
                size=module_info.SizeOfImage
            )


# we can memoize modules info as it doesn't change
_modules_memoize: dict[ctypes.c_void_p, dict[str, ProcessModule]] = {}


def find_module_by_name(process: SimpleProcessHandle | ComplexProcessHandle, name: str):

    # use process handle as key
    if process.handle not in _modules_memoize:
        _modules_memoize[process.handle] = {}

    # use module name as key
    if name not in _modules_memoize[process.handle]:
        if isinstance(process, SimpleProcessHandle):
            process = fill_process_with_modules(process)

        module = next(
            (m for m in process.modules if m.name == name), None)

        if not module:
            raise Exception("Module not found")

        _modules_memoize[process.handle][name] = module

    return _modules_memoize[process.handle][name]


def virtual_query(process: SimpleProcessHandle, address: int):
    information = MEMORY_BASIC_INFORMATION()

    ctypes.windll.kernel32.VirtualQueryEx(
        process.handle,
        int(address),
        ctypes.byref(information),
        ctypes.sizeof(information)
    )

    error = ctypes.windll.kernel32.GetLastError()
    ctypes.windll.kernel32.SetLastError(0)

    if error:
        raise Exception(f"VirtualQueryEx failed with error {error}")

    return information


def has_active_window(process: SimpleProcessHandle):
    # get the process window
    window = ctypes.windll.user32.GetForegroundWindow()

    # get the process id from the window
    window_pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(
        window, ctypes.byref(window_pid))

    # check if the process id is the same as the process id we are looking for
    if window_pid.value == process.pid:
        return True

    return False


def read_memory(process: SimpleProcessHandle, address: int, format: str = 'i'):
    # create a buffer to store the data
    size = struct.calcsize(format)
    buffer = ctypes.create_string_buffer(size)
    bytes_read = wintypes.DWORD(0)

    ctypes.windll.kernel32.ReadProcessMemory(
        process.handle,
        int(address),
        ctypes.byref(buffer),
        size,
        ctypes.byref(bytes_read)
    )

    if bytes_read.value != size:
        raise Exception(
            f'''
            Failed to read memory, last error: {ctypes.windll.kernel32.GetLastError()}
                {process.name} [{hex(address)}]
                {format} : {bytes_read.value} / {size}
                {buffer.raw}
            ''')

    return MemoryPiece(
        process=process,
        address=address,
        data=buffer.raw,
        format=format
    )


def write_memory(process: SimpleProcessHandle, address: int, data: bytes | int | float):
    # create a variable to store the number of bytes written
    bytes_written = wintypes.DWORD(0)

    if isinstance(data, int):
        data = struct.pack('i', data)

    if isinstance(data, float):
        data = struct.pack('f', data)

    # write the memory
    ctypes.windll.kernel32.WriteProcessMemory(
        process.handle, int(address), data, len(data), ctypes.byref(bytes_written))

    # if the number of bytes written is not the same as the size
    if bytes_written.value != len(data):
        # raise an exception
        raise Exception("Failed to write memory")

    # return the data
    return bytes_written.value
