from .bot_config import BotConfig
from .paths import PACKAGE_ROOT, ASSETS_PATH, TEMPLATES_PATH


class Config:

    def __init__(self, window_mode: str = 'Auto Detect', custom_width: int = 1920, custom_height: int = 1080):
        self.bot = BotConfig(
            window_mode=window_mode,
            custom_width=custom_width,
            custom_height=custom_height
        )

        self.paths = {
            'package_root': PACKAGE_ROOT,
            'assets': ASSETS_PATH,
            'templates': TEMPLATES_PATH
        }

    def get_template_path(self, template_name):
        filename = self.bot.detection.templates[template_name]

        if filename:
            return self.paths['templates'] / filename
        return None
