import os
from PyQt6.QtWidgets import QSplashScreen, QApplication, QProgressBar, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter

from ..utils.path import resource_path

class SplashScreen(QSplashScreen):    
    def __init__(self):
        pixmap = QPixmap(450, 350)
        pixmap.fill(QColor(255, 255, 255))
        
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        self._setup_ui()
        self._loading_steps = []
        self._current_step = 0
        
    def _setup_ui(self):
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 450, 350)
        self.container.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(self.container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        self.title_label = QLabel("FantasyNET")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #1a1a2e;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("BPSR Bot Fishing")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: #e94560;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(self.subtitle_label)
        
        mascot_layout = QHBoxLayout()
        mascot_layout.setSpacing(20)
        mascot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.mascot_left = QLabel()
        self.mascot_left.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        mascot_layout.addWidget(self.mascot_left)
        
        self.mascot_right = QLabel()
        self.mascot_right.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        mascot_layout.addWidget(self.mascot_right)
        
        self._load_mascots()
        
        layout.addLayout(mascot_layout)
        
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #e0e0e0;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #e94560;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        self.credits_label = QLabel("Credit: hyuse98 | Modified: KepomPong2816")
        self.credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.credits_label.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 9px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(self.credits_label)
        
    def _load_mascots(self):
        def load_image(filename):
            path = resource_path(filename)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return pixmap.scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
            return None

        pix_left = load_image('maskot.png')
        if pix_left:
            self.mascot_left.setPixmap(pix_left)
        else:
            self.mascot_left.setText("🐟")
            self.mascot_left.setStyleSheet("font-size: 40px;")

        pix_right = load_image('maskot2.png')
        if pix_right:
            self.mascot_right.setPixmap(pix_right)
        else:
            self.mascot_right.setText("🎣")
            self.mascot_right.setStyleSheet("font-size: 40px;")
        
    def set_status(self, message: str, progress: int = None):
        self.status_label.setText(message)
        if progress is not None:
            self.progress_bar.setValue(progress)
        QApplication.processEvents()
        
    def set_progress(self, value: int):
        self.progress_bar.setValue(value)
        QApplication.processEvents()
