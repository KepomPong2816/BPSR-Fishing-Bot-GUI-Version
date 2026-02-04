import sys
import os

if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
os.environ['QT_SCALE_FACTOR'] = '1'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_admin():
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def main():
    if not check_admin():
        print("WARNING: Not running as Administrator!")
        print("Mouse/keyboard control may not work properly.")
        print("Please run as Administrator for full functionality.\n")
    
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    from src.fishbot.ui.splash_screen import SplashScreen
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    
    splash.set_status("Initializing application...", 5)
    app.processEvents()
    
    splash.set_status("Loading styles...", 15)
    from src.fishbot.ui.styles import MAIN_STYLESHEET
    app.processEvents()
    
    splash.set_status("Loading numerical libraries...", 25)
    import numpy
    app.processEvents()
    
    splash.set_status("Loading image processing (OpenCV)...", 40)
    import cv2
    app.processEvents()
    
    splash.set_status("Loading screen capture module...", 55)
    import mss
    app.processEvents()
    
    splash.set_status("Loading input controllers...", 70)
    import pyautogui
    import keyboard
    app.processEvents()
    
    splash.set_status("Preparing main window...", 85)
    from src.fishbot.ui.main_window import MainWindow
    app.processEvents()
    
    splash.set_status("Starting application...", 100)
    window = MainWindow()
    app.processEvents()
    
    import time
    time.sleep(0.15)
    
    splash.finish(window)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
