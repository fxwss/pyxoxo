from offsets import Offsets
from process import ComplexProcessHandle
from sdk.entity import get_local_player, iter_entities


def start(process: ComplexProcessHandle, offsets: Offsets):
    ...


def update(process: ComplexProcessHandle, offsets: Offsets, _) -> None:
    player = get_local_player(process)

    enemies = filter(
        lambda e: e.valid() and e.enemy_of(player),
        iter_entities(process)
    )

    for enemy in enemies:
        enemy.spot()
