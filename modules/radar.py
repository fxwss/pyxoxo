from process.offsets import Offsets
from process.process import ComplexProcessHandle
from sdk.entity import get_local_player, iter_entities


def update(process: ComplexProcessHandle, offsets: Offsets) -> None:
    player = get_local_player(process)

    enemies = filter(
        lambda e: e.valid() and e.enemy_of(player),
        iter_entities(process)
    )

    for enemy in enemies:
        enemy.spot()
