import time

_log_callback = None


def set_log_callback(callback):
    global _log_callback
    _log_callback = callback

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    
    if _log_callback is not None:
        try:
            _log_callback(formatted_message)
        except Exception:
            pass