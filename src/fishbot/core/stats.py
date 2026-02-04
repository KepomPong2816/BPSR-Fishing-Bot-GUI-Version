import time


class StatsTracker:
    def __init__(self):
        self.stats = {
            'cycles': 0,
            'fish_caught': 0,
            'fish_escaped': 0,
            'rod_breaks': 0,
            'timeouts': 0
        }
        self._start_time: float = 0
        self._session_start: float = 0
        self._hourly_catches: list = []

    def start_session(self):
        self._session_start = time.time()
        self._start_time = self._session_start
        self._hourly_catches = []

    def increment(self, stat_name: str, value: int = 1):
        if stat_name in self.stats:
            self.stats[stat_name] += value
            
            if stat_name == 'fish_caught':
                self._hourly_catches.append(time.time())

    def get_elapsed_seconds(self) -> int:
        if self._session_start == 0:
            return 0
        return int(time.time() - self._session_start)

    def get_elapsed_formatted(self) -> str:
        elapsed = self.get_elapsed_seconds()
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_catch_rate(self) -> float:
        total = self.stats['fish_caught'] + self.stats['fish_escaped']
        if total == 0:
            return 0.0
        return (self.stats['fish_caught'] / total) * 100

    def get_fish_per_hour(self) -> float:
        elapsed_hours = self.get_elapsed_seconds() / 3600
        if elapsed_hours < 0.001:
            return 0.0
        return self.stats['fish_caught'] / elapsed_hours

    def get_catches_last_hour(self) -> int:
        if not self._hourly_catches:
            return 0
        
        one_hour_ago = time.time() - 3600
        return sum(1 for t in self._hourly_catches if t >= one_hour_ago)

    def get_extended_stats(self) -> dict:
        return {
            **self.stats,
            'catch_rate': round(self.get_catch_rate(), 1),
            'fish_per_hour': round(self.get_fish_per_hour(), 1),
            'elapsed': self.get_elapsed_formatted(),
            'catches_last_hour': self.get_catches_last_hour()
        }

    def reset(self):
        for key in self.stats:
            self.stats[key] = 0
        self._hourly_catches = []
        self._session_start = 0

    def show(self):
        print("\n" + "=" * 50)
        print("📊 SESSION STATISTICS")
        print("=" * 50)
        print(f"  ⏱️ Duration: {self.get_elapsed_formatted()}")
        print(f"  🐟 Fish Caught: {self.stats['fish_caught']}")
        print(f"  💨 Fish Escaped: {self.stats['fish_escaped']}")
        print(f"  📈 Catch Rate: {self.get_catch_rate():.1f}%")
        print(f"  ⚡ Fish/Hour: {self.get_fish_per_hour():.1f}")
        print(f"  🔧 Rod Breaks: {self.stats['rod_breaks']}")
        print(f"  ⏱️ Timeouts: {self.stats['timeouts']}")
        print(f"  🔄 Cycles: {self.stats['cycles']}")
        print("=" * 50)