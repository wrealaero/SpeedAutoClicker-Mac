# Aerout SpeedAutoClicker

An advanced auto-clicker for macOS with precise control over click rate, duty cycle, and more.

## Features

- **Precise Click Control**: Set exact click intervals in milliseconds
- **Click Duty Cycle**: Control how long each click is held down
- **Multiple Mouse Buttons**: Support for left, right, and middle mouse buttons
- **Hotkey Support**: Activate clicking with customizable hotkeys
- **Hold or Toggle Mode**: Choose between holding the hotkey or toggling on/off
- **Click Limiting**: Set a specific number of clicks or run indefinitely

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/wrealaero/AeroClicker.git
   cd AeroClicker
   ```

2. Run the installation script:
   ```
   ./install.sh
   ```

3. Grant accessibility permissions to Terminal (or your terminal app) in:
   System Preferences > Security & Privacy > Privacy > Accessibility

## Usage

Run AeroClicker from the terminal:

```
aeroclicker
```

### Command-line Options

- `-i, --interval`: Click interval in milliseconds
- `-d, --duty`: Click duty cycle percentage
- `-l, --limit`: Click limit (0 for unlimited)
- `-b, --button`: Mouse button to click (left, right, middle)
- `-t, --toggle`: Use toggle mode instead of hold mode
- `-k, --hotkey`: Hotkey to activate clicking (e.g., "shift+a")
- `-s, --start`: Start clicking immediately

### Interactive Commands

Once running, you can use these commands:
- `start` - Start clicking
- `stop` - Stop clicking
- `interval <ms>` - Set click interval in milliseconds
- `duty <percentage>` - Set duty cycle percentage
- `limit <number>` - Set click limit (0 for unlimited)
- `button <left|right|middle>` - Set mouse button
- `mode <hold|toggle>` - Set activation mode
- `hotkey <key combination>` - Set hotkey (e.g., 'shift+a')
- `status` - Show current settings
- `discord` - Open Discord server link
- `exit` - Exit the program

## Support

For bugs and issues, please DM 5qvx on Discord or join our server:
[https://discord.gg/MxGV8fGzpR](https://discord.gg/MxGV8fGzpR)
