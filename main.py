import os

from cheat.cheat import Cheat
from cheat.module import CheatModule

from utils import set_proc_name
from logger import logger

from modules import triggerbot, esp


def main():
    logger.info("xoxo: setting title")
    set_proc_name('xoxo')

    pid = os.getpid()
    logger.info(f"PID: {pid}")

    Cheat(
        'cs2',
        [
            CheatModule('Trigger', triggerbot.update, 1 / 60),
            CheatModule('ESP', esp.update, 1 / 1000)
        ]
    )\
        .start_modules()\
        .render_gui()\
        .wait()


if __name__ == "__main__":
    main()