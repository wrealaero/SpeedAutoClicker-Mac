# SpeedAutoClicker for macOS

An advanced auto-clicker for macOS with precise control over click rate, duty cycle, and more. Works on both Intel and Apple Silicon Macs.

## Features

- **Precise Click Rate Control**: Set click intervals in milliseconds with high precision
- **Click Duty Cycle**: Control how long each click is held down
- **Multiple Mouse Buttons**: Support for left, right, and middle mouse buttons
- **Hotkey Support**: Configurable keyboard shortcuts
- **Click Limiting**: Set a specific number of clicks to perform
- **Two Activation Modes**:
  - Toggle Mode: Press once to start, again to stop
  - Hold Mode: Click only while the hotkey is held down
- **Cross-Platform**: Works on both Intel and Apple Silicon Macs

## Installation

### Check Your Python Version

To check if you have Python installed and which version:

```bash
python3 --version
```

If Python is not installed or the version is below 3.6, you'll need to install/update Python.

### Method 1: Using the Installation Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/wrealaero/SpeedAutoClicker-Mac.git
cd SpeedAutoClicker-Mac

# Run the installation script
chmod +x install.sh
./install.sh

# The script will create a launcher that you can use:
./speedautoclicker
```

### Method 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/wrealaero/SpeedAutoClicker-Mac.git
cd SpeedAutoClicker-Mac

# Install dependencies directly
pip3 install -r requirements.txt

# Run the autoclicker
python3 autoclicker.py
```

## Troubleshooting

### Python Installation Issues

If you don't have Python installed:

1. Visit https://www.python.org/downloads/ and download the latest version for macOS
2. Or install using Homebrew: `brew install python`

### Module Not Found Errors

If you encounter "ModuleNotFoundError" for modules like 'pynput' or 'Quartz':

```bash
# Try installing the missing module
pip3 install pynput pyobjc-framework-Quartz

# If that doesn't work, try installing dependencies one by one
pip3 install six
pip3 install pynput==1.7.6
pip3 install pyobjc-core
pip3 install pyobjc-framework-Cocoa
pip3 install pyobjc-framework-ApplicationServices
pip3 install pyobjc-framework-Quartz
```

### Accessibility Permissions

If clicking doesn't work or the app crashes immediately:

1. Open System Preferences
2. Go to Security & Privacy > Privacy > Accessibility
3. Click the lock icon to make changes (enter your password)
4. Add Terminal or Python to the list of allowed apps
5. Restart the application

You can check if you have the right permissions by running:

```bash
# This will attempt to get your mouse position
python3 -c "from Quartz.CoreGraphics import CGEventCreate, CGEventGetLocation; print(CGEventGetLocation(CGEventCreate(None)))"
```

If it shows coordinates, permissions are working.

### App Crashes on Launch

If the app crashes immediately:

1. Try running from Terminal to see error messages:
   ```bash
   cd /path/to/SpeedAutoClicker-Mac
   python3 autoclicker.py
   ```

2. Make sure you have the correct Python version (3.6+)

3. Try reinstalling the dependencies:
   ```bash
   pip3 uninstall -y pynput pyobjc-framework-Quartz pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-ApplicationServices
   pip3 install -r requirements.txt
   ```

### Apple Silicon (M1/M2) Specific Issues

If you're using an Apple Silicon Mac and experiencing issues:

1. Make sure you're using Python for Apple Silicon
2. Try installing Rosetta 2 if you're using Intel-based Python:
   ```bash
   softwareupdate --install-rosetta
   ```

3. Install dependencies with arch flag:
   ```bash
   arch -arm64 pip3 install -r requirements.txt
   ```

### Hotkey Setup

To set a hotkey:

1. Click the "Set Hotkey" button
2. Press the key combination you want to use (e.g., Shift+Q)
3. The hotkey will be displayed in the UI
4. Use this hotkey to start/stop clicking based on your selected mode

If hotkeys don't work, try using simple key combinations (like a single function key).

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
- For games that need longer click duration, try increasing this value

## Support

If you encounter any issues or have suggestions:
- Join our [Discord Server](https://discord.gg/MxGV8fGzpR)
- DM 5qvx for bugs and issues
