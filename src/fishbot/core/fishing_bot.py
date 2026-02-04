import time

from src.fishbot.config import Config
from src.fishbot.core.game.controller import GameController
from src.fishbot.core.game.detector import Detector
from src.fishbot.core.interceptors.level_check_interceptor import LevelCheckInterceptor
from src.fishbot.core.state.impl.casting_bait_state import CastingBaitState
from src.fishbot.core.state.impl.checking_rod_state import CheckingRodState
from src.fishbot.core.state.impl.finishing_state import FinishingState
from src.fishbot.core.state.impl.playing_minigame_state import PlayingMinigameState
from src.fishbot.core.state.impl.starting_state import StartingState
from src.fishbot.core.state.impl.waiting_for_bite_state import WaitingForBiteState
from src.fishbot.core.state.state_machine import StateMachine
from src.fishbot.core.state.state_type import StateType
from src.fishbot.core.stats import StatsTracker
from src.fishbot.utils.logger import log, set_debug_mode
from src.fishbot.utils.config_watcher import ConfigWatcher
from src.fishbot.config.paths import get_user_rois_path


class FishingBot:
    def __init__(self, window_mode: str = 'Auto Detect', custom_width: int = 1920, custom_height: int = 1080):
        self.config = Config(
            window_mode=window_mode,
            custom_width=custom_width,
            custom_height=custom_height
        )
        self.stats = StatsTracker()
        self.log = log

        use_async = getattr(self.config.bot, 'async_capture_enabled', True)
        self.detector = Detector(self.config, use_async=use_async)
        self.controller = GameController(self.config)
        self.state_machine = StateMachine(self)

        self.level_check_interceptor = LevelCheckInterceptor(self)

        self._stopped = False
        self.debug_mode = self.config.bot.debug_mode
        
        set_debug_mode(self.debug_mode)
        self.controller.set_debug(self.debug_mode)

        self.target_delay = 0
        if self.config.bot.target_fps > 0:
            self.target_delay = 1.0 / self.config.bot.target_fps

        self._register_states()
        
        self._config_watcher = None
        self._setup_config_watcher()

    def _setup_config_watcher(self):
        try:
            width, height = self.config.bot.detection.get_current_resolution()
            rois_path = get_user_rois_path(width, height)
            
            self._config_watcher = ConfigWatcher(
                file_path=rois_path,
                callback=self._on_config_changed,
                poll_interval=2.0
            )
            self._config_watcher.start()
            log("[BOT] Config hot reload enabled")
        except Exception as e:
            log(f"[BOT] Config watcher failed: {e}")

    def _on_config_changed(self):
        try:
            self.config.bot.detection.reload_config()
            log("[BOT] ⚡ ROI config reloaded")
        except Exception as e:
            log(f"[BOT] Config reload error: {e}")

    def _register_states(self):
        self.state_machine.add_state(StateType.STARTING, StartingState(self))
        self.state_machine.add_state(StateType.CHECKING_ROD, CheckingRodState(self))
        self.state_machine.add_state(StateType.CASTING_BAIT, CastingBaitState(self))
        self.state_machine.add_state(StateType.WAITING_FOR_BITE, WaitingForBiteState(self))
        self.state_machine.add_state(StateType.PLAYING_MINIGAME, PlayingMinigameState(self))
        self.state_machine.add_state(StateType.FINISHING, FinishingState(self))

    def start(self):
        log("[INFO] 🎣 Bot ready!")
        log("[INFO] IMPORTANT: Keep the game in FOCUS (active window)")
        log("[INFO] CREDIT: https://github.com/hyuse98/BPSR-Fishing-Bot")
        log("[INFO] MODIFIED: https://github.com/KepomPong2816")
        log(f"[INFO] Accuracy: {self.config.bot.detection.precision * 100:.0f}%")
        log(f"[INFO] Target FPS: {'MAX' if self.config.bot.target_fps == 0 else self.config.bot.target_fps}")
        log("[INFO] Warming up detection system...")
        time.sleep(1)
        self.state_machine.set_state(StateType.STARTING)

    def update(self):
        if self._stopped:
            return

        loop_start = time.time()

        screen = self.detector.capture_screen()
        if screen is None:
            return

        self.state_machine.handle(screen)

        if self.target_delay > 0:
            loop_time = time.time() - loop_start
            sleep_time = max(0, self.target_delay - loop_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        if not getattr(self, "_stats_shown", False):
            self.stats.show()
            self._stats_shown = True

        if not self._stopped:
            self.log("[BOT] 🛑 Shutting down the bot...")
            self._stopped = True

            if self._config_watcher:
                self._config_watcher.stop()

            try:
                self.detector.cleanup()
            except Exception as e:
                self.log(f"[ERROR] Failed to cleanup detector: {e}")

            try:
                self.controller.release_all_controls()
            except Exception as e:
                self.log(f"[ERROR] Failed to release controls: {e}")

    def is_stopped(self):
        return self._stopped