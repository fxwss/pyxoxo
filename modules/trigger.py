from dataclasses import dataclass
from offsets import Offsets
from process import ComplexProcessHandle
from sdk.entity import get_local_player
from input.input import KeyCodes, Keyboard


@dataclass(eq=True, frozen=True)
class Config:
    key: KeyCodes


config = Config(KeyCodes.LeftShift)


def start(process: ComplexProcessHandle, offsets: Offsets):
    ...


def update(process: ComplexProcessHandle, offsets: Offsets, _):
    player = get_local_player(process)

    if config.key and not Keyboard.is_pressed(config.key):
        return

    entity = player.in_crosshair()
    if not entity or not entity.valid() or not player.enemy_of(entity):
        return

    player.attack()
