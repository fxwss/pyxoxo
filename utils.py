import subprocess
import time
from sys import platform
from typing import Callable

from ewmh import EWMH
from threading import Thread


from logger import logger
from process import find_module_by_name, read_memory
from process import offsets
from process.interfaces import SimpleProcessHandle
from taks import TaskPool


# https://stackoverflow.com/questions/564695/is-there-a-way-to-change-effective-process-name-in-python
def set_proc_name(name: str):
    if not 'linux' in platform:
        return logger.warning("set_proc_name is only supported on linux")

    from ctypes import byref, cdll, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')

    buff = create_string_buffer(len(name) + 1)
    buff.value = name.encode()
    
    libc.prctl(15, byref(buff), 0, 0, 0)

def run_after(delay_in_ms: int, func: Callable):
  TaskPool.new(delay_in_ms, func)

class Store:
    _last_shot = 0.0

def shot(delay_per_shot_ms = 120, debug = False):
    # Make sure we don't shoot too fast
    if time.time() - Store._last_shot < delay_per_shot_ms / 1000:
        return

    if debug:
        logger.info(f"Shooting: {time.time() - Store._last_shot}")

    Store._last_shot = time.time()

    subprocess.run(["xdotool", "click", "1"])


def shot_after(delay_in_ms: int):
    run_after(delay_in_ms, shot)    

def get_window_by_name(name: str):
    if not 'linux' in platform:
        return logger.warning("get_window_by_name is only supported on linux")

    ewmh = EWMH()

    def frame(client):
        frame = client
        
        while frame.query_tree().parent != ewmh.root:
            frame = frame.query_tree().parent

        return frame

    for client in ewmh.getClientList():
        f = frame(client)

        if f is None:
            continue

        if f.get_wm_name() == name:
            return f

def get_window_rect(title = 'Counter-Strike 2'):

    if not 'linux' in platform:
        return logger.warning("get_window_rect is only supported on linux")
    
    frame = get_window_by_name(title)

    if frame is None:
        return logger.warning("Couldn't find window")

    geometry = frame.get_geometry()

    return (geometry.x, geometry.y, geometry.width, geometry.height)

def create_thread(func: Callable, daemon = True):
    thread = Thread(target=func, daemon=daemon)
    thread.start()

    return thread

def world_to_screen(process: SimpleProcessHandle, vector: tuple[float, float, float]):
    client = find_module_by_name(process, "libclient.so")

    # float[4][4] inline = float[16]
    view_matrix = read_memory(process, client + offsets.dwViewMatrix, '16f').unwrap()

    def matrix(x: int, y: int) -> int:
        return view_matrix[x * 4 + y]

    _x = matrix(0, 0) * vector[0] +\
         matrix(0, 1) * vector[1] +\
         matrix(0, 2) * vector[2] +\
         matrix(0, 3)

    _y = matrix(1, 0) * vector[0] +\
         matrix(1, 1) * vector[1] +\
         matrix(1, 2) * vector[2] +\
         matrix(1, 3)

    w = matrix(3, 0) * vector[0] + matrix(3, 1) * vector[1] + matrix(3, 2) * vector[2] + matrix(3, 3)

    inv_w = 1.0 / w

    _x *= inv_w
    _y *= inv_w

    rect = get_window_rect()

    if not rect:
        raise Exception("Couldn't get window rect")

    left, top, width, height = rect
    right, bottom = left + width, top + height

    x = width  * 0.5
    y = height * 0.5

    x += 0.5 * _x * width  + 0.5
    y -= 0.5 * _y * height + 0.5

    return ( x, y, w )
