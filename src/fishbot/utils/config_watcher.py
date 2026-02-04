import os
import threading
import time
from typing import Callable, Optional


class ConfigWatcher:
    def __init__(self, file_path: str, callback: Callable[[], None], poll_interval: float = 1.0):
        self.file_path = file_path
        self.callback = callback
        self.poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_mtime: float = 0

    def start(self):
        if self._running:
            return
        
        self._running = True
        self._last_mtime = self._get_mtime()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _get_mtime(self) -> float:
        try:
            if os.path.exists(self.file_path):
                return os.path.getmtime(self.file_path)
        except Exception:
            pass
        return 0

    def _watch_loop(self):
        while self._running:
            try:
                current_mtime = self._get_mtime()
                
                if current_mtime > self._last_mtime and self._last_mtime > 0:
                    self._last_mtime = current_mtime
                    try:
                        self.callback()
                    except Exception:
                        pass
                elif current_mtime != self._last_mtime:
                    self._last_mtime = current_mtime
                    
            except Exception:
                pass
            
            time.sleep(self.poll_interval)

    def is_running(self) -> bool:
        return self._running

    def trigger_reload(self):
        if self.callback:
            self.callback()
