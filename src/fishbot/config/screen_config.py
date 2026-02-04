import pywinctl as pwc
from typing import List, Dict, Optional

try:
    import mss
except ImportError:
    mss = None


def get_available_monitors() -> List[Dict]:
    monitors = []
    
    if mss:
        try:
            with mss.mss() as sct:
                for i, mon in enumerate(sct.monitors):
                    if i == 0:
                        continue
                    monitors.append({
                        'index': i - 1,
                        'name': f"Monitor {i}",
                        'left': mon['left'],
                        'top': mon['top'],
                        'width': mon['width'],
                        'height': mon['height']
                    })
        except Exception as e:
            print(f"[SCREEN] Failed to enumerate monitors: {e}")
    
    if not monitors:
        monitors.append({
            'index': 0,
            'name': 'Primary Monitor',
            'left': 0,
            'top': 0,
            'width': 1920,
            'height': 1080
        })
    
    return monitors


class ScreenConfig:
    def __init__(self, detection_config=None, window_mode: str = 'Auto Detect', 
                 custom_width: int = 1920, custom_height: int = 1080,
                 selected_monitor: int = 0):
        self.window_title = "Blue Protocol: Star Resonance"
        self.monitor_x = 0
        self.monitor_y = 0
        self.monitor_width = 1920
        self.monitor_height = 1080
        self._detection_config = detection_config
        self._window_mode = window_mode
        self._custom_width = custom_width
        self._custom_height = custom_height
        self._selected_monitor = selected_monitor
        
        self._available_monitors = get_available_monitors()

        self._apply_window_mode()

    def get_available_monitors(self) -> List[Dict]:
        self._available_monitors = get_available_monitors()
        return self._available_monitors

    def set_selected_monitor(self, index: int):
        self._selected_monitor = index
        self._apply_window_mode()

    def get_selected_monitor(self) -> int:
        return self._selected_monitor

    def get_monitor_offset(self) -> tuple:
        if self._selected_monitor < len(self._available_monitors):
            mon = self._available_monitors[self._selected_monitor]
            return mon['left'], mon['top']
        return 0, 0

    def get_monitor_resolution(self) -> tuple:
        if self._selected_monitor < len(self._available_monitors):
            mon = self._available_monitors[self._selected_monitor]
            return mon['width'], mon['height']
        return 1920, 1080

    def _apply_window_mode(self):
        if self._window_mode == 'Auto Detect':
            self._detect_window()
        elif self._window_mode == 'Fullscreen':
            self._use_fullscreen()
        elif self._window_mode == 'Windowed':
            self._use_custom_resolution()
    
    def _use_fullscreen(self):
        if self._selected_monitor < len(self._available_monitors):
            mon = self._available_monitors[self._selected_monitor]
            self.monitor_x = mon['left']
            self.monitor_y = mon['top']
            self.monitor_width = mon['width']
            self.monitor_height = mon['height']
        else:
            self.monitor_x = 0
            self.monitor_y = 0
            self.monitor_width = 1920
            self.monitor_height = 1080
            
        print(f"[SCREEN] Fullscreen mode on Monitor {self._selected_monitor + 1}: {self.monitor_width}x{self.monitor_height}")
        
        if self._detection_config:
            self._detection_config.update_resolution(self.monitor_width, self.monitor_height)
    
    def _use_custom_resolution(self):
        offset_x, offset_y = self.get_monitor_offset()
        self.monitor_x = offset_x
        self.monitor_y = offset_y
        self.monitor_width = self._custom_width
        self.monitor_height = self._custom_height
        
        windows = pwc.getAllWindows()
        for window in windows:
            if "Blue Protocol" in window.title:
                (self.monitor_x, self.monitor_y) = window.topleft
                if self.monitor_x > 0 or self.monitor_y > 0:
                    self.monitor_y = self.monitor_y + 32
                    self.monitor_x = self.monitor_x + 8
                print(f"[SCREEN] Window found at ({self.monitor_x}, {self.monitor_y})")
                break
        
        print(f"[SCREEN] Custom resolution: {self.monitor_width}x{self.monitor_height}")
        
        if self._detection_config:
            self._detection_config.update_resolution(self.monitor_width, self.monitor_height)

    def _detect_window(self):
        windows = pwc.getAllWindows()
        
        mon_x, mon_y = self.get_monitor_offset()
        mon_w, mon_h = self.get_monitor_resolution()

        for window in windows:
            if "Blue Protocol: Star Resonance" in window.title:
                (self.monitor_x, self.monitor_y) = window.topleft
                (self.monitor_width, self.monitor_height) = window.size
                
                if self.monitor_x > 0 or self.monitor_y > 0:
                    self.monitor_y = self.monitor_y + 32
                    self.monitor_x = self.monitor_x + 8
                    self.monitor_width = self.monitor_width - 16
                    self.monitor_height = self.monitor_height - 39

                    print(f"[SCREEN] Game window detected at ({self.monitor_x}, {self.monitor_y})")
                    print(f"[SCREEN] Window size: {self.monitor_width}x{self.monitor_height}")
                else:
                    print(f"[SCREEN] Fullscreen mode detected: {self.monitor_width}x{self.monitor_height}")
                
                if self._detection_config:
                    self._detection_config.update_resolution(self.monitor_width, self.monitor_height)
                
                return
        
        self.monitor_x = mon_x
        self.monitor_y = mon_y
        self.monitor_width = mon_w
        self.monitor_height = mon_h
        
        print(f"[SCREEN] Window not found. Using Monitor {self._selected_monitor + 1} resolution: {mon_w}x{mon_h}")
        
        if self._detection_config:
            self._detection_config.update_resolution(self.monitor_width, self.monitor_height)

    def refresh_window_position(self):
        self._apply_window_mode()
        return (self.monitor_x, self.monitor_y, self.monitor_width, self.monitor_height)

    def get_monitor_dict(self) -> dict:
        return {
            'left': self.monitor_x,
            'top': self.monitor_y,
            'width': self.monitor_width,
            'height': self.monitor_height
        }
