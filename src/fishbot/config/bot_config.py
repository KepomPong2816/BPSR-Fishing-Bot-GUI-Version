from .screen_config import ScreenConfig
from .detection_config import DetectionConfig

class BotConfig:
    def __init__(self, window_mode: str = 'Auto Detect', custom_width: int = 1920, custom_height: int = 1080):
        self.detection = DetectionConfig()
        
        self.screen = ScreenConfig(
            detection_config=self.detection,
            window_mode=window_mode,
            custom_width=custom_width,
            custom_height=custom_height
        )

        self.state_timeouts = {
            "STARTING": 8,
            "CHECKING_ROD": 13,
            "CASTING_BAIT": 13,
            "WAITING_FOR_BITE": 23,
            "PLAYING_MINIGAME": 28,
            "FINISHING": 8
        }

        self.quick_finish_enabled = False
        self.debug_mode = False

        self.target_fps = 60

        self.default_delay = 0.3
        self.finish_wait_delay = 0.3
        self.casting_delay = 0.3
