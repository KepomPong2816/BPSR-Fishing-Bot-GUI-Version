import pywinctl as pwc

class ScreenConfig:
    def __init__(self, detection_config=None, window_mode: str = 'Auto Detect', 
                 custom_width: int = 1920, custom_height: int = 1080):
        self.window_title = "Blue Protocol: Star Resonance"
        self.monitor_x = 0
        self.monitor_y = 0
        self.monitor_width = 1920
        self.monitor_height = 1080
        self._detection_config = detection_config
        self._window_mode = window_mode
        self._custom_width = custom_width
        self._custom_height = custom_height

        self._apply_window_mode()

    def _apply_window_mode(self):
        if self._window_mode == 'Auto Detect':
            self._detect_window()
        elif self._window_mode == 'Fullscreen':
            self._use_fullscreen()
        elif self._window_mode == 'Windowed':
            self._use_custom_resolution()
    
    def _use_fullscreen(self):
        self.monitor_x = 0
        self.monitor_y = 0
        self.monitor_width = 1920
        self.monitor_height = 1080
        print(f"[SCREEN] Fullscreen mode: {self.monitor_width}x{self.monitor_height}")
        
        if self._detection_config:
            self._detection_config.update_resolution(self.monitor_width, self.monitor_height)
    
    def _use_custom_resolution(self):
        self.monitor_x = 0
        self.monitor_y = 0
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
                
                break 
        else:
            print("[SCREEN] Window not found. Using defaults (1920x1080).")
            if self._detection_config:
                self._detection_config.update_resolution(self.monitor_width, self.monitor_height)

    def refresh_window_position(self):
        self._apply_window_mode()
        return (self.monitor_x, self.monitor_y, self.monitor_width, self.monitor_height)
