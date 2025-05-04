#!/bin/bash

BOLD="\033[1m"
RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
BLUE="\033[94m"
RESET="\033[0m"

echo -e "${BOLD}${BLUE}==================================================${RESET}"
echo -e "${BOLD}${BLUE}  Aerout SpeedAutoClicker for macOS - Installer   ${RESET}"
echo -e "${BOLD}${BLUE}==================================================${RESET}"
echo ""

if [ "$(uname)" != "Darwin" ]; then
    echo -e "${RED}Error: This installer is for macOS only.${RESET}"
    exit 1
fi

MACOS_VERSION=$(sw_vers -productVersion)
echo -e "${YELLOW}Detected macOS version: ${MACOS_VERSION}${RESET}"

ARCH=$(uname -m)
echo -e "${YELLOW}Detected architecture: ${ARCH}${RESET}"
echo ""

echo -e "${BLUE}Checking for Python 3...${RESET}"
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}Found ${PYTHON_VERSION}${RESET}"
else
    echo -e "${RED}Python 3 not found. Please install Python 3 from python.org${RESET}"
    echo -e "${YELLOW}Opening Python download page...${RESET}"
    open "https://www.python.org/downloads/macos/"
    exit 1
fi

echo -e "${BLUE}Creating application directory...${RESET}"
APP_DIR="$HOME/Applications/AeroutClicker"
mkdir -p "$APP_DIR"
echo -e "${GREEN}Created directory: ${APP_DIR}${RESET}"

echo -e "${BLUE}Creating data directory...${RESET}"
DATA_DIR="$HOME/Documents/AeroutClicker"
mkdir -p "$DATA_DIR"
mkdir -p "$DATA_DIR/configs"
mkdir -p "$DATA_DIR/logs"
echo -e "${GREEN}Created directory: ${DATA_DIR}${RESET}"

echo -e "${BLUE}Copying application files...${RESET}"
cp -f autoclicker.py "$APP_DIR/"
cp -f logger.py "$APP_DIR/"
cp -f updater.py "$APP_DIR/"
cp -f requirements.txt "$APP_DIR/"
cp -f README.md "$APP_DIR/"
cp -f LICENSE "$APP_DIR/"

chmod +x "$APP_DIR/autoclicker.py"
chmod +x "$APP_DIR/updater.py"
echo -e "${GREEN}Files copied successfully${RESET}"

echo -e "${BLUE}Installing dependencies...${RESET}"
python3 -m pip install --user -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies. Please try running:${RESET}"
    echo -e "${YELLOW}python3 -m pip install --user -r requirements.txt${RESET}"
else
    echo -e "${GREEN}Dependencies installed successfully${RESET}"
fi

echo -e "${BLUE}Creating application launcher...${RESET}"
LAUNCHER="$HOME/Applications/Aerout SpeedAutoClicker.command"
cat > "$LAUNCHER" << EOF
#!/bin/bash
cd "$APP_DIR"
python3 autoclicker.py
EOF
chmod +x "$LAUNCHER"
echo -e "${GREEN}Launcher created: ${LAUNCHER}${RESET}"

echo -e "${BLUE}Creating desktop shortcut...${RESET}"
DESKTOP_SHORTCUT="$HOME/Desktop/Aerout SpeedAutoClicker.command"
ln -sf "$LAUNCHER" "$DESKTOP_SHORTCUT"
echo -e "${GREEN}Desktop shortcut created${RESET}"

echo ""
echo -e "${BOLD}${GREEN}==================================================${RESET}"
echo -e "${BOLD}${GREEN}  Aerout SpeedAutoClicker installed successfully!  ${RESET}"
echo -e "${BOLD}${GREEN}==================================================${RESET}"
echo ""
echo -e "${YELLOW}To start the application:${RESET}"
echo -e "  1. Double-click the 'Aerout SpeedAutoClicker' icon on your desktop"
echo -e "  2. If you see a security warning, right-click the icon and select Open"
echo ""
echo -e "${YELLOW}Application data is stored in:${RESET}"
echo -e "  ${DATA_DIR}"
echo ""
echo -e "${BLUE}Thank you for installing Aerout SpeedAutoClicker!${RESET}"

echo ""
read -p "Would you like to start the application now? (y/n): " START_NOW
if [[ $START_NOW == "y" || $START_NOW == "Y" ]]; then
    echo -e "${GREEN}Starting Aerout SpeedAutoClicker...${RESET}"
    open "$LAUNCHER"
fi

exit 0
