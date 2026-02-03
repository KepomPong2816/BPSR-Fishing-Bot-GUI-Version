from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, 
    QComboBox, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt

from .styles import MAIN_STYLESHEET, COLORS


class SettingsDialog(QDialog):    
    def __init__(self, parent=None, current_settings: dict = None):
        super().__init__(parent)
        self._current_settings = current_settings or {}
        self._setup_ui()
        self._apply_current_settings()
        
    def _setup_ui(self):
        self.setWindowTitle("⚙️ Settings")
        self.setMinimumSize(450, 400)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        window_group = QGroupBox("🖥️ Window Settings")
        window_layout = QGridLayout(window_group)
        window_layout.setSpacing(12)
        
        window_layout.addWidget(QLabel("Window Mode:"), 0, 0)
        self.window_mode_combo = QComboBox()
        self.window_mode_combo.addItems(["Auto Detect", "Fullscreen", "Windowed"])
        self.window_mode_combo.setToolTip(
            "Auto Detect: Automatically detect game window\n"
            "Fullscreen: Use full screen resolution\n"
            "Windowed: Use custom resolution below"
        )
        self.window_mode_combo.currentIndexChanged.connect(self._on_window_mode_changed)
        window_layout.addWidget(self.window_mode_combo, 0, 1)
        
        window_layout.addWidget(QLabel("Width:"), 1, 0)
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(640, 3840)
        self.width_spinbox.setValue(1920)
        self.width_spinbox.setSingleStep(10)
        self.width_spinbox.setEnabled(False)
        window_layout.addWidget(self.width_spinbox, 1, 1)
        
        window_layout.addWidget(QLabel("Height:"), 2, 0)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(480, 2160)
        self.height_spinbox.setValue(1080)
        self.height_spinbox.setSingleStep(10)
        self.height_spinbox.setEnabled(False)
        window_layout.addWidget(self.height_spinbox, 2, 1)
        
        layout.addWidget(window_group)
        
        bot_group = QGroupBox("🤖 Bot Settings")
        bot_layout = QGridLayout(bot_group)
        bot_layout.setSpacing(12)
        
        bot_layout.addWidget(QLabel("Target FPS:"), 0, 0)
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(0, 120)
        self.fps_spinbox.setValue(60)
        self.fps_spinbox.setToolTip("0 = Unlimited")
        bot_layout.addWidget(self.fps_spinbox, 0, 1)
        
        bot_layout.addWidget(QLabel("Precision:"), 1, 0)
        self.precision_spinbox = QDoubleSpinBox()
        self.precision_spinbox.setRange(0.1, 1.0)
        self.precision_spinbox.setSingleStep(0.05)
        self.precision_spinbox.setValue(0.65)
        bot_layout.addWidget(self.precision_spinbox, 1, 1)
        
        self.quick_finish_checkbox = QCheckBox("Quick Finish")
        self.quick_finish_checkbox.setToolTip("Skip the result screen after catching a fish")
        bot_layout.addWidget(self.quick_finish_checkbox, 2, 0, 1, 2)
        
        self.debug_checkbox = QCheckBox("Debug Mode")
        self.debug_checkbox.setToolTip("Show detailed detection logs")
        bot_layout.addWidget(self.debug_checkbox, 3, 0, 1, 2)
        
        layout.addWidget(bot_group)
        
        hotkey_group = QGroupBox("Hotkeys")
        hotkey_layout = QVBoxLayout(hotkey_group)
        
        self.hotkey_checkbox = QCheckBox("Enable Hotkeys")
        self.hotkey_checkbox.setChecked(True)
        self.hotkey_checkbox.setToolTip("Enable keyboard shortcuts: 7=Start, 9=Stop, 0=ROI Editor")
        hotkey_layout.addWidget(self.hotkey_checkbox)
        
        hotkey_info = QLabel("Keys: 7=Start | 9=Stop | 0=ROI Editor")
        hotkey_info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        hotkey_layout.addWidget(hotkey_info)
        
        layout.addWidget(hotkey_group)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("startButton")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("stopButton")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_window_mode_changed(self, index: int):
        is_custom = (index == 2)
        self.width_spinbox.setEnabled(is_custom)
        self.height_spinbox.setEnabled(is_custom)
    
    def _apply_current_settings(self):
        if not self._current_settings:
            return
            
        window_mode = self._current_settings.get('window_mode', 'Auto Detect')
        index = self.window_mode_combo.findText(window_mode)
        if index >= 0:
            self.window_mode_combo.setCurrentIndex(index)
        
        self.width_spinbox.setValue(self._current_settings.get('custom_width', 1920))
        self.height_spinbox.setValue(self._current_settings.get('custom_height', 1080))
        
        self.fps_spinbox.setValue(self._current_settings.get('target_fps', 60))
        self.precision_spinbox.setValue(self._current_settings.get('precision', 0.65))
        self.quick_finish_checkbox.setChecked(self._current_settings.get('quick_finish', False))
        self.debug_checkbox.setChecked(self._current_settings.get('debug_mode', False))
        
        self.hotkey_checkbox.setChecked(self._current_settings.get('hotkeys_enabled', True))
    
    def get_settings(self) -> dict:
        return {
            'window_mode': self.window_mode_combo.currentText(),
            'custom_width': self.width_spinbox.value(),
            'custom_height': self.height_spinbox.value(),
            'target_fps': self.fps_spinbox.value(),
            'precision': self.precision_spinbox.value(),
            'quick_finish': self.quick_finish_checkbox.isChecked(),
            'debug_mode': self.debug_checkbox.isChecked(),
            'hotkeys_enabled': self.hotkey_checkbox.isChecked(),
        }
