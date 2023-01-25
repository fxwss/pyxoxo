from offsets import Offsets
from process import ComplexProcessHandle
from sdk.entity import Entity, get_local_player, iter_entities


def start(process: ComplexProcessHandle, offsets: Offsets):
    ...


def update(process: ComplexProcessHandle, offsets: Offsets, _):
    player = get_local_player(process)

    def rgba(entity: Entity):
        health = entity.get(offsets.m_iHealth).into('i')
        return (1.0 - (health / 100), health / 100, 0.0, 0.6)

    enemies = filter(
        lambda e: e.valid() and e.enemy_of(player),
        iter_entities(process)
    )

    for enemy in enemies:
        enemy.glow(rgba(enemy))
