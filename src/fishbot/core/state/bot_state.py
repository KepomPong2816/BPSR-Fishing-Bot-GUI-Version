from abc import ABC, abstractmethod

from ..bot_component import BotComponent
from src.fishbot.config.screen_config import ScreenConfig


class BotState(BotComponent, ABC):

    def __init__(self, bot):
        super().__init__(bot)
        self.level_check_interceptor = bot.level_check_interceptor
        self.window = ScreenConfig()

    @abstractmethod
    def handle(self, screen):
        pass