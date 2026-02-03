from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSpinBox, QComboBox, QPushButton, QGroupBox,
    QMessageBox
)
from PyQt6.QtCore import Qt

from .styles import MAIN_STYLESHEET, COLORS


class ROIEditorDialog(QDialog):    
    def __init__(self, parent, detection_config, screen_config):
        super().__init__(parent)
        self.detection_config = detection_config
        self.screen_config = screen_config
        
        self.current_rois = self.detection_config.rois.copy()
        
        self.setWindowTitle("ROI Editor (Detection Areas)")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(MAIN_STYLESHEET)
        
        self._setup_ui()
        self._load_selected_roi()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        info = QLabel("Adjust detection areas manually if auto-detection fails.")
        info.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold;")
        layout.addWidget(info)
        
        select_group = QGroupBox("Select Template")
        select_layout = QVBoxLayout(select_group)
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(sorted(self.detection_config.templates.keys()))
        self.template_combo.currentIndexChanged.connect(self._load_selected_roi)
        select_layout.addWidget(self.template_combo)
        
        layout.addWidget(select_group)
        
        editor_group = QGroupBox("Adjust Coordinates")
        grid = QGridLayout(editor_group)
        grid.setSpacing(10)
        
        grid.addWidget(QLabel("X (Left):"), 0, 0)
        self.spin_x = QSpinBox()
        self.spin_x.setRange(0, 3840)
        grid.addWidget(self.spin_x, 0, 1)
        
        grid.addWidget(QLabel("Y (Top):"), 0, 2)
        self.spin_y = QSpinBox()
        self.spin_y.setRange(0, 2160)
        grid.addWidget(self.spin_y, 0, 3)
        
        grid.addWidget(QLabel("Width:"), 1, 0)
        self.spin_w = QSpinBox()
        self.spin_w.setRange(1, 1920)
        grid.addWidget(self.spin_w, 1, 1)
        
        grid.addWidget(QLabel("Height:"), 1, 2)
        self.spin_h = QSpinBox()
        self.spin_h.setRange(1, 1080)
        grid.addWidget(self.spin_h, 1, 3)
        
        layout.addWidget(editor_group)
        
        monitor_info = QLabel(
            f"Current Resolution: {self.screen_config.monitor_width}x{self.screen_config.monitor_height}"
        )
        monitor_info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        layout.addWidget(monitor_info)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Save & Apply")
        apply_btn.setObjectName("startButton")
        apply_btn.clicked.connect(self._save_changes)
        btn_layout.addWidget(apply_btn)
        
        reset_btn = QPushButton("Reset Default")
        reset_btn.clicked.connect(self._reset_current)
        btn_layout.addWidget(reset_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
    def _load_selected_roi(self):
        name = self.template_combo.currentText()
        roi = self.current_rois.get(name)
        
        if roi:
            x, y, w, h = roi
            self.spin_x.setValue(int(x))
            self.spin_y.setValue(int(y))
            self.spin_w.setValue(int(w))
            self.spin_h.setValue(int(h))
            
    def _save_changes(self):
        name = self.template_combo.currentText()
        new_roi = [
            self.spin_x.value(),
            self.spin_y.value(),
            self.spin_w.value(),
            self.spin_h.value()
        ]
        
        user_rois = self.detection_config.load_user_rois()
        user_rois[name] = new_roi
        
        self.detection_config.save_user_rois(user_rois)
        
        self.current_rois[name] = tuple(new_roi)
        
        QMessageBox.information(self, "Saved", f"Custom ROI for '{name}' saved!")
        
    def _reset_current(self):
        name = self.template_combo.currentText()
        
        user_rois = self.detection_config.load_user_rois()
        if name in user_rois:
            del user_rois[name]
            self.detection_config.save_user_rois(user_rois)
            QMessageBox.information(self, "Reset", f"Custom ROI for '{name}' removed. Default scaling will be used.")
            
            w, h = self.screen_config.monitor_width, self.screen_config.monitor_height
            self.detection_config.update_resolution(w, h)
            self.current_rois[name] = self.detection_config.rois[name]
            self._load_selected_roi()
        else:
            QMessageBox.information(self, "Info", "This is already using the default value.")
