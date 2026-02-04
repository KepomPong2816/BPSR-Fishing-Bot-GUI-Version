import threading
import time
from typing import Optional
import numpy as np

try:
    import mss
    import cv2 as cv
except ImportError:
    pass


class AsyncScreenCapture:
    def __init__(self, monitor: dict, fps: int = 30):
        self.monitor = monitor
        self.fps = fps
        self._frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._sct = None
        self._frame_interval = 1.0 / fps if fps > 0 else 0.033

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        if self._sct:
            self._sct.close()
            self._sct = None

    def update_monitor(self, monitor: dict):
        with self._lock:
            self.monitor = monitor

    def get_latest_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            if self._frame is not None:
                return self._frame.copy()
            return None

    def _capture_loop(self):
        self._sct = mss.mss()
        
        while self._running:
            try:
                start_time = time.perf_counter()
                
                with self._lock:
                    current_monitor = self.monitor.copy()
                
                screenshot = self._sct.grab(current_monitor)
                img = np.array(screenshot)
                
                if img is not None and img.size > 0:
                    frame = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
                    with self._lock:
                        self._frame = frame
                
                elapsed = time.perf_counter() - start_time
                sleep_time = max(0, self._frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception:
                time.sleep(0.1)

    def is_running(self) -> bool:
        return self._running
