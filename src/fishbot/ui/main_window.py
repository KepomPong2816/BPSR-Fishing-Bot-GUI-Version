import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QGroupBox, QGridLayout, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot

from .styles import MAIN_STYLESHEET, get_status_style, COLORS
from .workers import BotWorker, TimerWorker
from .settings_dialog import SettingsDialog
from ..utils.logger import set_log_callback
from ..utils.roi_visualizer import main as show_roi_editor
from ..utils.path import resource_path
import multiprocessing


class StatCard(QFrame):
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 6, 8, 6)
        
        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.text_label = QLabel(f"{icon} {label}")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label)
        
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: {COLORS['bg_light']};
                border-radius: 6px;
                border: 1px solid {COLORS['border']};
            }}
            QFrame#statCard QLabel {{
                font-size: 12px;
                color: {COLORS['text_primary']};
            }}
        """)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {COLORS['accent']};
            }}
        """)
        self.text_label.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: {COLORS['text_secondary']};
            }}
        """)
    
    def set_value(self, value):
        if isinstance(value, float):
            self.value_label.setText(f"{value:.1f}")
        else:
            self.value_label.setText(str(value))


class MainWindow(QMainWindow):    
    MAX_LOG_LINES = 500
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.timer = TimerWorker(self)
        self._is_paused = False
        self._user_scrolling = False
        self._log_line_count = 0
        self._hotkeys_enabled = True
        self._settings = self._default_settings()
        self.visualizer_process = None
        
        self._setup_ui()
        self._connect_signals()
        self._setup_hotkeys()
        
        set_log_callback(self._safe_append_log)
        
        self._check_admin()
    
    def _default_settings(self) -> dict:
        return {
            'selected_monitor': 0,
            'window_mode': 'Auto Detect',
            'custom_width': 1920,
            'custom_height': 1080,
            'target_fps': 60,
            'precision': 0.65,
            'session_time_limit': 0,
            'quick_finish': False,
            'debug_mode': False,
            'file_logging_enabled': False,
            'hotkeys_enabled': True,
        }
        
    def _setup_ui(self):
        self.setWindowTitle("iBal the Finisher V 2.0")
        self.setMinimumSize(480, 600)
        self.resize(500, 650)
        self.setStyleSheet(MAIN_STYLESHEET)
        
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)
        
        title_label = QLabel("Untuk Lord Firzha V 2.0")
        title_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['accent']};")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        button_style = f"""
            QPushButton {{
                min-width: 30px;
                max-width: 35px;
                padding: 2px 4px;
                font-size: 10px;
                background-color: {COLORS['bg_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']};
            }}
        """

        self.always_on_top_btn = QPushButton("📌")
        self.always_on_top_btn.setFixedSize(35, 22)
        self.always_on_top_btn.setToolTip("Toggle Always on Top")
        self.always_on_top_btn.setCheckable(True)
        self.always_on_top_btn.setStyleSheet(f"""
            QPushButton {{
                min-width: 30px;
                max-width: 35px;
                padding: 2px 4px;
                font-size: 10px;
                background-color: {COLORS['bg_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            QPushButton:checked {{
                background-color: {COLORS['accent']};
                color: white;
            }}
        """)
        self.always_on_top_btn.clicked.connect(self._on_always_on_top_changed)
        header_layout.addWidget(self.always_on_top_btn)
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(35, 22)
        self.settings_btn.setToolTip("Open Settings")
        self.settings_btn.setStyleSheet(button_style)
        self.settings_btn.clicked.connect(self._open_settings)
        header_layout.addWidget(self.settings_btn)

        self.roi_btn = QPushButton("HUD")
        self.roi_btn.setFixedSize(35, 22)
        self.roi_btn.setToolTip("Open ROI Editor")
        self.roi_btn.setStyleSheet(button_style)
        self.roi_btn.clicked.connect(self._open_roi_editor)
        header_layout.addWidget(self.roi_btn)

        self.bg_btn = QPushButton("🖼️ BG")
        self.bg_btn.setFixedSize(45, 22)
        self.bg_btn.setToolTip("Toggle Background")
        self.bg_btn.setCheckable(True)
        self.bg_btn.setStyleSheet(button_style)
        self.bg_btn.toggled.connect(self._toggle_background)
        header_layout.addWidget(self.bg_btn)
        
        main_layout.addLayout(header_layout)
        
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(8)
        
        self.status_label = QLabel("READY")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(get_status_style('READY'))
        status_layout.addWidget(self.status_label)
        
        timer_row = QHBoxLayout()
        timer_row.setSpacing(15)
        
        self.timer_label = QLabel("⏱️ 00:00:00")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']};")
        timer_row.addWidget(self.timer_label)
        
        self.session_limit_label = QLabel("")
        self.session_limit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_limit_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        timer_row.addWidget(self.session_limit_label)
        
        status_layout.addLayout(timer_row)
        
        stats_layout = QGridLayout()
        stats_layout.setSpacing(6)
        
        self.stat_cards = {}
        
        self.stat_cards['fish_caught'] = StatCard("🐟", "Caught")
        stats_layout.addWidget(self.stat_cards['fish_caught'], 0, 0)
        
        self.stat_cards['fish_escaped'] = StatCard("💨", "Escaped")
        stats_layout.addWidget(self.stat_cards['fish_escaped'], 0, 1)
        
        self.stat_cards['catch_rate'] = StatCard("📈", "Rate%")
        stats_layout.addWidget(self.stat_cards['catch_rate'], 0, 2)
        
        self.stat_cards['fish_per_hour'] = StatCard("⚡", "F/H")
        stats_layout.addWidget(self.stat_cards['fish_per_hour'], 1, 0)
        
        self.stat_cards['rod_breaks'] = StatCard("🔧", "Rods")
        stats_layout.addWidget(self.stat_cards['rod_breaks'], 1, 1)
        
        self.stat_cards['timeouts'] = StatCard("⏱️", "T/O")
        stats_layout.addWidget(self.stat_cards['timeouts'], 1, 2)
        
        status_layout.addLayout(stats_layout)
        
        main_layout.addWidget(status_group)
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        self.start_button = QPushButton("▶ START")
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self._on_start_clicked)
        controls_layout.addWidget(self.start_button)
        
        controls_layout.addSpacing(15)
        
        self.stop_button = QPushButton("⏹ STOP")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        controls_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(controls_layout)
        
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(8, 10, 8, 8)
        log_layout.setSpacing(5)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMinimumHeight(150)
        self.log_console.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }}
        """)
        self.log_console.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)
        log_layout.addWidget(self.log_console)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setMaximumWidth(80)
        clear_btn.clicked.connect(self._clear_log)
        log_layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addWidget(log_group, stretch=1)
        
        footer = QLabel(
            '⌨️ 7=Start | 9=Stop | 0=ROI Editor | '
            f'<a href="https://github.com/KepomPong2816" style="color: {COLORS["accent"]};">KepomPong2816</a>'
        )
        footer.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setOpenExternalLinks(True)
        main_layout.addWidget(footer)
        
    def _connect_signals(self):
        self.timer.time_updated.connect(self._on_timer_updated)
    
    def _check_admin(self):
        import ctypes
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            is_admin = False
        
        if not is_admin:
            self._append_log("[GUI] ⚠️ NOT RUNNING AS ADMINISTRATOR!")
            self._append_log("[GUI] ⚠️ Mouse/keyboard control may not work.")
            self._append_log("[GUI] ⚠️ Run python main.py / main_gui.py ON Terminal with 'Run as Administrator'.")
    
    def _setup_hotkeys(self):
        try:
            import keyboard
            
            keyboard.on_press_key('7', lambda _: self._on_hotkey_start())
            keyboard.on_press_key('9', lambda _: self._on_hotkey_stop())
            keyboard.on_press_key('0', lambda _: self._on_hotkey_visualizer())
            
            self._append_log("[GUI] Hotkeys: 7=Start, 9=Stop, 0=Visual")
        except ImportError:
            self._append_log("[GUI] Keyboard library not found")
            self._hotkeys_enabled = False
    
    def _on_hotkey_start(self):
        if not self._hotkeys_enabled:
            return
        from PyQt6.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(self.start_button, "click", Qt.ConnectionType.QueuedConnection)
    
    def _on_hotkey_stop(self):
        if not self._hotkeys_enabled:
            return
        from PyQt6.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(self.stop_button, "click", Qt.ConnectionType.QueuedConnection)
    
    def _on_hotkey_visualizer(self):
        if not self._hotkeys_enabled:
            return
        
        from PyQt6.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(self, "_open_roi_editor", Qt.ConnectionType.QueuedConnection)
    
    def _open_settings(self):
        dialog = SettingsDialog(self, self._settings)
        if dialog.exec():
            old_hotkeys = self._settings.get('hotkeys_enabled', True)
            self._settings = dialog.get_settings()
            new_hotkeys = self._settings.get('hotkeys_enabled', True)
            
            if old_hotkeys != new_hotkeys:
                self._hotkeys_enabled = new_hotkeys
                status = "enabled" if new_hotkeys else "disabled"
                self._append_log(f"[GUI] ⌨️ Hotkeys {status}")
            
            self._append_log("[GUI] Settings saved")
            
    def _open_roi_editor(self):
        monitor_index = self._settings.get('selected_monitor', 0)
        self._append_log(f"[GUI] Opening HUD Editor on Monitor {monitor_index + 1}...")
        
        p = multiprocessing.Process(target=show_roi_editor, args=(monitor_index,), daemon=True)
        p.start()
    
    def _toggle_background(self, checked: bool):
        if checked:
            bg_path = resource_path('maskot2.png')
            
            bg_path_css = bg_path.replace('\\', '/')
            
            if os.path.exists(bg_path):
                transparent_style = """
                    QWidget#centralWidget {
                        background-color: rgba(0, 0, 0, 80);
                    }
                    QGroupBox {
                        background-color: transparent;
                        border: 1px solid rgba(255, 255, 255, 50);
                    }
                    QFrame#statCard {
                        background-color: rgba(0, 0, 0, 40);
                        border: 1px solid rgba(255, 255, 255, 50);
                    }
                    QTextEdit {
                        background-color: rgba(0, 0, 0, 40);
                        border: 1px solid rgba(255, 255, 255, 50);
                    }
                    QLabel#statusLabel {
                        background-color: rgba(0, 0, 0, 40);
                    }
                """
                
                self.setStyleSheet(f"""
                    QMainWindow {{
                        background-image: url({bg_path_css});
                        background-position: center;
                        background-repeat: no-repeat;
                    }}
                    {MAIN_STYLESHEET}
                    {transparent_style}
                """)
            else:
                self._append_log("[GUI] maskot2.png not found!")
                self.bg_btn.setChecked(False)
        else:
            self.setStyleSheet(MAIN_STYLESHEET)
    
    @pyqtSlot()
    def _on_always_on_top_changed(self):
        if self.always_on_top_btn.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        
    @pyqtSlot()
    def _on_start_clicked(self):
        if self.worker is None:
            self.worker = BotWorker(self._settings)
            self.worker.state_changed.connect(self._on_state_changed)
            self.worker.stats_updated.connect(self._on_stats_updated)
            self.worker.log_message.connect(self._append_log)
            self.worker.bot_stopped.connect(self._on_bot_stopped)
            self.worker.bot_error.connect(self._on_bot_error)
            self.worker.session_limit_reached.connect(self._on_session_limit_reached)
            
            self.worker.start()
            self.timer.start_timer()
            
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.settings_btn.setEnabled(False)
            
            session_limit = self._settings.get('session_time_limit', 0)
            if session_limit > 0:
                self.session_limit_label.setText(f"⏳ Limit: {session_limit}m")
            else:
                self.session_limit_label.setText("")
            
            self._append_log("[GUI] 🚀 Bot started!")
            
        elif self.worker.is_paused():
            self._is_paused = False
            self.worker.resume()
            self._append_log("[GUI] ▶️ Bot resumed!")
            self.start_button.setEnabled(False)
            self.timer.resume_timer()
    

    @pyqtSlot()
    def _on_stop_clicked(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait(5000)
            self.worker = None
            self._append_log("[GUI] ⏹️ Bot stopped!")

        self.status_label.setText("STOPPED")
        self.status_label.setStyleSheet(get_status_style('STOPPED'))
        self._reset_ui(stopped=True)
    
    @pyqtSlot()
    def _on_session_limit_reached(self):
        self._append_log("[GUI] ⏱️ Session limit reached! Auto-stopping...")
        QMessageBox.information(self, "Session Limit", "Session time limit reached. Bot has stopped.")
        self._on_stop_clicked()
    
    @pyqtSlot(str)
    def _on_state_changed(self, state: str):
        if self._is_paused and state != 'PAUSED':
            return
        self.status_label.setText(state)
        self.status_label.setStyleSheet(get_status_style(state))
    
    @pyqtSlot(dict)
    def _on_stats_updated(self, stats: dict):
        for key, value in stats.items():
            if key in self.stat_cards:
                self.stat_cards[key].set_value(value)
    
    @pyqtSlot()
    def _on_bot_stopped(self):
        self._reset_ui()
    
    @pyqtSlot(str)
    def _on_bot_error(self, error: str):
        self._append_log(f"[ERROR] ❌ {error}")
        QMessageBox.critical(self, "Error", f"Bot error: {error}")
        self._reset_ui()
    
    @pyqtSlot(str)
    def _on_timer_updated(self, time_str: str):
        self.timer_label.setText(f"⏱️ {time_str}")
    
    def _on_scroll_changed(self, value: int):
        scrollbar = self.log_console.verticalScrollBar()
        self._user_scrolling = (value < scrollbar.maximum() - 10)
    
    @pyqtSlot(str)
    def _safe_append_log(self, message: str):
        from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(
            self, "_append_log",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, message)
        )
    
    @pyqtSlot(str)
    def _append_log(self, message: str):
        if self._log_line_count >= self.MAX_LOG_LINES:
            cursor = self.log_console.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, 50)
            cursor.removeSelectedText()
            self._log_line_count -= 50
        
        self.log_console.append(message)
        self._log_line_count += 1
        
        if not self._is_paused and not self._user_scrolling:
            scrollbar = self.log_console.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def _clear_log(self):
        self.log_console.clear()
        self._log_line_count = 0
        
    def _reset_ui(self, stopped: bool = False):
        self._is_paused = False
        self._user_scrolling = False
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.settings_btn.setEnabled(True)
        
        self.timer.stop_timer()
        self.timer.reset_timer()
        self.timer_label.setText("⏱️ 00:00:00")
        self.session_limit_label.setText("")
        
        for key in self.stat_cards:
            self.stat_cards[key].set_value(0)
        
        if not stopped:
            self.status_label.setText("READY")
            self.status_label.setStyleSheet(get_status_style('READY'))

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.worker.wait(1000)
            
        if self.visualizer_process and self.visualizer_process.is_alive():
            self.visualizer_process.terminate()
            
        event.accept()

def run_app():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
