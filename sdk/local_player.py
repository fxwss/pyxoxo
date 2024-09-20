
from dataclasses import dataclass

from process import offsets, find_module_by_name, read_memory
from process.interfaces import ComplexProcessHandle
from sdk.entity import Entity, get_entity


@dataclass(eq=True, frozen=True)
class LocalPlayer(Entity):

    def enemy_of(self, other: Entity):
        return self.team != other.team

    def in_crosshair(self):
        id = self.get(offsets.m_iIDEntIndex).into()

        if id < 1:
            return None

        return get_entity(self.process, id)

    # TODO: Implement stop method
    def stop(self):
        ...

def get_local_player(process: ComplexProcessHandle):
    client = find_module_by_name(process, 'libclient.so')
    address = read_memory(process, client + 0x388C760, 'q').unwrap()

    return LocalPlayer(0, address, process)