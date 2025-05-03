# SpeedAutoClicker for macOS

A high-performance, reliable auto-clicker with precise control over click rate, duty cycle, and more.

## Features

- **High Performance**: Optimized for smooth operation even at high click rates
- **Customizable Click Rate**: Set clicks per second or millisecond intervals
- **Duty Cycle Control**: Adjust how long each click is held down
- **Multiple Mouse Buttons**: Support for left, right, and middle mouse buttons
- **Hotkey Activation**: Configurable hotkeys to start/stop clicking
- **Click Limiting**: Option to automatically stop after a specific number of clicks
- **User-Friendly Interface**: Simple and intuitive GUI

## Installation

### Setting Up with Virtual Environment (Recommended)

1. Download the SpeedAutoClicker folder
2. Open Terminal and navigate to the downloaded directory
3. Create a virtual environment:
   ```
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```
5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Make the script executable:
   ```
   chmod +x autoclicker.py
   ```
7. Run the application:
   ```
   ./autoclicker.py
   ```

### Quick Start (Alternative)

If you prefer not to use a virtual environment:

1. Download the SpeedAutoClicker folder
2. Open Terminal and navigate to the downloaded directory
3. Install the required dependencies:
   ```
   pip3 install -r requirements.txt
   ```
4. Make the script executable:
   ```
   chmod +x autoclicker.py
   ```
5. Run the application:
   ```
   python3 autoclicker.py
   ```

## Usage

### Main Controls

- **Click Interval**: Set the time between clicks in milliseconds (lower = faster)
- **Mouse Button**: Choose which mouse button to click (left, right, or middle)
- **Hotkey**: Configure a keyboard shortcut to start/stop clicking
- **Activation Mode**: Choose between toggle mode (press once to start, again to stop) or hold mode (click only while hotkey is held)

### Advanced Options

- **Duty Cycle**: Control how long each click is held down (as a percentage of the interval)
- **Click Limit**: Set a maximum number of clicks to perform before stopping automatically

### Troubleshooting

If the hotkey system stops responding, use the "Restart Hotkey System" button in the Advanced tab.

## Permissions

macOS requires accessibility permissions for applications that control the mouse. When you first run SpeedAutoClicker, you may need to:

1. Go to System Preferences > Security & Privacy > Privacy > Accessibility
2. Add Terminal or Python to the list of allowed applications
3. Ensure the checkbox next to the application is selected

## Support & Community

Join our Discord server for support, feature requests, and to connect with other users:
[SpeedAutoClicker Discord](https://discord.gg/MxGV8fGzpR)

## Credits

Created by wrealaero
