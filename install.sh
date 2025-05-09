GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

#ts so tuff boi
echo -e "${BLUE}"
echo "  ___                  _    _       _        ___ _ _      _             "
echo " / __|_ __  ___ ___ __| |  /_\  _  | |_ ___ / __| (_)__  | |_____ _ _   "
echo " \__ \ '_ \/ -_) -_) _\` | / _ \| || |  _/ _ \ (__| | / _| | / / -_) '_|  "
echo " |___/ .__/\___\___\__,_|/_/ \_\\_,_|\__\___/\___|_|_\__| |_\_\___|_|    "
echo "     |_|                                                                "
echo -e "${NC}"
echo -e "${GREEN}Dependency Installer${NC}"
echo

if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This installer is only for macOS systems.${NC}"
    exit 1
fi

echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.6 or higher from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

if [ $PYTHON_MAJOR -lt 3 ] || { [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 6 ]; }; then
    echo -e "${RED}Error: Python 3.6 or higher is required.${NC}"
    echo "Current version: $PYTHON_VERSION"
    echo "Please update Python from https://www.python.org/downloads/"
    exit 1
fi

echo -e "${GREEN}Python $PYTHON_VERSION detected.${NC}"

echo "Installing required packages..."
if ! pip3 install -r requirements.txt; then
    echo -e "${RED}Error: Failed to install dependencies. Trying with different approach...${NC}"
    python3 -m pip install --upgrade pip
    python3 -m pip install --force-reinstall -r requirements.txt
fi

read -p "Would you like to run Aerout SpeedAutoClicker now? (y/n): " choice
case "$choice" in 
  y|Y ) 
    echo "Starting Aerout SpeedAutoClicker..."
    python3 autoclicker.py
    ;;
  * ) 
    echo "You can run Aerout SpeedAutoClicker later using:"
    echo "python3 autoclicker.py"
    ;;
esac

exit 0
