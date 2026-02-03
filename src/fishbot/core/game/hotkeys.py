import keyboard
import multiprocessing
from src.fishbot.utils.logger import log
from src.fishbot.utils.roi_visualizer import main as show_roi_visualizer

class Hotkeys:
    def __init__(self, bot):
        self.bot = bot
        self.paused = True
        self.visualizer_process = None
        self._register_hotkeys()

    def _register_hotkeys(self):
        keyboard.add_hotkey('7', self._toggle_pause)
        keyboard.add_hotkey('8', self._stop)
        keyboard.add_hotkey('0', self._toggle_visualizer)
        log("[INFO] Hotkeys registered: '7' (Pause/Resume), '8' (Exit), '0' (HUD Visualizer)")

    def _toggle_pause(self):
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RUNNING"
        log(f"[HOTKEY] Bot {status}.")

    def _stop(self):
        log("[HOTKEY] Stopping the bot...")
        if self.visualizer_process and self.visualizer_process.is_alive():
            self.visualizer_process.terminate()
        self.bot.stop()

    def _toggle_visualizer(self):
        if self.visualizer_process and self.visualizer_process.is_alive():
            log("[HOTKEY] Closing the HUD visualizer.")
            self.visualizer_process.terminate()
            self.visualizer_process = None
        else:
            log("[HOTKEY] Opening the HUD visualizer.")
            self.visualizer_process = multiprocessing.Process(target=show_roi_visualizer, daemon=True)
            self.visualizer_process.start()

    def wait_for_exit(self):
        keyboard.wait('8')