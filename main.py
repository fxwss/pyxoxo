from cheat.cheat import Cheat
from cheat.module import CheatModule
from modules import bhop, glow, radar, trigger


def main():
    Cheat(
        'csgo.exe',
        [
            CheatModule('Glow', glow.start, glow.update),
            CheatModule('Bunny hopping', bhop.start, bhop.update),
            CheatModule('Trigger', trigger.start, trigger.update),
            CheatModule('Radar', radar.start, radar.update),
        ]
    )\
        .start_modules()\
        .wait()


if __name__ == "__main__":
    main()
