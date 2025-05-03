#!/bin/bash

BOLD="\033[1m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RESET="\033[0m"

echo -e "${BOLD}${BLUE}====================================${RESET}"
echo -e "${BOLD}${BLUE}     SpeedAutoClicker Installation  ${RESET}"
echo -e "${BOLD}${BLUE}====================================${RESET}"
echo

echo -e "${BOLD}Checking Python installation...${RESET}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found $PYTHON_VERSION${RESET}"
else
    echo -e "${RED}✗ Python 3 not found${RESET}"
    echo -e "${YELLOW}Please install Python 3 from python.org or using Homebrew:${RESET}"
    echo "    brew install python"
    exit 1
fi

echo -e "${BOLD}Checking pip installation...${RESET}"
if python3 -m pip --version &>/dev/null; then
    PIP_VERSION=$(python3 -m pip --version)
    echo -e "${GREEN}✓ Found pip${RESET}"
else
    echo -e "${RED}✗ pip not found${RESET}"
    echo -e "${YELLOW}Installing pip...${RESET}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

echo -e "${BOLD}Checking virtualenv...${RESET}"
if python3 -m pip show virtualenv &>/dev/null; then
    echo -e "${GREEN}✓ virtualenv is installed${RESET}"
else
    echo -e "${YELLOW}Installing virtualenv...${RESET}"
    python3 -m pip install virtualenv
fi

IS_APPLE_SILICON=false
if [[ $(uname -m) == "arm64" ]]; then
    IS_APPLE_SILICON=true
    echo -e "${BLUE}ℹ Detected Apple Silicon Mac${RESET}"
fi

echo -e "${BOLD}Setting up virtual environment...${RESET}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}ℹ Existing virtual environment found. Recreating...${RESET}"
    rm -rf venv
fi

python3 -m virtualenv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to create virtual environment${RESET}"
    echo -e "${YELLOW}Trying alternative method...${RESET}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to create virtual environment using venv${RESET}"
        echo -e "${YELLOW}Installing dependencies globally...${RESET}"
        python3 -m pip install -r requirements.txt
    fi
else
    echo -e "${GREEN}✓ Virtual environment created${RESET}"
    source venv/bin/activate
    echo -e "${BOLD}Installing dependencies...${RESET}"
    if [ "$IS_APPLE_SILICON" = true ]; then
        echo -e "${BLUE}ℹ Using Apple Silicon specific installation${RESET}"
        pip install six
        pip install pynput==1.7.6
        pip install pyobjc-framework-Quartz==9.2 pyobjc-core>=9.2 pyobjc-framework-Cocoa>=9.2 pyobjc-framework-ApplicationServices>=9.2
    else
        pip install -r requirements.txt
    fi
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to install dependencies${RESET}"
        echo -e "${YELLOW}Please try installing them manually:${RESET}"
        echo "    pip install -r requirements.txt"
    else
        echo -e "${GREEN}✓ Dependencies installed successfully${RESET}"
    fi
fi

echo -e "${BOLD}Making scripts executable...${RESET}"
chmod +x autoclicker.py
chmod +x updater.py
echo -e "${GREEN}✓ Scripts are now executable${RESET}"

echo -e "${BOLD}Checking accessibility permissions...${RESET}"
echo -e "${YELLOW}ℹ SpeedAutoClicker requires accessibility permissions to function properly.${RESET}"
echo -e "${YELLOW}ℹ You may be prompted to grant these permissions when you first run the app.${RESET}"

echo
echo -e "${BOLD}${GREEN}Installation complete!${RESET}"
echo
echo -e "${BOLD}To run SpeedAutoClicker:${RESET}"
echo -e "1. Activate the virtual environment:${RESET}"
echo -e "   ${BLUE}source venv/bin/activate${RESET}"
echo
echo -e "2. Run the application:${RESET}"
echo -e "   ${BLUE}./autoclicker.py${RESET}"
echo -e "   or"
echo -e "   ${BLUE}python3 autoclicker.py${RESET}"
echo
echo -e "${BOLD}${BLUE}====================================${RESET}"
echo -e "${BOLD}${BLUE}  Thank you for using SpeedAutoClicker!${RESET}"
echo -e "${BOLD}${BLUE}====================================${RESET}"
