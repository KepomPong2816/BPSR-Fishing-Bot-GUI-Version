import time

from ..bot_state import BotState
from ..state_type import StateType


class StartingState(BotState):

    def __init__(self, bot):
        super().__init__(bot)
        self._last_search_log = 0

    def _scale_coords(self, base_x: int, base_y: int) -> tuple:
        scale_x, scale_y = self.config.detection.get_scale_info()
        return (
            int(base_x * scale_x) + self.window.monitor_x,
            int(base_y * scale_y) + self.window.monitor_y
        )

    def handle(self, screen):
        if self.detector.find(screen, "connect_server", 5, debug=self.bot.debug_mode):
            x, y = self._scale_coords(1100, 795)

            self.controller.move_to(x, y)
            time.sleep(0.5)
            self.controller.move_to(x, y)
            time.sleep(0.5)
            self.controller.click('left')
            time.sleep(1)

            self.bot.log("[RECONNECT] ✅ confirm server connection")

        pos = self.detector.find(screen, "fishing_spot_btn", 5, debug=self.bot.debug_mode)

        if pos:
            self.bot.log(f"[STARTING] ✅ Fishing spot detected at {pos}")
            self.bot.log("[STARTING] Pressing 'F'...")
            time.sleep(0.5)

            self.controller.press_key('f')
            self.bot.log("[STARTING] Entering fishing mode")
            time.sleep(2)

            return StateType.CHECKING_ROD

        already_fishing = self.detector.find(screen, "level_check", 5, debug=self.bot.debug_mode)

        if already_fishing:
            self.bot.log("[STARTING] 🎣 Already in fishing mode — skipping interaction")
            return StateType.CHECKING_ROD      
        
        current_time = time.time()
        if current_time - self._last_search_log > 2:
            self.bot.log("[STARTING] 🔍 Searching for fishing spot...")
            self.controller.key_down('s')
            self.controller.key_down('d')
            time.sleep(0.1)
            self.controller.key_up('s')
            self.controller.key_up('d')

            if self.bot.debug_mode:
                self.bot.log("[STARTING] 💡Debug enabled")
            self._last_search_log = current_time

        return StateType.STARTING
