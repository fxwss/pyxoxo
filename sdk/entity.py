import time

from dataclasses import dataclass
from math import sqrt

from process import (ComplexProcessHandle, find_module_by_name, offsets,
                     read_memory)
from sdk.base import BaseEntity

SPACING = 0x78

@dataclass(eq=True, frozen=True)
class Entity(BaseEntity):

    def __add__(self, other):
        if isinstance(other, int):
            return self.address + other

        raise Exception(f"Cannot add {type(other)} to {type(self)}")

    def __mul__(self, other):
        if isinstance(other, int):
            return self.address * other

        raise Exception(f"Cannot multiply {type(self)} by {type(other)}")

    def __int__(self):
        return self.address
    
    def is_alive(self):
        return self.valid() and self.health > 0
    
    @property
    def velocity(self) -> tuple[float, float, float]:
        return self.get(offsets.m_vecVelocity, '3f').unwrap()
    
    @property
    def abs_velocity(self) -> tuple[float, float, float]:
        return self.get(offsets.m_vecAbsVelocity, '3f').unwrap()
    
    @property
    def team(self):
        return self.get(offsets.m_iTeamNum, 'H').unwrap()
    
    @property
    def health(self):
        return self.get(offsets.m_iHealth, 'i').unwrap()
    
    @property
    def speed(self):
        return sqrt(sum(map(lambda x: pow(x, 2), self.abs_velocity)))
    
    @property
    def origin(self):
        return self.get(offsets.m_vOldOrigin, '3f').unwrap()

    @property
    def head(self):
        #scene = self.get(offsets.m_pGameSceneNode, 'Q').unwrap()
        #bones = read_memory(self.process, scene + offsets.m_modelState + 0x80, 'Q').unwrap()

        #return read_memory(self.process, bones + 6 * 32, '3f').unwrap()

        x, y, z =  self.origin

        return x, y, z + 72.0


def get_entity(process: ComplexProcessHandle, id: int) -> Entity:
    if id < 0:
        raise Exception(f"Entity id must be greater than 0, got {id}")

    client = find_module_by_name(process, "libclient.so").base_address
    entity_list = read_memory(process, client + offsets.dwEntityList, 'q').unwrap()

    entry = read_memory(process, entity_list + 0x8 * (id >> 9) + 0x10, 'q').unwrap()
    address = read_memory(process, entry + SPACING * (id & 0x1FF), 'q').unwrap()

    return Entity(id, address, process)

def iter_entities(process: ComplexProcessHandle, start=1, end=64):
    client = find_module_by_name(process, "libclient.so").base_address
    entity_list = read_memory(process, client + offsets.dwEntityList, 'q').unwrap()

    for id in range(start, end):
        entry = read_memory(process, entity_list + 0x10, 'q').unwrap()
        controller = read_memory(process, entry + SPACING * (id & 0x1FF), 'q').unwrap()

        pawn = read_memory(process, controller + 0x794, 'q').unwrap()
        entry_2 = read_memory(process, entity_list + 0x8 * ((pawn & 0x7FFF) >> 9) + 16, 'q').unwrap()

        address = read_memory(process, entry_2 + SPACING * (pawn & 0x1FF), 'q').unwrap()

        entity = Entity(id, address, process)

        yield entity