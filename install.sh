#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' 

echo -e "${BLUE}"
echo "  ___                  _    _       _        ___ _ _      _             "
echo " / __|_ __  ___ ___ __| |  /_\  _  | |_ ___ / __| (_)__  | |_____ _ _   "
echo " \__ \ '_ \/ -_) -_) _\` | / _ \| || |  _/ _ \ (__| | / _| | / / -_) '_|  " # ts so tuff boi
echo " |___/ .__/\___\___\__,_|/_/ \_\\_,_|\__\___/\___|_|_\__| |_\_\___|_|    "
echo "     |_|                                                                "
echo -e "${NC}"
echo -e "${GREEN}Installation Script${NC}"
echo

if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This installer is only for macOS systems.${NC}"
    exit 1
fi
INSTALL_DIR="$HOME/Applications/AeroutClicker"
DESKTOP_SHORTCUT="$HOME/Desktop/AeroutClicker.command"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.6 or higher from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION < 3.6" | bc -l) )); then
    echo -e "${RED}Error: Python 3.6 or higher is required.${NC}"
    echo "Current version: $PYTHON_VERSION"
    echo "Please update Python from https://www.python.org/downloads/"
    exit 1
fi

echo -e "${GREEN}Python $PYTHON_VERSION detected.${NC}"

echo "Installing required packages..."
pip3 install --user pyautogui pynput packaging requests

echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

echo "Copying files..."
cp -R "$CURRENT_DIR"/* "$INSTALL_DIR/"

echo "Setting permissions..."
chmod +x "$INSTALL_DIR/autoclicker.py"
chmod +x "$INSTALL_DIR/updater.py"
chmod +x "$INSTALL_DIR/install.sh"

echo "Creating desktop shortcut..."
cat > "$DESKTOP_SHORTCUT" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 autoclicker.py
EOF
chmod +x "$DESKTOP_SHORTCUT"

if [ ! -f "$INSTALL_DIR/version.txt" ]; then
    echo "1.1.0" > "$INSTALL_DIR/version.txt"
fi

mkdir -p "$HOME/Documents/AeroutClicker/logs"
mkdir -p "$HOME/Documents/AeroutClicker/configs"
mkdir -p "$HOME/Documents/AeroutClicker/diagnostics"

echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "You can start Aerout SpeedAutoClicker by:"
echo "1. Double-clicking the shortcut on your Desktop"
echo "2. Running 'python3 $INSTALL_DIR/autoclicker.py'"
echo ""
echo -e "${BLUE}Note: On first run, you may need to grant accessibility permissions${NC}"
echo "This is required for the autoclicker to function properly."
echo ""
echo -e "${GREEN}Thank you for installing Aerout SpeedAutoClicker!${NC}"
echo "Join our Discord server for updates and help: https://discord.gg/shA7X2Wesr"

read -p "Would you like to run Aerout SpeedAutoClicker now? (y/n): " choice
case "$choice" in 
  y|Y ) 
    echo "Starting Aerout SpeedAutoClicker..."
    cd "$INSTALL_DIR" && python3 autoclicker.py
    ;;
  * ) 
    echo "You can run Aerout SpeedAutoClicker later using the desktop shortcut."
    ;;
esac

exit 0
