import pywinctl as pwc

class ScreenConfig:
    def __init__(self):
        self.window_title = "Blue Protocol: Star Resonance"
        self.monitor_x = 0
        self.monitor_y = 0
        self.monitor_width = 1920
        self.monitor_height = 1080

        windows = pwc.getAllWindows()

        for window in windows:
            if "Blue Protocol" in window.title:
                (self.monitor_x, self.monitor_y) = window.topleft
                (self.monitor_width, self.monitor_height) = window.size
                

                if self.monitor_x > 0 or self.monitor_y > 0:
                    self.monitor_y = self.monitor_y + 32 # windowed mode so adjust down for top bar
                    self.monitor_x = self.monitor_x + 8
                    self.monitor_width = self.monitor_width - 16
                    self.monitor_height = self.monitor_height - 39

                    print(f"game window detected at ({self.monitor_x}, {self.monitor_y})")
                    print(f"width and height ({self.monitor_width}, {self.monitor_height})")
                break 
        else:
            print("Window not found. using defaults.")
