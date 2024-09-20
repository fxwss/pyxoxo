import random
import keyboard
import mouse

from dataclasses import dataclass

import ui

from logger import logger
from process.interfaces import ComplexProcessHandle
from sdk.entity import iter_entities
from sdk.local_player import get_local_player
from utils import shot_after, world_to_screen


@dataclass(eq=True, frozen=True)
class Config:
    debug = False

config = Config()

def update(process: ComplexProcessHandle):
    for entity in iter_entities(process):
        id = entity.id

        if not entity.is_alive():
            ui.shapes.remove(id)
            continue

        x, y, z = world_to_screen(process, entity.head)

        if not z > 0.01:
            ui.shapes.remove(id)
            continue
        
        ui.shapes.add(ui.Circle.new(x, y, 5, id))
        ui.shapes.add(ui.Line.new(x, y, 960, 540 - 32, id))
