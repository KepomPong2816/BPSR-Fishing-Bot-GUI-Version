from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QMetaObject, Qt, Q_ARG


class BotWorker(QThread):
    state_changed = pyqtSignal(str)
    log_message = pyqtSignal(str)
    stats_updated = pyqtSignal(dict)
    bot_stopped = pyqtSignal()
    bot_ready = pyqtSignal()
    bot_error = pyqtSignal(str)
    session_limit_reached = pyqtSignal()
    
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.bot = None
        self._is_running = False
        self._is_paused = False
        self._should_stop = False
        self._session_start_time = 0
        self._session_time_limit = settings.get('session_time_limit', 0)
        
    def run(self):
        import time
        
        try:
            self.log_message.emit("[GUI] ⏳ Initializing bot...")
            self._init_bot()
            self.log_message.emit("[GUI] ✅ Bot initialized!")
            self.bot_ready.emit()
            
            self._is_running = True
            self._session_start_time = time.time()
            self.bot.start()
            self.bot.stats.start_session()
            
            if self._session_time_limit > 0:
                self.log_message.emit(f"[GUI] ⏱️ Session limit: {self._session_time_limit} minutes")
            
            while self._is_running and not self._should_stop and not self.bot.is_stopped():
                if self._session_time_limit > 0:
                    elapsed_minutes = (time.time() - self._session_start_time) / 60
                    if elapsed_minutes >= self._session_time_limit:
                        self.log_message.emit(f"[GUI] ⏱️ Session time limit reached ({self._session_time_limit} min)")
                        self.session_limit_reached.emit()
                        break
                
                if not self._is_paused:
                    try:
                        self.bot.update()
                        
                        if self.bot.state_machine.current_state_name:
                            self.state_changed.emit(self.bot.state_machine.current_state_name.name)
                        
                        self.stats_updated.emit(self.bot.stats.get_extended_stats())
                        
                    except Exception as e:
                        self.log_message.emit(f"[ERROR] Bot update failed: {e}")
                else:
                    self.msleep(100)
            
            if self.bot:
                self.bot.stop()
                
        except Exception as e:
            self.bot_error.emit(str(e))
            self.log_message.emit(f"[ERROR] ❌ Bot initialization failed: {e}")
        finally:
            self._cleanup()
            self.bot_stopped.emit()
    
    def _init_bot(self):
        from src.fishbot.core.fishing_bot import FishingBot
        from src.fishbot.utils.logger import setup_file_logging, set_debug_mode
        
        window_mode = self.settings.get('window_mode', 'Auto Detect')
        custom_width = self.settings.get('custom_width', 1920)
        custom_height = self.settings.get('custom_height', 1080)
        
        if self.settings.get('file_logging_enabled', False):
            setup_file_logging()
        
        set_debug_mode(self.settings.get('debug_mode', False))
        
        self.bot = FishingBot(
            window_mode=window_mode,
            custom_width=custom_width,
            custom_height=custom_height
        )
        
        self.bot.config.bot.target_fps = self.settings.get('target_fps', 60)
        self.bot.config.bot.detection.precision = self.settings.get('precision', 0.65)
        self.bot.config.bot.quick_finish_enabled = self.settings.get('quick_finish', False)
        self.bot.config.bot.debug_mode = self.settings.get('debug_mode', False)
        self.bot.config.bot.selected_monitor = self.settings.get('selected_monitor', 0)
        
        if self.bot.config.bot.target_fps > 0:
            self.bot.target_delay = 1.0 / self.bot.config.bot.target_fps
        else:
            self.bot.target_delay = 0

    def _cleanup(self):
        if self.bot and hasattr(self.bot, 'detector'):
            try:
                self.bot.detector.cleanup()
            except Exception:
                pass
    
    def get_remaining_time(self) -> int:
        if self._session_time_limit <= 0:
            return -1
        
        import time
        elapsed = (time.time() - self._session_start_time) / 60
        remaining = max(0, self._session_time_limit - elapsed)
        return int(remaining * 60)
    
    def get_session_time_limit(self) -> int:
        return self._session_time_limit
    
    def pause(self):
        self._is_paused = True
        self.state_changed.emit('PAUSED')
    
    def resume(self):
        self._is_paused = False
    
    def stop(self):
        self._should_stop = True
        self._is_running = False
        self._is_paused = True
        
    def is_paused(self):
        return self._is_paused


class TimerWorker(QTimer):
    time_updated = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._seconds = 0
        self.timeout.connect(self._tick)
        
    def _tick(self):
        self._seconds += 1
        self.time_updated.emit(self._format_time())
    
    def _format_time(self) -> str:
        hours = self._seconds // 3600
        minutes = (self._seconds % 3600) // 60
        seconds = self._seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def start_timer(self):
        self._seconds = 0
        self.start(1000)
    
    def resume_timer(self):
        self.start(1000)
    
    def stop_timer(self):
        self.stop()
    
    def reset(self):
        self._seconds = 0
        self.time_updated.emit("00:00:00")
    
    def reset_timer(self):
        self.reset()
    
    def get_elapsed(self) -> int:
        return self._seconds
