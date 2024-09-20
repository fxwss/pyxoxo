import random
import keyboard
import mouse

from dataclasses import dataclass
from typing import Union

from logger import logger
from process.interfaces import ComplexProcessHandle
from sdk.local_player import get_local_player
from utils import shot_after


@dataclass(eq=True, frozen=True)
class Config:
    key: Union[str, None] = 'shift'
    should_shoot_alies: bool = True
    max_speed = 73.0
    delay = (20, 60)
    debug = False

config = Config()

def update(process: ComplexProcessHandle):
    player = get_local_player(process)

    if player.speed > config.max_speed:
        return

    if config.key and not keyboard.is_pressed('shift'):
        return

    if mouse.is_pressed():
        return

    entity = player.in_crosshair()

    if entity and config.debug:
        logger.info(f"Entity in crosshair: {str(entity.id).zfill(3)} | isAlive: {entity.is_alive()} | isEnemy: {player.enemy_of(entity)} | team: {entity.team} x {player.team} | health: {entity.health}")

    if entity is None:
        return

    if not entity.is_alive():
        return
    
    if not config.should_shoot_alies and not player.enemy_of(entity):
        return    

    delay = random.randint(*config.delay)
    
    shot_after(delay)

