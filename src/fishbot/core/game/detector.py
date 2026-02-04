import cv2 as cv
import numpy as np
from typing import Optional

from src.fishbot.utils.logger import log

try:
    import mss
except ImportError:
    log("[ERROR] ❌ MSS library not found! Install with: pip install mss")
    log("[ERROR] The bot cannot run without MSS.")
    exit(1)


class Detector:
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080
    
    def __init__(self, config, use_async: bool = True):
        self.unified_config = config
        self.detection_config = config.bot.detection
        self.screen_config = config.bot.screen

        self.templates = self._load_templates()
        self.scaled_templates = {}
        self.sct = None
        self.monitor = {
            'left': self.screen_config.monitor_x,
            'top': self.screen_config.monitor_y,
            'width': self.screen_config.monitor_width,
            'height': self.screen_config.monitor_height
        }
        
        self._scale_templates()
        
        self._use_async = use_async
        self._async_capture = None
        
        if self._use_async:
            self._init_async_capture()

    def _init_async_capture(self):
        try:
            from src.fishbot.utils.async_capture import AsyncScreenCapture
            self._async_capture = AsyncScreenCapture(
                monitor=self.monitor,
                fps=self.unified_config.bot.target_fps or 30
            )
            self._async_capture.start()
            log("[INFO] ✅ Async screen capture enabled")
        except Exception as e:
            log(f"[WARNING] Async capture failed, using sync: {e}")
            self._use_async = False
            self._async_capture = None

    def _scale_templates(self):
        scale_x = self.screen_config.monitor_width / self.BASE_WIDTH
        scale_y = self.screen_config.monitor_height / self.BASE_HEIGHT
        
        # Check if scaling is needed (strict tolerance)
        if abs(scale_x - 1.0) < 0.01 and abs(scale_y - 1.0) < 0.01:
            self.scaled_templates = self.templates.copy()
            log(f"[INFO] Templates at base resolution (1920x1080)")
            return
        
        log(f"[INFO] Scaling templates for {self.screen_config.monitor_width}x{self.screen_config.monitor_height} (scale: {scale_x:.3f}x, {scale_y:.3f}y)")
        
        for name, (template_img, mask) in self.templates.items():
            # Use separate scaling factors for width and height
            new_w = int(template_img.shape[1] * scale_x)
            new_h = int(template_img.shape[0] * scale_y)
            
            # Safety check for very small dimensions
            if new_w < 4 or new_h < 4:
                log(f"[WARNING] Template '{name}' too small after scaling ({new_w}x{new_h}), using original.")
                self.scaled_templates[name] = (template_img, mask)
                continue
            
            # Use INTER_AREA for shrinking (better quality), INTER_LINEAR for enlarging
            interpolation = cv.INTER_AREA if (scale_x < 1.0 or scale_y < 1.0) else cv.INTER_LINEAR
            
            scaled_template = cv.resize(template_img, (new_w, new_h), interpolation=interpolation)
            
            scaled_mask = None
            if mask is not None:
                scaled_mask = cv.resize(mask, (new_w, new_h), interpolation=interpolation)
            
            self.scaled_templates[name] = (scaled_template, scaled_mask)
        
        log(f"[INFO] ✅ Scaled {len(self.scaled_templates)} templates")

    def update_monitor(self, monitor: dict):
        self.monitor = monitor
        if self._async_capture:
            self._async_capture.update_monitor(monitor)

    def cleanup(self):
        if self._async_capture:
            self._async_capture.stop()
            self._async_capture = None
        if self.sct:
            self.sct.close()
            self.sct = None

    def _load_templates(self):
        loaded = {}
        log("[INFO] Loading templates...")
        for name in self.detection_config.templates:
            path = self.unified_config.get_template_path(name)
            if not (path and path.exists()):
                log(f"[INFO] ❌ {name} - not found at '{path}'")
                continue

            img = cv.imread(str(path), cv.IMREAD_UNCHANGED)
            template_img, mask = None, None

            if img.shape[2] == 4:
                log(f"[INFO] ✅ {name} (with transparency mask)")
                mask = img[:, :, 3]
                template_img = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
            else:
                log(f"[INFO] ✅ {name}")
                template_img = img
            
            loaded[name] = (template_img, mask)
        return loaded
    
    def _generate_concentric_square_pixels(self, center_x, center_y, max_radius):
        for r in range(1, max_radius + 1):
            for x in range(center_x - r, center_x + r + 1):
                yield x, center_y - r
            for x in range(center_x - r, center_x + r + 1):
                yield x, center_y + r
            for y in range(center_y - r + 1, center_y + r):
                yield center_x - r, y
            for y in range(center_y - r + 1, center_y + r):
                yield center_x + r, y

    def capture_screen(self) -> Optional[np.ndarray]:
        if self._use_async and self._async_capture:
            frame = self._async_capture.get_latest_frame()
            if frame is not None:
                return frame
        
        if self.sct is None:
            self.sct = mss.mss()
            log(f"[INFO] ✅ MSS initialized. Monitor: {self.monitor}")

        screenshot = self.sct.grab(self.monitor)
        img = np.array(screenshot)
        
        if img is None or img.size == 0:
            log(f"[ERROR] Captured empty screen! Monitor: {self.monitor}")
            return None
            
        try:
            return cv.cvtColor(img, cv.COLOR_BGRA2BGR)
        except cv.error as e:
            log(f"[ERROR] cvtColor failed: {e}. Shape: {img.shape}")
            return None

    def _check_xy(self, search_area, x, y, template_data, template_img, template_name, debug):
        confidence, location = self._perform_match(search_area, template_data)

        if confidence is None:
            return None
        
        precision = self.detection_config.get_precision_for_template(template_name)
        is_match = confidence >= precision

        if debug and confidence >= .3:
            status = 'MATCH' if is_match else 'NO MATCH'
            log(f"[DEBUG] [{template_name}] at ({x}, {y}) Confidence: {confidence:.2%} (required: {precision:.0%}) -> {status}")

        if is_match:
            self.detection_config.record_detection_result(template_name, True, confidence)
            return self._calculate_center(location, template_img.shape[:2], (x, y))
        else:
            if confidence >= 0.3:
                self.detection_config.record_detection_result(template_name, False, confidence)

        return None

    def _get_search_area(self, screen, template_name, radius, debug):
        template_data = self.scaled_templates.get(template_name, self.templates.get(template_name))
        if not template_data:
            return None
            
        template_img, _ = template_data

        roi_config = self.detection_config.rois.get(template_name)
        if isinstance(roi_config, str):
            roi = self.detection_config.rois.get(roi_config)
        else:
            roi = roi_config

        if not roi:
            return screen, (0, 0)

        x, y, w, h = roi
        screen_h, screen_w = screen.shape[:2]
        x = max(0, min(x, screen_w - 1))
        y = max(0, min(y, screen_h - 1))
        w = min(w, screen_w - x)
        h = min(h, screen_h - y)

        if w > 0 and h > 0:
            result = self._check_xy(screen[y:y + h, x:x + w], x, y, template_data, template_img, template_name, debug)

            if result != None:
                return result
            
            if radius > 0:
                concentric_coords = self._generate_concentric_square_pixels(x, y, radius)

                for pixel in list(concentric_coords):
                    x, y = pixel

                    result = self._check_xy(screen[y:y + h, x:x + w], x, y, template_data, template_img, template_name, debug)

                    if result != None:
                        return result

        return None

    def _perform_match(self, search_area, template_data):
        template_img, mask = template_data

        search_gray = cv.cvtColor(search_area, cv.COLOR_BGR2GRAY)
        template_gray = cv.cvtColor(template_img, cv.COLOR_BGR2GRAY)

        if search_gray.shape[0] < template_gray.shape[0] or search_gray.shape[1] < template_gray.shape[1]:
            return None, None

        result = cv.matchTemplate(search_gray, template_gray, cv.TM_CCOEFF_NORMED, mask=mask)
        _, confidence, _, location = cv.minMaxLoc(result)
        return confidence, location

    def _calculate_center(self, location, template_shape, offset):
        h_t, w_t = template_shape
        offset_x, offset_y = offset
        return (
            location[0] + w_t // 2 + offset_x + self.screen_config.monitor_x,
            location[1] + h_t // 2 + offset_y + self.screen_config.monitor_y
        )

    def find(self, screen, template_name, radius = 0, debug=False):
        if template_name not in self.templates:
            log(f"[INFO] ❌ Template '{template_name}' was not loaded.")
            return None
        
        return self._get_search_area(screen, template_name, radius, debug)