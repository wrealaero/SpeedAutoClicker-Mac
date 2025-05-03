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
- **Automatic Updates**: Get the latest features and fixes automatically
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

## Usage Guide

### Setting Up Your First Auto-Click

1. **Launch the application**: Run `python3 autoclicker.py`
2. **Set your click interval**: Enter the time in milliseconds between clicks
3. **Choose a mouse button**: Select left, right, or middle mouse button
4. **Configure a hotkey**: Click "Set Hotkey" and press your desired key combination
5. **Select an activation mode**:
   - Toggle Mode: Press hotkey once to start, again to stop
   - Hold Mode: Clicking happens only while hotkey is held down
6. **Start clicking**: Press your configured hotkey or click the "Start" button

### Advanced Options

- **Click Duty Cycle**: Adjust how long each click is held down (as a percentage)
- **Click Limit**: Enable to set a maximum number of clicks to perform
- **CPS Display**: Shows the equivalent Clicks Per Second for your interval setting

## Troubleshooting

### Common Issues and Solutions

#### Python Version Issues
- **Error**: "ImportError: No module named 'tkinter'"
  - **Solution**: Install tkinter for your Python version:
    ```bash
    # For Intel Macs
    brew install python-tk
    
    # For Apple Silicon Macs
    arch -arm64 brew install python-tk
    ```

- **Error**: "ModuleNotFoundError: No module named 'pynput'"
  - **Solution**: Install the missing module:
    ```bash
    pip3 install pynput==1.7.6
    ```

- **Error**: "ModuleNotFoundError: No module named 'Quartz'"
  - **Solution**: Install the required PyObjC modules:
    ```bash
    pip3 install pyobjc-framework-Quartz==9.2 pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-ApplicationServices
    ```

#### Application Crashes
- **Issue**: Python crashes immediately when running the script
  - **Solution 1**: Try running with a specific Python version:
    ```bash
    python3.9 autoclicker.py
    ```
  - **Solution 2**: Reinstall dependencies:
    ```bash
    pip3 uninstall -y pynput pyobjc-framework-Quartz pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-ApplicationServices
    pip3 install -r requirements.txt
    ```

#### Clicking Not Working
- **Issue**: The application runs but doesn't perform clicks
  - **Solution**: Grant accessibility permissions:
    1. Open System Preferences
    2. Go to Security & Privacy > Privacy > Accessibility
    3. Click the lock icon to make changes
    4. Add Terminal or Python to the list of allowed apps
    5. Restart the application

- **Issue**: Clicks are inconsistent or laggy
  - **Solution**: Adjust the duty cycle to a lower value (try 20-30%)

#### M1/M2/M3 Mac Specific Issues
- **Issue**: "ImportError: dlopen failed" errors on Apple Silicon
  - **Solution**: Install Python and dependencies using Rosetta:
    ```bash
    arch -x86_64 pip3 install -r requirements.txt
    arch -x86_64 python3 autoclicker.py
    ```

- **Issue**: "Cannot load PyObjC" errors
  - **Solution**: Install a compatible version of PyObjC:
    ```bash
    pip3 install pyobjc==9.2
    ```

#### Installation Issues
- **Issue**: "Permission denied" when running install.sh
  - **Solution**: Make the script executable:
    ```bash
    chmod +x install.sh
    ```

- **Issue**: Virtual environment creation fails
  - **Solution**: Install venv module and try again:
    ```bash
    pip3 install virtualenv
    python3 -m virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

### Checking Your Python Installation

To check if Python is installed and which version you have:
```bash
python3 --version
```

If Python is not installed, you can install it using Homebrew:
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

Or download the official installer from [python.org](https://www.python.org/downloads/).

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

## Development

### Building from Source

If you want to modify the code or contribute to development:

1. Fork the repository
2. Make your changes
3. Test thoroughly on different macOS versions if possible
4. Submit a pull request with a detailed description of your changes

### Project Structure

- `autoclicker.py` - Main application file
- `updater.py` - Handles automatic updates
- `install.sh` - Installation script
- `requirements.txt` - Python dependencies

## Support

If you encounter any issues or have suggestions:
- Join our [Discord Server](https://discord.gg/MxGV8fGzpR)
- Open an issue on [GitHub](https://github.com/wrealaero/SpeedAutoClicker-Mac/issues)
- DM 5qvx for bugs and issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors and testers (Lighting, Cretz, etc.)
- Special thanks to the pynput and PyObjC projects for making this possible - cause with these holy i wuld have been COOKED - all the tuts and shi
