import ctypes
from process.utils import choose


class MEMORY_BASIC_INFORMATION_x86(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_ulong),
        ("AllocationBase", ctypes.c_ulong),
        ("AllocationProtect", ctypes.c_ulong),
        ("RegionSize", ctypes.c_ulong),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong)
    ]


class MEMORY_BASIC_INFORMATION_x64(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_ulonglong),
        ("AllocationBase", ctypes.c_ulonglong),
        ("AllocationProtect", ctypes.c_ulong),
        ("__alignment1", ctypes.c_ulong),
        ("RegionSize", ctypes.c_ulonglong),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong),
        ("__alignment2", ctypes.c_ulong),
    ]


MEMORY_BASIC_INFORMATION = choose(
    MEMORY_BASIC_INFORMATION_x86,
    MEMORY_BASIC_INFORMATION_x64
)
