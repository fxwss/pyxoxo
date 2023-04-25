
import numpy
from sdk.entity import get_local_player

from process.offsets import Offsets
from process.process import ComplexProcessHandle, find_module_by_name, read_memory


def Vector3(x, y, z):
    return numpy.array([x, y, z])


def calc_angle(source: numpy.ndarray, destiny: numpy.ndarray, view: numpy.ndarray):
    delta = destiny - source
    return numpy.angle(delta)


def update(process: ComplexProcessHandle, offsets: Offsets):
    player = get_local_player(process)
    engine = find_module_by_name(process, 'engine.dll')

    player_team = player.get(offsets.m_iTeamNum).into('i')
    player_eyes_position = \
        Vector3(*player.get(offsets.m_vecOrigin, '3f').into())\
        +\
        Vector3(*player.get(offsets.m_vecViewOffset, '3f').into())

    client_state = read_memory(process, engine + offsets.dwClientState)

    view_angles = Vector3(
        *player.get(offsets.dwClientState_ViewAngles, '3f').into())
