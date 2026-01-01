import time

from ..bot_state import BotState
from ..state_type import StateType


class CheckingRodState(BotState):

    def handle(self, screen):
        self.bot.log("[CHECKING_ROD] Checking rod...")

        time.sleep(1)

        found_rod = 0

        if self.detector.find(screen, "reg_rod", 5, debug=True):
            found_rod = 1

        if found_rod == 0 and self.detector.find(screen, "sturdy_rod", 5, debug=True):
            found_rod = 1
               
        if found_rod == 0:
            self.bot.log("[CHECKING_ROD] ⚠️  Broken rod! Replacing...")
            self.bot.stats.increment('rod_breaks')
            time.sleep(1)

            self.controller.press_key('m')
            time.sleep(1)

            self.controller.move_to(1650, 600)
            time.sleep(0.5)
            self.controller.move_to(1650, 600)
            time.sleep(0.5)
            self.controller.click('left')
            time.sleep(1)

            self.bot.log("[CHECKING_ROD] ✅ Rod replaced")
        else:
            time.sleep(1)
            self.bot.log("[CHECKING_ROD] ✅ Rod OK")

        return StateType.CASTING_BAIT
