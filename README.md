# Aerout SpeedAutoClicker for macOS

A high-performance autoclicker with advanced features, designed specifically for macOS.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **High Performance**: Optimized for speed and reliability
- **Flexible Clicking**: Adjust CPS (clicks per second) from 0.1 to 1000+
- **Multiple Mouse Buttons**: Support for left, right, and middle mouse buttons
- **Advanced Controls**: Customize duty cycle and hold time for precise clicking patterns
- **Hotkey Support**: Configurable keyboard shortcuts to control the autoclicker
- **Click Modes**: Toggle mode and hold mode for different use cases
- **Click Limiting**: Set a maximum number of clicks
- **Configuration Profiles**: Save and load different clicking configurations
- **Customizable UI**: Multiple themes and color options
- **Diagnostic Tools**: Built-in logging and diagnostic reporting

## Installation

### Method 1: Installer Script

1. Download the latest release from the [Releases page](https://github.com/wrealaero/SpeedAutoClicker-Mac/releases)
2. Extract the ZIP file
3. Open Terminal and navigate to the extracted folder
4. Run the installer script:
   ```bash
   ./install.sh
   ```
5. Follow the on-screen instructions

### Method 2: Manual Installation

1. Download the latest release from the [Releases page](https://github.com/wrealaero/SpeedAutoClicker-Mac/releases)
2. Extract the ZIP file to a location of your choice
3. Install the required dependencies:
   ```bash
   python3 -m pip install --user -r requirements.txt
   ```
4. Run the application:
   ```bash
   python3 autoclicker.py
   ```

## Usage

### Basic Usage

1. Set your desired Clicks Per Second (CPS)
2. Choose which mouse button to click
3. Select Toggle or Hold mode
4. Press the hotkey (default: F6) to start/stop clicking

### Advanced Features

- **Duty Cycle**: Controls how long the mouse button is held down
  - 50% is balanced (equal press and release time)
  - Higher values make the press longer
  - Lower values make the release longer

- **Hold Time**: Precise control over button press duration in milliseconds
  - Set to 0 to use the duty cycle instead

- **Click Limit**: Automatically stop after a specific number of clicks

- **Configurations**: Save and load different clicking profiles for various use cases

## Troubleshooting

### Common Issues

1. **Hotkeys Not Working**
   - Make sure you've granted accessibility permissions to the application
   - Try running the app with administrator privileges
   - Check if another application is using the same hotkey

2. **Clicking Not Working**
   - Verify that the application has accessibility permissions
   - Try a different mouse button
   - Restart the application

3. **Application Won't Start**
   - Check if Python 3 is installed correctly
   - Verify that all dependencies are installed
   - Check the logs for error messages

### Diagnostic Report

If you encounter issues, you can generate a diagnostic report:

1. Go to the "Advanced" tab
2. Click "Create Diagnostic Report"
3. Share this report when seeking help

## Privacy

Aerout SpeedAutoClicker respects your privacy:

- No data is sent to any servers
- All logs and configurations are stored locally on your computer
- No personal information is collected

## System Requirements

- macOS 10.13 (High Sierra) or later
- Python 3.7 or later
- 50MB of disk space
- Administrative privileges for installation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors and testers (Lighting, Cretz, etc..)
- Special thanks to the Python community for the excellent libraries

## Contact & Support

For bug reports and feature requests, please use the [GitHub Issues page](https://github.com/wrealaero/SpeedAutoClicker-Mac/issues).

---

Made with ❤️ by RealAero <3
