COLORS = {
    'bg_dark': '#1a1a2e',
    'bg_medium': '#16213e',
    'bg_light': '#0f3460',
    'accent': '#e94560',
    'accent_hover': '#ff6b6b',
    'success': '#00d9a5',
    'warning': '#ffc107',
    'error': '#ff4757',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'border': '#2d3748',
}

MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['bg_dark']};
}}

QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 12px;
}}

QGroupBox {{
    background-color: {COLORS['bg_medium']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding: 15px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {COLORS['accent']};
    font-size: 13px;
}}

QPushButton {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text_primary']};
    border: none;
    border-radius: 6px;
    padding: 12px 24px;
    font-size: 13px;
    font-weight: bold;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {COLORS['accent']};
}}

QPushButton:pressed {{
    background-color: {COLORS['accent_hover']};
}}

QPushButton:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['text_secondary']};
}}

QPushButton#startButton {{
    background-color: {COLORS['success']};
    color: {COLORS['bg_dark']};
}}

QPushButton#startButton:hover {{
    background-color: #00f5b8;
}}

QPushButton#pauseButton {{
    background-color: {COLORS['warning']};
    color: {COLORS['bg_dark']};
}}

QPushButton#pauseButton:hover {{
    background-color: #ffd43b;
}}

QPushButton#stopButton {{
    background-color: {COLORS['error']};
}}

QPushButton#stopButton:hover {{
    background-color: #ff6b7a;
}}

QLabel {{
    color: {COLORS['text_primary']};
    background-color: transparent;
}}

QLabel#statusLabel {{
    font-size: 18px;
    font-weight: bold;
    padding: 15px;
    background-color: {COLORS['bg_medium']};
    border-radius: 8px;
    border: 2px solid {COLORS['accent']};
}}

QLabel#timerLabel {{
    font-size: 14px;
    color: {COLORS['text_secondary']};
}}

QLabel#statValue {{
    font-size: 20px;
    font-weight: bold;
    color: {COLORS['success']};
}}

QLabel#statLabel {{
    font-size: 11px;
    color: {COLORS['text_secondary']};
}}

QTextEdit {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
}}

QTextEdit:focus {{
    border-color: {COLORS['accent']};
}}

QScrollBar:vertical {{
    background-color: {COLORS['bg_medium']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['bg_light']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['accent']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px 12px;
    min-width: 100px;
    min-height: 28px;
    font-size: 13px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['accent']};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: {COLORS['bg_light']};
    border: none;
    width: 24px;
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {COLORS['accent']};
}}

QComboBox {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px 12px;
    min-width: 120px;
    min-height: 28px;
    font-size: 13px;
}}

QCheckBox {{
    spacing: 8px;
    color: {COLORS['text_primary']};
    background-color: transparent;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    background-color: {COLORS['bg_medium']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['accent']};
}}

QComboBox:focus {{
    border-color: {COLORS['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent']};
    border: 1px solid {COLORS['border']};
    font-size: 13px;
}}

QTabWidget::pane {{
    background-color: {COLORS['bg_medium']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text_secondary']};
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['accent']};
    color: {COLORS['text_primary']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLORS['border']};
}}
"""

STATE_COLORS = {
    'STARTING': '#ffc107',
    'CHECKING_ROD': '#17a2b8',
    'CASTING_BAIT': '#6f42c1',
    'WAITING_FOR_BITE': '#007bff',
    'PLAYING_MINIGAME': '#28a745',
    'FINISHING': '#20c997',
    'PAUSED': '#6c757d',
    'STOPPED': '#dc3545',
    'READY': '#00d9a5',
}

def get_status_style(state: str) -> str:
    color = STATE_COLORS.get(state, COLORS['accent'])
    return f"""
        font-size: 18px;
        font-weight: bold;
        padding: 15px;
        background-color: {COLORS['bg_medium']};
        border-radius: 8px;
        border: 2px solid {color};
        color: {color};
    """
