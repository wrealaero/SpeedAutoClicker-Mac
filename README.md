# 🚀 Aerout SpeedAutoClicker for macOS

A high-performance autoclicker with advanced features for macOS.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![Python](https://img.shields.io/badge/python-3.6%2B-green)

## ✨ Features

- **High Performance**: Optimized for speed and low CPU usage
- **Multiple Click Modes**: Toggle or Hold modes
- **Custom CPS**: Set your desired Clicks Per Second
- **Advanced Click Patterns**: Control duty cycle and hold time
- **Click Limiting**: Set a maximum number of clicks
- **Custom Hotkeys**: Use keyboard or mouse buttons as triggers
- **Configuration Profiles**: Save and load different clicking setups
- **Custom Themes**: Personalize your autoclicker with custom color schemes
- **Diagnostic Tools**: Built-in logging and troubleshooting reports

## 📋 Requirements

- macOS High Sierra (10.13) or newer
- Python 3.6 or newer
- Required Python packages (automatically installed):
  - pyautogui
  - pynput
  - packaging
  - requests

## 🔧 Installation

### Easy Install

1. Download the latest release from the [Releases page](https://github.com/wrealaero/SpeedAutoClicker-Mac/releases)
2. Extract the ZIP file
3. Run the installer script:
   ```
   chmod +x install.sh
   ./install.sh
   ```
4. Follow the on-screen instructions

### Manual Installation

1. Clone the repository:
   ```
   git clone https://github.com/wrealaero/SpeedAutoClicker-Mac.git
   ```
2. Install the required packages:
   ```
   pip3 install -r requirements.txt
   ```
3. Run the application:
   ```
   python3 autoclicker.py
   ```

## 🎮 Usage

1. **Set Your Clicking Speed**:
   - Enter your desired Clicks Per Second (CPS)

2. **Choose Mouse Button**:
   - Select which mouse button to click: Left, Right, or Middle

3. **Select Click Mode**:
   - **Toggle Mode**: Press hotkey once to start clicking, press again to stop
   - **Hold Mode**: Clicking continues only while you hold down the hotkey

4. **Start/Stop Clicking**:
   - Press the default hotkey (F6) to start clicking
   - In Toggle Mode, press F6 again to stop
   - In Hold Mode, release F6 to stop
   - You can also use the Start/Stop buttons in the app

### Advanced Features

- **Duty Cycle**: Controls how long each click is held down
- **Hold Time**: Set exact milliseconds for button press duration
- **Click Limiting**: Set a maximum number of clicks to perform
- **Custom Hotkeys**: Change the activation key or mouse button
- **Configurations**: Save different settings for different applications
- **Themes**: Choose between Default, Light, Dark, or Custom themes

## 🤝 Support

If you encounter any issues or have questions:

- Join our [Discord server](https://discord.gg/shA7X2Wesr) for help and updates
- Create an issue on GitHub
- Use the built-in diagnostic tool to generate a report

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Thanks to all contributors and testers

---

Made with ❤️ by RealAero <3
