import time

from src.fishbot.utils.logger import log

class StateMachine:
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.bot
        self.states = {}
        self.current_state_name = None
        self.current_state = None
        self.state_start_time = None

    def add_state(self, name, state_instance):
        self.states[name] = state_instance

    def set_state(self, new_state_name, force=False):
        if not force and new_state_name == self.current_state_name:
            return

        if new_state_name not in self.states:
            log(f"[ERROR] Attempted to switch to unknown state: {new_state_name}")
            return

        if self.current_state_name is None:
            log(f"[INFO] Starting state machine in: {new_state_name.name}")
        elif new_state_name != self.current_state_name:
            log(f"[INFO] Changing state: {self.current_state_name.name} -> {new_state_name.name}")
        elif force:
            log(f"[INFO] Forcing state reset: {new_state_name.name}")

        self.current_state_name = new_state_name
        self.current_state = self.states[self.current_state_name]
        self.state_start_time = time.time()

    def _check_state_timeout(self):
        timeout_limit = self.config.state_timeouts.get(self.current_state_name.name)
        if not timeout_limit:
            return False

    def handle(self, screen):
        if self._check_state_timeout():
            return

        new_state_name = self.current_state.handle(screen)
        self.set_state(new_state_name)