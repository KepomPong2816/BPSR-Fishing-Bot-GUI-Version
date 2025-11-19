import time

from .base_interceptor import BaseInterceptor


class LevelCheckInterceptor(BaseInterceptor):

    def check(self, screen):

        if self.detector.find(screen, "level_check"):
            self.bot.log("[GUARD RAIL 1] ⚠️ 'Level Check' UI detected!")
            self.bot.log("[GUARD RAIL 1] Resetting to rod-checking state.")

            self.controller.release_all_controls()

            if hasattr(self.bot.states["PLAYING_MINIGAME"], '_current_arrow'):
                self.bot.states["PLAYING_MINIGAME"]._current_arrow = None
            self.bot.set_state("CHECKING_ROD")
            time.sleep(1)
            return True

        return False