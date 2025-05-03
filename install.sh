#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
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
echo -e "${BLUE}=== AeroutClicker Installation Script ===${NC}"
echo -e "${YELLOW}This script will install all required dependencies for AeroutClicker.${NC}"
echo

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed.${NC}"
    echo -e "Please install Python 3 using one of these methods:"
    echo -e "1. Download from ${BLUE}https://www.python.org/downloads/macos/${NC}"
    echo -e "2. Install using Homebrew: ${BLUE}brew install python3${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${YELLOW}Detected Python version: ${PYTHON_VERSION}${NC}"

if ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}Installing pip...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv 2>/dev/null

if [ -d "venv" ]; then
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
    USING_VENV=true
else
    echo -e "${YELLOW}Virtual environment creation failed, continuing with system Python...${NC}"
    USING_VENV=false
fi

echo -e "${YELLOW}Installing dependencies...${NC}"

ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    echo -e "${YELLOW}Detected Apple Silicon (M1/M2) Mac${NC}"
else
    echo -e "${YELLOW}Detected Intel Mac${NC}"
fi

python3 -m pip install --upgrade pip

echo -e "${YELLOW}Installing six...${NC}"
python3 -m pip install six || { echo -e "${RED}Failed to install six${NC}"; exit 1; }

echo -e "${YELLOW}Installing pynput...${NC}"
python3 -m pip install pynput==1.7.6 || { echo -e "${RED}Failed to install pynput${NC}"; exit 1; }

echo -e "${YELLOW}Installing PyObjC components...${NC}"
python3 -m pip install pyobjc-core>=9.2 || { echo -e "${RED}Failed to install pyobjc-core${NC}"; exit 1; }
python3 -m pip install pyobjc-framework-Cocoa>=9.2 || { echo -e "${RED}Failed to install pyobjc-framework-Cocoa${NC}"; exit 1; }
python3 -m pip install pyobjc-framework-Quartz==9.2 || { echo -e "${RED}Failed to install pyobjc-framework-Quartz${NC}"; exit 1; }
python3 -m pip install pyobjc-framework-ApplicationServices>=9.2 || { echo -e "${RED}Failed to install pyobjc-framework-ApplicationServices${NC}"; exit 1; }

chmod +x autoclicker.py

echo -e "${GREEN}Installation complete!${NC}"

echo -e "${BLUE}=== How to Run AeroutClicker ===${NC}"
if [ "$USING_VENV" = true ]; then
    echo -e "1. Activate the virtual environment: ${YELLOW}source venv/bin/activate${NC}"
    echo -e "2. Run the autoclicker: ${YELLOW}python autoclicker.py${NC}"
    echo -e "Or use the one-line command: ${YELLOW}source venv/bin/activate && python autoclicker.py${NC}"
else
    echo -e "Run the autoclicker: ${YELLOW}python3 autoclicker.py${NC}"
fi

echo -e "${BLUE}=== Important Notice ===${NC}"
echo -e "${YELLOW}You may need to grant accessibility permissions to use AeroutClicker.${NC}"
echo -e "Go to System Preferences > Security & Privacy > Privacy > Accessibility"
echo -e "and add Terminal or the Python application to the list of allowed apps."

echo -e "${BLUE}=== Troubleshooting Tips ===${NC}"
echo -e "If you encounter issues:"
echo -e "1. Make sure you've granted accessibility permissions"
echo -e "2. Try running with a specific Python version: ${YELLOW}python3.9 autoclicker.py${NC}"
echo -e "3. For module errors, try reinstalling: ${YELLOW}pip3 install -r requirements.txt${NC}"
echo -e "4. Join our Discord for help: ${BLUE}https://discord.gg/MxGV8fGzpR${NC}"
