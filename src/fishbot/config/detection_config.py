from .paths import TEMPLATES_PATH, get_user_rois_path, USER_ROIS_PATH

class DetectionConfig:
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080
    
    def __init__(self):
        self.precision = 0.65

        self.templates_path = str(TEMPLATES_PATH)

        self.templates = {
            "fishing_spot_btn": "fishing_spot_btn.png",
            "broken_rod": "broken_rod.png",
            "new_rod": "new_rod.png",
            "reg_rod": "reg_pole.png",
            "sturdy_rod": "sturdy_pole.png",
            "flex_rod": "flex_pole.png",
            "exclamation": "exclamation.png",
            "left_arrow": "left_arrow.png",
            "right_arrow": "right_arrow.png",
            "failure": "fish_escaped.png",
            "success": "success.png",
            "continue": "continue.png",
            "level_check": "level_check.png",
            "connect_server": "connect.png"
        }

        self._base_rois = {
            "fishing_spot_btn": (1400, 540, 121, 55),
            "broken_rod": (1635, 982, 250, 63),
            "reg_rod": (1638, 985, 210, 33),
            "sturdy_rod": (1637, 984, 194, 37),
            "flex_rod": (1637, 984, 204, 36),
            "new_rod": (1624, 563, 185, 65),
            "exclamation": (929, 438, 52, 142),
            "left_arrow": (740, 490, 220, 100),
            "right_arrow": (960, 490, 220, 100),
            "failure": (973, 630, 702, 101),
            "success": (710, 620, 570, 130),
            "continue": (1439, 942, 306, 75),
            "level_check": (1101, 985, 48, 29),
            "connect_server": (1057, 763, 279, 67),
        }
        
        self.rois = self._base_rois.copy()
        
        self._current_width = self.BASE_WIDTH
        self._current_height = self.BASE_HEIGHT
        
        self.user_rois = self.load_user_rois()
        self._apply_user_rois()
    
    def update_resolution(self, width: int, height: int):
        resolution_changed = (width != self._current_width or height != self._current_height)
        
        self._current_width = width
        self._current_height = height
        
        scale_x = width / self.BASE_WIDTH
        scale_y = height / self.BASE_HEIGHT
        
        scaled_rois = {}
        for name, roi in self._base_rois.items():
            if roi is None:
                scaled_rois[name] = None
            else:
                x, y, w, h = roi
                scaled_rois[name] = (
                    int(x * scale_x),
                    int(y * scale_y),
                    int(w * scale_x),
                    int(h * scale_y)
                )
        
        self.rois = scaled_rois
        
        if resolution_changed and (width != self.BASE_WIDTH or height != self.BASE_HEIGHT):
            print(f"[DETECTION] ROIs scaled for {width}x{height} (scale: {scale_x:.2f}x, {scale_y:.2f}y)")
        
        if resolution_changed:
            self.user_rois = self.load_user_rois()
            
        self._apply_user_rois()
        
    def get_scale_info(self) -> tuple:
        scale_x = self._current_width / self.BASE_WIDTH
        scale_y = self._current_height / self.BASE_HEIGHT
        return scale_x, scale_y
    
    def get_current_resolution(self) -> tuple:
        return self._current_width, self._current_height

    def load_user_rois(self) -> dict:
        import json
        import os
        
        rois_path = get_user_rois_path(self._current_width, self._current_height)
        
        if os.path.exists(rois_path):
            try:
                with open(rois_path, 'r') as f:
                    user_rois = json.load(f)
                    print(f"[DETECTION] Loaded {len(user_rois)} custom ROIs for {self._current_width}x{self._current_height}")
                    return user_rois
            except Exception as e:
                print(f"[DETECTION] Failed to load user ROIs: {e}")
                return {}
        
        if os.path.exists(USER_ROIS_PATH):
            try:
                with open(USER_ROIS_PATH, 'r') as f:
                    user_rois = json.load(f)
                    print(f"[DETECTION] Migrating {len(user_rois)} ROIs from legacy file to {self._current_width}x{self._current_height}")
                    self.user_rois = user_rois
                    self.save_user_rois(user_rois)
                    return user_rois
            except Exception as e:
                print(f"[DETECTION] Failed to load legacy ROIs: {e}")
        
        print(f"[DETECTION] No custom ROIs for {self._current_width}x{self._current_height}, using defaults")
        return {}
            
    def save_user_rois(self, rois: dict):
        import json
        import os
        
        rois_path = get_user_rois_path(self._current_width, self._current_height)
        
        try:
            parent_dir = os.path.dirname(rois_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            with open(rois_path, 'w') as f:
                json.dump(rois, f, indent=4)
            print(f"[DETECTION] Custom ROIs saved for {self._current_width}x{self._current_height}")
            
            self.user_rois = rois
            self._apply_user_rois()
            
        except Exception as e:
            print(f"[DETECTION] Failed to save user ROIs: {e}")

    def _apply_user_rois(self):
        if not self.user_rois:
            return
            
        for name, roi in self.user_rois.items():
            if name in self.rois:
                self.rois[name] = tuple(roi)
                print(f"[DETECTION] Applied custom ROI for '{name}': {roi}")