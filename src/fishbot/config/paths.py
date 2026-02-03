import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    INTERNAL_BASE = Path(sys._MEIPASS)
    EXTERNAL_BASE = Path(sys.executable).parent
else:
    INTERNAL_BASE = Path(__file__).parent.parent.parent.parent
    EXTERNAL_BASE = INTERNAL_BASE

PROJECT_ROOT = INTERNAL_BASE
SRC_DIR = PROJECT_ROOT / "src"
FISHBOT_DIR = SRC_DIR / "fishbot"
PACKAGE_ROOT = FISHBOT_DIR
ASSETS_DIR = FISHBOT_DIR / "assets"
ASSETS_PATH = ASSETS_DIR
TEMPLATES_PATH = ASSETS_DIR / "templates"

USER_ROIS_PATH = EXTERNAL_BASE / "user_rois.json"

def get_user_rois_path(width: int, height: int) -> Path:
    """Get per-resolution user ROIs file path."""
    return EXTERNAL_BASE / f"user_rois_{width}x{height}.json"