import sys
import multiprocessing

if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

import os
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
os.environ['QT_SCALE_FACTOR'] = '1'

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QGuiApplication
from PyQt6.QtCore import Qt, QRect, QPoint

from src.fishbot.config.detection_config import DetectionConfig


class InteractiveROIEditor(QWidget):
    def __init__(self, monitor_index: int = 0):
        super().__init__()
        
        screens = QGuiApplication.screens()
        if monitor_index < len(screens):
            screen = screens[monitor_index]
        else:
            screen = screens[0] if screens else None
        
        if screen:
            geom = screen.geometry()
            self.screen_width = geom.width()
            self.screen_height = geom.height()
            self.screen_left = geom.x()
            self.screen_top = geom.y()
        else:
            self.screen_width = 1920
            self.screen_height = 1080
            self.screen_left = 0
            self.screen_top = 0
        
        self.detection_config = DetectionConfig()
        self.detection_config.update_resolution(self.screen_width, self.screen_height)
        
        self.cached_user_rois = self.detection_config.load_user_rois()
        
        self.roi_rects = {}
        self._load_all_rois()
        
        self.selected_roi = None
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.drag_start_pos = QPoint()
        self.initial_rect = QRect()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        if screen:
            self.setGeometry(screen.geometry())
            self.setScreen(screen)
        
        print(f"[ROI EDITOR] Editor opened on Monitor {monitor_index + 1}")
        print(f"[ROI EDITOR] Resolution: {self.screen_width}x{self.screen_height}")
        print("[ROI EDITOR] Click any ROI to select, drag to move, resize from edges.")
        print("[ROI EDITOR] Press ESC to close and save all changes.")
        
    def _load_all_rois(self):
        for name, roi in self.detection_config.rois.items():
            if roi:
                x, y, w, h = roi
                self.roi_rects[name] = QRect(int(x), int(y), int(w), int(h))
                
    def _save_roi(self, name):
        if name not in self.roi_rects:
            return
            
        rect = self.roi_rects[name]
        x = rect.x()
        y = rect.y()
        w = rect.width()
        h = rect.height()
        
        self.cached_user_rois[name] = [x, y, w, h]
        self.detection_config.save_user_rois(self.cached_user_rois)
        self.detection_config.rois[name] = (x, y, w, h)
        
        print(f"[ROI EDITOR] 💾 Saved '{name}': [{x}, {y}, {w}, {h}]")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(20, 40, f"📐 ROI Editor [{self.screen_width}x{self.screen_height}]")
        painter.setFont(QFont("Arial", 12))
        painter.drawText(20, 65, f"Config: user_rois_{self.screen_width}x{self.screen_height}.json | Press ESC to close")
        
        if not self.roi_rects:
            painter.setPen(QColor(255, 200, 0))
            painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            painter.drawText(20, 120, "⚠️ No ROIs loaded")
        
        for name, rect in self.roi_rects.items():
            is_selected = name == self.selected_roi
            
            if is_selected:
                pen = QPen(QColor(0, 255, 0), 3, Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.setBrush(QColor(0, 255, 0, 60))
                painter.drawRect(rect)
                
                painter.setBrush(QColor(255, 255, 255))
                painter.setPen(Qt.PenStyle.NoPen)
                handle_size = 10
                handles = [
                    rect.topLeft(), rect.topRight(), 
                    rect.bottomLeft(), rect.bottomRight(),
                    QPoint(rect.center().x(), rect.top()),
                    QPoint(rect.center().x(), rect.bottom()),
                    QPoint(rect.left(), rect.center().y()),
                    QPoint(rect.right(), rect.center().y())
                ]
                for p in handles:
                    painter.drawEllipse(p, handle_size // 2, handle_size // 2)
                
                painter.setPen(QColor(0, 255, 0))
                painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                label = f"{name} ({rect.width()}x{rect.height()})"
                painter.drawText(rect.x(), rect.y() - 10, label)
            else:
                pen = QPen(QColor(0, 200, 255), 2, Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.setBrush(QColor(0, 200, 255, 40))
                painter.drawRect(rect)
                
                painter.setPen(QColor(0, 200, 255))
                painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                painter.drawText(rect.x() + 5, rect.y() + 18, name)

    def _get_roi_at_pos(self, pos):
        for name, rect in self.roi_rects.items():
            if rect.contains(pos):
                return name
        return None
        
    def _get_resize_edge(self, pos):
        if not self.selected_roi or self.selected_roi not in self.roi_rects:
            return None
            
        r = self.roi_rects[self.selected_roi]
        margin = 15
        
        if (pos - r.topLeft()).manhattanLength() < margin: return 'tl'
        if (pos - r.topRight()).manhattanLength() < margin: return 'tr'
        if (pos - r.bottomLeft()).manhattanLength() < margin: return 'bl'
        if (pos - r.bottomRight()).manhattanLength() < margin: return 'br'
        if abs(pos.y() - r.top()) < margin and r.left() < pos.x() < r.right(): return 'top'
        if abs(pos.y() - r.bottom()) < margin and r.left() < pos.x() < r.right(): return 'bottom'
        if abs(pos.x() - r.left()) < margin and r.top() < pos.y() < r.bottom(): return 'left'
        if abs(pos.x() - r.right()) < margin and r.top() < pos.y() < r.bottom(): return 'right'
        
        return None

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
            
        pos = event.pos()
        
        edge = self._get_resize_edge(pos)
        if edge and self.selected_roi:
            self.resizing = True
            self.resize_edge = edge
            self.drag_start_pos = pos
            self.initial_rect = QRect(self.roi_rects[self.selected_roi])
            return
            
        if self.selected_roi and self.roi_rects[self.selected_roi].contains(pos):
            self.dragging = True
            self.drag_start_pos = pos
            self.initial_rect = QRect(self.roi_rects[self.selected_roi])
            return
            
        clicked_roi = self._get_roi_at_pos(pos)
        if clicked_roi:
            self.selected_roi = clicked_roi
            self.dragging = True
            self.drag_start_pos = pos
            self.initial_rect = QRect(self.roi_rects[self.selected_roi])
            self.update()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        
        edge = self._get_resize_edge(pos)
        if edge in ['tl', 'br']:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge in ['tr', 'bl']:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edge in ['top', 'bottom']:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif edge in ['left', 'right']:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif self.selected_roi and self.roi_rects.get(self.selected_roi, QRect()).contains(pos):
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        elif self._get_roi_at_pos(pos):
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        if self.dragging and self.selected_roi:
            delta = pos - self.drag_start_pos
            self.roi_rects[self.selected_roi] = self.initial_rect.translated(delta)
            self.update()
            
        elif self.resizing and self.selected_roi:
            r = QRect(self.initial_rect)
            delta = pos - self.drag_start_pos
            
            if 'left' in self.resize_edge:
                r.setLeft(r.left() + delta.x())
            if 'right' in self.resize_edge:
                r.setRight(r.right() + delta.x())
            if 'top' in self.resize_edge:
                r.setTop(r.top() + delta.y())
            if 'bottom' in self.resize_edge:
                r.setBottom(r.bottom() + delta.y())
                
            self.roi_rects[self.selected_roi] = r.normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if (self.dragging or self.resizing) and self.selected_roi:
            self._save_roi(self.selected_roi)
            
        self.dragging = False
        self.resizing = False
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            print("[ROI EDITOR] Editor closed.")
            self.close()
            QApplication.instance().quit()


def main(monitor_index: int = 0):
    print("Starting Interactive ROI Editor...")
    print("Click any ROI to select, drag to move, resize from edges.")
    print("Press ESC to close.")
    
    app = QApplication(sys.argv)
    editor = InteractiveROIEditor(monitor_index=monitor_index)
    editor.showFullScreen()
    sys.exit(app.exec())


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()