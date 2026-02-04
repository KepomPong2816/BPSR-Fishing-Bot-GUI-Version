# BPSR Fishing Bot - GUI Version

> **Fork of [hyuse98/BPSR-Fishing-Bot](https://github.com/hyuse98/BPSR-Fishing-Bot)**  
> Modified by [KepomPong2816](https://github.com/KepomPong2816)

---

## 🎣 What's New in V2.0

This GUI version adds significant improvements over the original console-based bot.

### ✨ New Features

| Feature | Description |
|---------|-------------|
| **🖥️ GUI Interface** | Modern PyQt6-based interface with real-time stats and log console |
| **📸 Async Screenshot** | Background thread capture - no more UI freezing |
| **🎯 Adaptive Thresholds** | Detection accuracy auto-adjusts based on match history |
| **🔄 Retry with Backoff** | Failed clicks automatically retry with exponential delays |
| **🖥️ Multi-Monitor** | Select which monitor to capture from settings |
| **📊 Enhanced Stats** | Catch Rate %, Fish/Hour, and detailed session tracking |
| **📝 File Logging** | Save logs to `logs/fishbot.log` with rotation |
| **⚡ Config Hot Reload** | Edit ROIs while bot is running - no restart needed |
| **⏱️ Session Time Limit** | Auto-stop after X minutes |

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `7` | Start Bot |
| `9` | Stop Bot |
| `0` | Open ROI Editor |

---

## ⚙️ Settings

Access via the ⚙️ button in the top-right corner:

- **Monitor Selection** - Choose capture monitor
- **Window Mode** - Auto Detect / Fullscreen / Windowed
- **Target FPS** - 0 = Unlimited
- **Precision** - Detection threshold (0.1 - 1.0)
- **Session Limit** - Auto-stop after X minutes (0 = unlimited)
- **Debug Mode** - Verbose logging
- **File Logging** - Save to file
- **Hotkeys** - Enable/disable keyboard shortcuts

---

## 📊 Dashboard Stats

| Stat | Description |
|------|-------------|
| 🐟 Caught | Total fish caught |
| 💨 Escaped | Fish that got away |
| 📈 Rate% | Success rate percentage |
| ⚡ F/H | Fish per hour rate |
| 🔧 Rods | Rod breaks encountered |
| ⏱️ T/O | Timeout occurrences |

---

## 📁 Files Added/Modified

### New Files
```
src/fishbot/utils/
├── async_capture.py    # Background screenshot capture
├── retry_handler.py    # Retry with exponential backoff
└── config_watcher.py   # Hot reload for config files
```

### Modified Files
```
src/fishbot/config/
├── bot_config.py       # Added: session_limit, async_capture, retry settings
├── detection_config.py # Added: AdaptiveThreshold, auto-create JSON
└── screen_config.py    # Added: multi-monitor support

src/fishbot/core/
├── fishing_bot.py      # Integrated: config watcher, async capture
├── stats.py            # Added: catch_rate, fish_per_hour, session tracking
└── state/impl/
    └── playing_minigame_state.py  # Added: retry handler

src/fishbot/ui/
├── main_window.py      # Enhanced: 6 stat cards, session limit display
├── settings_dialog.py  # Added: monitor, session limit, file logging
├── workers.py          # Added: session timer, extended stats
└── logger.py           # Added: file logging, log levels
```

---

## 🚀 Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run (requires Administrator)
python main_gui.py
```

---

## 📦 Building EXE

```bash
pyinstaller --noconfirm BPSR-Fishing-Bot.spec
```

Output: `dist/Pelanggan Glenn Itu Lagi v4.exe`

---

## ⚠️ Requirements

- Windows 10/11
- Python 3.10+
- Run as **Administrator** (required for keyboard/mouse control)
- Game: Blue Protocol: Star Resonance

---

## 📜 Credits

- Original: [hyuse98/BPSR-Fishing-Bot](https://github.com/hyuse98/BPSR-Fishing-Bot)
- GUI Version: [KepomPong2816](https://github.com/KepomPong2816)
