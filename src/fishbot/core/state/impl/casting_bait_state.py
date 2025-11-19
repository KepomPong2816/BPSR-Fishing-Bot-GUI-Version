import time

from ..bot_state import BotState
from ..state_type import StateType


class CastingBaitState(BotState):

    def handle(self, screen):
        self.bot.log(f"[CASTING_BAIT] 🎣 Waiting {self.config.casting_delay} seconds...")
        time.sleep(self.config.casting_delay)

        center_x = self.config.screen.monitor_width // 2 + self.config.screen.monitor_x
        center_y = self.config.screen.monitor_height // 2 + self.config.screen.monitor_y

        self.bot.log(f"[CASTING_BAIT] 📍 Moving mouse to center of the screen ({center_x}, {center_y})")
        self.controller.move_to(center_x, center_y)
        time.sleep(1)

        self.bot.log("[CASTING_BAIT] 🖱️ Clicking to ensure focus...")
        self.controller.click_at(center_x, center_y)
        time.sleep(0.5)

        self.bot.log("[CASTING_BAIT] 🎣 Casting bait...")
        self.controller.mouse_down('left')
        time.sleep(0.1)
        self.controller.mouse_up('left')
        time.sleep(2)

        return StateType.WAITING_FOR_BITE