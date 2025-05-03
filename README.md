# SpeedAutoClicker for macOS

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![Python](https://img.shields.io/badge/python-3.6%2B-green)

A powerful, feature-rich auto-clicker for macOS with precise control over click timing, duty cycle, and more.

## Features

- **High-Performance Clicking**: Achieve click rates up to 100 clicks per second
- **Adjustable Click Interval**: Fine-tune the time between clicks (in milliseconds)
- **Duty Cycle Control**: Adjust how long each click is held down
- **Multiple Mouse Buttons**: Support for left, right, and middle mouse buttons
- **Custom Hotkeys**: Set your own keyboard shortcuts to start/stop clicking
- **Toggle or Hold Mode**: Choose between toggle (press once to start, again to stop) or hold (click only while key is held) modes
- **Click Limiting**: Set a maximum number of clicks to perform
- **Auto-Updates**: Built-in updater to keep your software current
- **Diagnostics Tool**: Troubleshoot system compatibility issues

## Requirements

- macOS 10.12 or later
- Python 3.6 or later
- Administrative privileges (for installation)

## Installation

### Method 1: Easy Install (Recommended)

1. Download the latest release from the [Releases page](https://github.com/wrealaero/SpeedAutoClicker-Mac/releases)
2. Extract the ZIP file
3. Open Terminal and navigate to the extracted folder
4. Run the installation script:

```bash
./install.sh
```

### Method 2: Manual Installation

1. Ensure you have Python 3.6+ installed
2. Clone or download this repository
3. Open Terminal and navigate to the project folder
4. Install the required dependencies:

```bash
pip3 install -r requirements.txt
```

5. Make the script executable:

```bash
chmod +x autoclicker.py
```

## Usage

### Starting the Application

After installation, you can run the application using:

```bash
./autoclicker.py
```

Or if you used the virtual environment during installation:

```bash
source venv/bin/activate
./autoclicker.py
```

### First-Time Setup

1. When you first run the application, you may be prompted to grant accessibility permissions
2. Go to System Preferences → Security & Privacy → Privacy → Accessibility
3. Add the Terminal application (or Python if running directly) to the list of allowed apps

### Basic Configuration

1. **Click Interval**: Set the time between clicks in milliseconds (lower = faster)
2. **Duty Cycle**: Adjust how long each click is held down (as a percentage of the interval)
3. **Mouse Button**: Select which mouse button to click (left, right, or middle)
4. **Activation Mode**: Choose between toggle mode or hold mode
5. **Hotkey**: Set your preferred keyboard shortcut to start/stop clicking

### Advanced Features

- **Click Limiting**: Enable to automatically stop after a specific number of clicks
- **Diagnostics**: Run the built-in diagnostics tool to check system compatibility
- **Updates**: Use the "Check for Updates" button to ensure you have the latest version

## Troubleshooting

### Hotkey Not Working

1. Make sure Terminal/Python has accessibility permissions
2. Try setting a different hotkey combination
3. Restart the application
4. Run the diagnostics tool to check for system issues

### Mouse Cursor Freezing

1. Lower the click rate (increase the interval)
2. Adjust the duty cycle to a value between 20-80%
3. Make sure you're not running other mouse-controlling software simultaneously

### Application Not Starting

1. Verify Python is installed correctly: `python3 --version`
2. Check that all dependencies are installed: `pip3 list`
3. Try reinstalling using the installation script

## Known Issues

- Some applications may have built-in protection against auto-clickers
- Performance may vary depending on system specifications
- May not work in certain games that use custom input methods

## Updates

The application includes a built-in updater. To check for updates:

1. Click the "Check for Updates" button in the application
2. If an update is available, follow the prompts to install it

Alternatively, you can manually update by downloading the latest release and running the installation script again.

## Support

If you encounter any issues or have questions:

- Join our [Discord server](https://discord.gg/MxGV8fGzpR)
- Open an issue on GitHub
- DM 5qvx for direct support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Thanks to all contributors and testers - (Lighting, Cretz, etc.)
- Special thanks to the pynput and pyobjc projects
