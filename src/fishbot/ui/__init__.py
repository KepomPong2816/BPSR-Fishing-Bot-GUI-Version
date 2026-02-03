"""
UI package for BPSR Fishing Bot.
Contains the PyQt6 GUI components.
"""

from .main_window import MainWindow, run_app
from .workers import BotWorker, TimerWorker
from .styles import MAIN_STYLESHEET, get_status_style, COLORS

__all__ = [
    'MainWindow',
    'run_app',
    'BotWorker',
    'TimerWorker',
    'MAIN_STYLESHEET',
    'get_status_style',
    'COLORS',
]
