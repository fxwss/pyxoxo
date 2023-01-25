from input.input import KeyCodes, Keyboard
from offsets import Offsets
from process import ComplexProcessHandle
from sdk.entity import get_local_player


def start(process: ComplexProcessHandle, offsets: Offsets):
    ...

# Flags
#
# 256 - Air           | 0001 0000 0000
# 257 - Floor         | 0001 0000 0001
# 261 - Mid Crouch    | 0001 0000 0101
# 262 - Air Crouched  | 0001 0000 0110
# 263 - Crouched      | 0001 0000 0111


def update(process: ComplexProcessHandle, offsets: Offsets, _):
    player = get_local_player(process)
    flags = player.get(offsets.m_fFlags).into('i')

    if flags & 1 == 1 and Keyboard.is_pressed(KeyCodes.Space):
        player.jump()
    else:
        player.stop_jump()
