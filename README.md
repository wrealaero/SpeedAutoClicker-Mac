# SpeedAutoClicker-Mac

An advanced auto-clicker for macOS with precise control over click rate, duty cycle, and more.

## Features

- **Precise Click Rate Control**: Set click intervals in milliseconds with high precision
- **Click Duty Cycle**: Control how long each click is held down
- **Multiple Mouse Buttons**: Support for left, right, and middle mouse buttons
- **Hotkey Support**: Configurable keyboard shortcuts
- **Click Limiting**: Set a specific number of clicks to perform
- **Two Activation Modes**:
  - Toggle Mode: Press once to start, again to stop
  - Hold Mode: Click only while the hotkey is held down
- **Click Counter**: Track how many clicks have been performed
- **Compatible with Intel and Apple Silicon Macs**

## Installation

### Method 1: Using the Virtual Environment (Recommended)

```bash
# Clone the repository
git clone https://github.com/wrealaero/SpeedAutoClicker-Mac.git
cd SpeedAutoClicker-Mac

# Run the installation script
chmod +x install.sh
./install.sh

# Activate the virtual environment
source venv/bin/activate

# Run the autoclicker
python autoclicker.py
```

### Method 2: Direct Installation

```bash
# Clone the repository
git clone https://github.com/wrealaero/SpeedAutoClicker-Mac.git
cd SpeedAutoClicker-Mac

# Install dependencies directly
pip3 install six pynput==1.7.6 pyobjc-framework-Quartz==9.2 pyobjc-core>=9.2 pyobjc-framework-Cocoa>=9.2 pyobjc-framework-ApplicationServices>=9.2

# Run the autoclicker
python3 autoclicker.py
```

## Troubleshooting

### Python Not Found

If you see an error about Python not being found, you need to install Python 3:

```bash
# Check if Python is installed
python3 --version

# If not installed, you can install with Homebrew
brew install python3
```

### Module Not Found Errors

If you encounter "ModuleNotFoundError" for modules like 'six' or 'pynput':

```bash
# Install the missing module
pip3 install six
pip3 install pynput==1.7.6
```

For PyObjC related errors:

```bash
pip3 install pyobjc-core>=9.2 pyobjc-framework-Cocoa>=9.2 pyobjc-framework-Quartz==9.2 pyobjc-framework-ApplicationServices>=9.2
```

### Python Crashes Immediately

If Python crashes when you try to run the script:

1. Make sure you've installed all dependencies correctly
2. Try running with a specific Python version:
   ```bash
   python3.9 autoclicker.py
   ```
3. Check if you have accessibility permissions enabled
4. Try reinstalling the dependencies:
   ```bash
   pip3 install --upgrade --force-reinstall -r requirements.txt
   ```

### Apple Silicon (M1/M2) Mac Issues

If you're using an Apple Silicon Mac and experiencing issues:

1. Make sure you're using Python for Apple Silicon
2. Try installing Rosetta 2 if you're using Intel-based Python:
   ```bash
   softwareupdate --install-rosetta
   ```
3. Reinstall the dependencies with the architecture-specific flag:
   ```bash
   pip3 install --upgrade --force-reinstall -r requirements.txt
   ```

### Accessibility Permissions

If clicking doesn't work, make sure you've granted accessibility permissions:

1. Open System Preferences
2. Go to Security & Privacy > Privacy > Accessibility
3. Add Terminal or Python to the list of allowed apps
4. Restart the application

### Hotkey Setup

To set a hotkey:

1. Click the "Set Hotkey" button
2. Press the key combination you want to use (e.g., Shift+Q)
3. The hotkey will be displayed in the UI
4. Use this hotkey to start/stop clicking based on your selected mode

## Understanding Click Settings

### Click Rate (CPS)
- Set in milliseconds (ms) between clicks
- Lower values = faster clicking
- The equivalent Clicks Per Second (CPS) is displayed

### Click Duty Cycle (CDC)
- Controls how long each click is held down
- Expressed as a percentage of the total click interval
- Example: With 100ms interval and 50% duty cycle:
  - Mouse button is pressed for 50ms
  - Mouse button is released for 50ms
- For games that require precise click timing, adjust this value to match the game's requirements

## Support

If you encounter any issues or have suggestions:
- Join our [Discord Server](https://discord.gg/MxGV8fGzpR)
- DM 5qvx for bugs and issues
