import time

from ..bot_state import BotState
from ..state_type import StateType
from src.fishbot.utils.retry_handler import RetryHandler


class PlayingMinigameState(BotState):

    def __init__(self, bot):
        super().__init__(bot)
        self._current_direction = None
        self.switch_delay = 0.5
        self._retry_handler = RetryHandler(
            max_retries=3,
            base_delay=0.3,
            max_delay=2.0,
            exponential=True
        )

    def _handle_arrow(self, direction, screen):
        arrow_template = f"{direction}_arrow"
        key_to_press = 'a' if direction == 'left' else 'd'
        key_to_release = 'd' if direction == 'left' else 'a'
        opposite_direction = 'right' if direction == 'left' else 'left'

        if self.detector.find(screen, arrow_template):
            if self._current_direction is None:
                self.bot.log(f"[MINIGAME] ▶️ Moving to the {direction} (Holding '{key_to_press}')")
                self.controller.key_down(key_to_press)
                self._current_direction = direction
                time.sleep(self.switch_delay)

            if self._current_direction == opposite_direction:
                self.bot.log(f"[MINIGAME] ◀️ Switching to the {direction} (Releasing '{key_to_release}')")
                self.controller.key_up(key_to_release)
                self._current_direction = None
                time.sleep(self.switch_delay)

    def _click_continue_with_retry(self, screen) -> bool:
        continue_pos = self.detector.find(screen, "continue", 5, debug=False)
        if continue_pos:
            def try_click():
                self.controller.click_at(continue_pos[0], continue_pos[1])
                time.sleep(0.3)
                new_screen = self.detector.capture_screen()
                return new_screen
            
            def check_success(new_screen):
                if new_screen is None:
                    return False
                return self.detector.find(new_screen, "continue", 5, debug=False) is None
            
            def on_retry(attempt, delay):
                self.bot.log(f"[MINIGAME] ⏳ Retry click #{attempt} (wait {delay:.1f}s)")
            
            result = self._retry_handler.execute(
                func=try_click,
                success_check=check_success,
                on_retry=on_retry
            )
            
            return result is not None
        
        return False

    def handle(self, screen):
        fish_complete = 0
        failed = 0

        if self.detector.find(screen, "success", 1, debug=False):
            fish_complete = 1
            self.bot.log("[MINIGAME] 🐟 Fish caught!")
            self.bot.stats.increment('fish_caught')

        if fish_complete == 0 and self.detector.find(screen, "failure", 1, debug=False):
            fish_complete = 1
            failed = 1
            self.bot.log("[MINIGAME] 🐟 Fish got away!")
            self.bot.stats.increment('fish_escaped')            
            
        if fish_complete == 1:
            self.controller.release_all_controls()
            self._current_direction = None

            if self.config.quick_finish_enabled:
                self.bot.log("[MINIGAME] ⏩ Quick finishing...")
                self.controller.press_key('esc')
                time.sleep(0.5)
                return StateType.STARTING
            else:
                if failed == 0:
                    return StateType.FINISHING
                else:
                    time.sleep(2)
                    return StateType.CHECKING_ROD

        if self.detector.find(screen, "continue", 5, debug=False):
            self.bot.log("[MINIGAME] 🎯 Continue button detected (instant catch)")
            self.controller.release_all_controls()
            self._current_direction = None
            self.bot.stats.increment('fish_caught')
            
            if self.config.quick_finish_enabled:
                self.bot.log("[MINIGAME] ⏩ Quick finishing...")
                self.controller.press_key('esc')
                time.sleep(0.5)
                return StateType.STARTING
            else:
                return StateType.FINISHING

        self._handle_arrow('left', screen)
        self._handle_arrow('right', screen)

        return StateType.PLAYING_MINIGAME