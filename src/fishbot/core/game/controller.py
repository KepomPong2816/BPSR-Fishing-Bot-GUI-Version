import time

import pyautogui as auto

from src.fishbot.utils.logger import log

class GameController:
    def __init__(self, config):
        self.config = config.bot
        self._debug = False
        auto.FAILSAFE = True
        auto.PAUSE = 0.05

    def set_debug(self, enabled: bool):
        self._debug = enabled

    def _log(self, message: str):
        if self._debug:
            log(message)

    def press_key(self, key):
        self._log(f"[CONTROLLER] 🔘 Pressing key: {key}")
        auto.press(key)
        time.sleep(0.1)

    def click(self, button='left', clicks=1, interval=0.1):
        self._log(f"[CONTROLLER] 🖱️ Clicking: {button} ({clicks}x)")
        auto.click(button=button, clicks=clicks, interval=interval)
        time.sleep(0.15)

    def click_at(self, x, y, button='left'):
        self._log(f"[CONTROLLER] 🖱️ Clicking at ({x}, {y})")
        auto.click(x, y, button=button)
        time.sleep(0.15)

    def move_to(self, x, y):
        self._log(f"[CONTROLLER] 📍 Moving mouse to: ({x}, {y})")
        auto.moveTo(x, y, duration=0.2)
        time.sleep(0.1)

    def mouse_down(self, button='left'):
        self._log(f"[CONTROLLER] 🖱️ ⬇️ Holding mouse: {button}")
        auto.mouseDown(button=button)
        time.sleep(0.1)

    def mouse_up(self, button='left'):
        self._log(f"[CONTROLLER] 🖱️ ⬆️ Releasing mouse: {button}")
        auto.mouseUp(button=button)
        time.sleep(0.1)

    def key_down(self, key):
        self._log(f"[CONTROLLER] 🔘 ⬇️ Holding key: {key}")
        auto.keyDown(key)

    def key_up(self, key):
        self._log(f"[CONTROLLER] 🔘 ⬆️ Releasing key: {key}")
        auto.keyUp(key)

    def release_all_controls(self):
        log("[CONTROLLER] ⚠️ Releasing all controls...")
        auto.mouseUp(button='left')
        auto.mouseUp(button='right')
        auto.keyUp('a')
        auto.keyUp('d')