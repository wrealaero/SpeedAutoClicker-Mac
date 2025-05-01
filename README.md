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

## Installation

### Method 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/wrealaero/SpeedAutoClicker-Mac.git
cd SpeedAutoClicker-Mac

# Run the installation script
chmod +x install.sh
./install.sh
```

### Method 2: Manual Installation

```bash
# Download the repository as ZIP and extract it
# Navigate to the extracted directory

# Install dependencies
pip3 install -r requirements.txt

# Make the script executable
chmod +x autoclicker.py
```

## Usage

1. Run the application:
   ```bash
   python3 autoclicker.py
   ```

2. Grant accessibility permissions when prompted:
   - Go to System Preferences > Security & Privacy > Privacy > Accessibility
   - Add Terminal or Python to the list of allowed applications

3. Configure your settings:
   - Set your desired click rate (in milliseconds)
   - Adjust the click duty cycle (how long each click is held)
   - Choose which mouse button to simulate
   - Set up your preferred hotkey
   - Select toggle or hold mode

4. Start clicking using either:
   - The "Start" button in the application
   - Your configured hotkey

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

## Troubleshooting

### Accessibility Permissions
If the auto-clicker doesn't work, make sure you've granted accessibility permissions:
1. Open System Preferences
2. Go to Security & Privacy > Privacy > Accessibility
3. Add Terminal or Python to the list of allowed apps
4. Restart the application

### Click Not Working in Some Applications
Some applications may have their own input handling that can interfere with simulated clicks. Try adjusting the click duty cycle or interval.

## Support

If you encounter any issues or have suggestions:
- Join our [Discord Server](https://discord.gg/MxGV8fGzpR)
- DM 5qvx for bugs and issues

## License

This project is open source and available under the MIT License.
