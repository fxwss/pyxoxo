from dataclasses import dataclass
from process.offsets import Offsets
from process.process import ComplexProcessHandle
from sdk.entity import get_local_player
from input.input import KeyCodes, Keyboard


@dataclass(eq=True, frozen=True)
class Config:
    key: KeyCodes


config = Config(KeyCodes.LeftShift)


def update(process: ComplexProcessHandle, offsets: Offsets):
    player = get_local_player(process)

    if config.key and not Keyboard.is_pressed(config.key):
        return

    entity = player.in_crosshair()

    if (not entity or not entity.valid() or not player.enemy_of(entity)) and not Keyboard.is_pressed(KeyCodes.LeftMouseButton):
        return

    player.attack()
