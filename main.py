from cheat.cheat import Cheat
from cheat.module import CheatModule
from modules import bhop, glow, radar, trigger, aimbot


def main():
    Cheat(
        'csgo.exe',
        [
            CheatModule('Glow', glow.update),
            CheatModule('Bunny hopping', bhop.update),
            CheatModule('Trigger', trigger.update),
            CheatModule('Radar', radar.update),
            CheatModule('Aimbot', aimbot.update)
        ]
    )\
        .start_modules()\
        .wait()


if __name__ == "__main__":
    main()
