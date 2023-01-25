from dataclasses import dataclass
from enum import Enum
import offsets as _offsets
from process import ComplexProcessHandle, SimpleProcessHandle, find_module_by_name, read_memory, write_memory

offsets = _offsets.get()


@dataclass(eq=True, frozen=True)
class BaseEntity:
    id: int
    address: int
    process: ComplexProcessHandle

    def get(self, offset: int):
        return read_memory(self.process, self.address + offset)

    def valid(self):
        return bool(self.address) and self.id > 0 and self.id < 32


class Teams(Enum):
    T = 2
    CT = 3


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

    # utils

    def enemy_of(self, entity: BaseEntity) -> bool:
        self_team: int = self.get(offsets.m_iTeamNum).into('i')
        other_team: int = entity.get(offsets.m_iTeamNum).into('i')

        valid_teams = (
            Teams.T,
            Teams.CT
        )

        if self_team not in valid_teams or other_team not in valid_teams:
            return False

        return self_team != other_team

    def spot(self):
        write_memory(self.process, self + offsets.m_bSpotted, 1)

    def glow(self, color: tuple[float, float, float, float]):
        client = find_module_by_name(self.process, "client.dll").base_address
        glow_manager = read_memory(
            self.process, client + offsets.dwGlowObjectManager).into('i')
        glow_index = self.get(offsets.m_iGlowIndex).into('i')

        write_memory(self.process, glow_manager +
                     (glow_index * 0x38) + 0x8, color[0])
        write_memory(self.process, glow_manager +
                     (glow_index * 0x38) + 0xC, color[1])
        write_memory(self.process, glow_manager +
                     (glow_index * 0x38) + 0x10, color[2])
        write_memory(self.process, glow_manager +
                     (glow_index * 0x38) + 0x14, color[3])

        write_memory(self.process, glow_manager +
                     (glow_index * 0x38) + 0x28, 1)


@dataclass(eq=True, frozen=True)
class LocalPlayer(Entity):

    def jump(self):
        client = find_module_by_name(self.process, "client.dll").base_address
        write_memory(self.process, client + offsets.dwForceJump, 5)

    def stop_jump(self):
        client = find_module_by_name(self.process, "client.dll").base_address
        write_memory(self.process, client + offsets.dwForceJump, 4)

    def attack(self):
        client = find_module_by_name(self.process, "client.dll").base_address
        write_memory(self.process, client + offsets.dwForceAttack, 6)

    def start_attack(self):
        client = find_module_by_name(self.process, "client.dll").base_address
        write_memory(self.process, client + offsets.dwForceAttack, 5)

    def stop_attack(self):
        client = find_module_by_name(self.process, "client.dll").base_address
        write_memory(self.process, client + offsets.dwForceAttack, 4)

    def in_crosshair(self):
        id = self.get(offsets.m_iCrosshairId).into('i')

        if id == 0:
            return None

        return get_entity(self.process, id - 1)


def get_local_player(process: ComplexProcessHandle) -> LocalPlayer:
    engine = find_module_by_name(process, "engine.dll").base_address

    client_state = read_memory(process, engine + offsets.dwClientState).into()
    local_player_index = read_memory(process,
                                     client_state + offsets.dwClientState_GetLocalPlayer).into()

    entity = get_entity(process, local_player_index)

    return LocalPlayer(entity.id, entity.address, entity.process)


def get_entity(process: ComplexProcessHandle, id: int) -> Entity:

    if id < 0:
        raise Exception(f"Entity id must be greater than 0, got {id}")

    client = find_module_by_name(process, "client.dll").base_address
    entity_list = client + offsets.dwEntityList

    address = read_memory(process, entity_list + id * 0x10).into()

    return Entity(id, address, process)


def iter_entities(process: ComplexProcessHandle, start=1, end=32):
    for i in range(start, end):
        yield get_entity(process, i)
