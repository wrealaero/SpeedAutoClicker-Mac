#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          AeroutClicker Installation        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"

echo -e "${YELLOW}Checking for Python 3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed.${NC}"
    echo -e "${YELLOW}Would you like to install Python 3 now? (y/n)${NC}"
    read -r install_python
    
    if [[ "$install_python" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Installing Python 3 using Homebrew...${NC}"

        if ! command -v brew &> /dev/null; then
            echo -e "${YELLOW}Homebrew not found. Installing Homebrew...${NC}"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi

        brew install python

        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}Failed to install Python 3. Please install it manually and try again.${NC}"
            echo -e "${YELLOW}Visit https://www.python.org/downloads/ to download Python 3.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Python 3 is required to run AeroutClicker.${NC}"
        echo -e "${YELLOW}Please install Python 3 and try again.${NC}"
        echo -e "${YELLOW}Visit https://www.python.org/downloads/ to download Python 3.${NC}"
        exit 1
    fi
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"

echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv 2>/dev/null

if [ -d "venv" ]; then
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate

    if [ "$VIRTUAL_ENV" != "" ]; then
        echo -e "${GREEN}Virtual environment activated.${NC}"
    else
        echo -e "${YELLOW}Could not activate virtual environment. Continuing with system Python...${NC}"
    fi
else
    echo -e "${YELLOW}Virtual environment creation failed. Continuing with system Python...${NC}"
fi

echo -e "${YELLOW}Installing dependencies...${NC}"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
else
    echo -e "${RED}Failed to install some dependencies.${NC}"
    echo -e "${YELLOW}Trying alternative installation method...${NC}"

    python3 -m pip install six
    python3 -m pip install pynput==1.7.6
    python3 -m pip install pyobjc-framework-Quartz==9.2
    python3 -m pip install pyobjc-core
    python3 -m pip install pyobjc-framework-Cocoa
    python3 -m pip install pyobjc-framework-ApplicationServices
    
    echo -e "${YELLOW}Alternative installation completed. Some features may not work correctly.${NC}"
fi

echo -e "${YELLOW}Setting permissions...${NC}"
chmod +x autoclicker.py
chmod +x updater.py

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Installation Complete!           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"

echo -e "${YELLOW}To run AeroutClicker:${NC}"
if [ -d "venv" ]; then
    echo -e "${BLUE}source venv/bin/activate${NC}"
fi
echo -e "${BLUE}python3 autoclicker.py${NC}"

echo -e "${YELLOW}Note: You may need to grant accessibility permissions to use AeroutClicker.${NC}"
echo -e "${YELLOW}Go to System Preferences > Security & Privacy > Privacy > Accessibility${NC}"
echo -e "${YELLOW}and add Terminal or the Python application to the list of allowed apps.${NC}"

echo -e "${YELLOW}Would you like to run AeroutClicker now? (y/n)${NC}"
read -r run_now

if [[ "$run_now" =~ ^[Yy]$ ]]; then
    python3 autoclicker.py
fi
