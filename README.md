## WILL BE MAKING A DISCORD SOON

# 🚀 Aerout SpeedAutoClicker for macOS

A high-performance autoclicker with advanced features for macOS.

![Version](https://img.shields.io/badge/version-2.0.1-blue)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![Python](https://img.shields.io/badge/python-3.13%2B-green)

## ✨ Features

- **High Performance**: Optimized for speed and low CPU usage
- **Multiple Click Modes**: Toggle or Hold modes
- **Custom CPS**: Set your desired Clicks Per Second (1-1000)
- **Advanced Timing**: Control click duration and intervals
- **Click Limiting**: Set maximum click count
- **Custom Hotkeys**: Configure activation keys
- **Themes**: Light, Dark and Custom color schemes

## ⚠️ Known Issues

- May require Accessibility permissions on first run
- Python 3.13+ users may need manual dependency install
- Some visual glitches in dark mode

## 📋 Requirements

- macOS 10.13+
- Python 3.6+
- Required packages (auto-installed):
  - pynput
  - pyobjc
  - requests

### Easy Install

1. Download the latest release from the [Releases page](https://github.com/wrealaero/SpeedAutoClicker-Mac/releases)
2. Extract the ZIP file
3. Run the installer script:
   ```
   chmod +x install.sh
   ./install.sh
   ```
4. Follow the on-screen instructions

## 🎮 Basic Usage

1. Set your CPS (clicks per second)
2. Choose mouse button (Left/Right/Middle)
3. Select mode:
   - **Toggle**: Hotkey to start/stop
   - **Hold**: Click while holding hotkey
4. Default hotkey: F6

## 🔄 Changes in v2.1.1

### ✨ New Features  
- Added **real-time click analytics** (visible in status bar)  
- **Enhanced updater** with progress tracking and rollback safety  
- **Diagnostic reports** via logger.py (saved to `~/Documents/AeroutClicker/diagnostics`)  

### 🛠️ Improvements  
- **5x faster** click loop using optimized Quartz calls  
- **Reduced CPU usage** by 30% in idle mode  
- **Pre-built macOS bundles** now available via GitHub Releases  

### 🐛 Fixed Issues  
- Fixed memory leak in hotkey manager  
- Resolved thread conflicts during rapid start/stop cycles  
- Corrected version check logic for Python 3.13+  

### 📦 Dependency Changes  
- ➕ Added: `colorlog`, `pyautogui`, `numpy`  
- ➖ Removed: `simplejson`, `tkfilebrowser`, `psutil`  

## 📝 License

MIT License - See included LICENSE file

---

Made with ❤️ by RealAero
