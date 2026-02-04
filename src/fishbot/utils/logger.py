import time
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Callable

_log_callback: Optional[Callable[[str], None]] = None
_file_logger: Optional[logging.Logger] = None
_debug_enabled: bool = False
_file_logging_enabled: bool = False
_log_file_path: str = ""


def set_log_callback(callback: Callable[[str], None]):
    global _log_callback
    _log_callback = callback


def set_debug_mode(enabled: bool):
    global _debug_enabled
    _debug_enabled = enabled


def is_debug_enabled() -> bool:
    return _debug_enabled


def setup_file_logging(log_dir: str = None, max_bytes: int = 5 * 1024 * 1024, backup_count: int = 3):
    global _file_logger, _file_logging_enabled, _log_file_path
    
    if log_dir is None:
        log_dir = os.path.join(os.getcwd(), "logs")
    
    os.makedirs(log_dir, exist_ok=True)
    
    _log_file_path = os.path.join(log_dir, "fishbot.log")
    
    _file_logger = logging.getLogger("fishbot")
    _file_logger.setLevel(logging.DEBUG)
    
    for handler in _file_logger.handlers[:]:
        _file_logger.removeHandler(handler)
    
    file_handler = RotatingFileHandler(
        _log_file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    
    _file_logger.addHandler(file_handler)
    _file_logging_enabled = True
    
    log(f"[LOGGER] File logging enabled: {_log_file_path}")


def disable_file_logging():
    global _file_logger, _file_logging_enabled
    
    if _file_logger:
        for handler in _file_logger.handlers[:]:
            handler.close()
            _file_logger.removeHandler(handler)
    
    _file_logging_enabled = False


def get_log_file_path() -> str:
    return _log_file_path


def log(message: str, level: str = "INFO"):
    timestamp = time.strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    
    print(formatted_message)
    
    if _log_callback is not None:
        try:
            _log_callback(formatted_message)
        except Exception:
            pass
    
    if _file_logging_enabled and _file_logger:
        try:
            level_map = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL
            }
            log_level = level_map.get(level.upper(), logging.INFO)
            _file_logger.log(log_level, message)
        except Exception:
            pass


def debug(message: str):
    if _debug_enabled:
        log(f"[DEBUG] {message}", "DEBUG")


def info(message: str):
    log(message, "INFO")


def warning(message: str):
    log(f"[WARNING] {message}", "WARNING")


def error(message: str):
    log(f"[ERROR] {message}", "ERROR")