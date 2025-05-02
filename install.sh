#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== SpeedAutoClicker Installer ===${NC}"
echo "This script will install SpeedAutoClicker and its dependencies."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Would you like to install Python now? (y/n)"
    read -r install_python
    
    if [[ $install_python == "y" || $install_python == "Y" ]]; then
        echo "Installing Python 3 using Homebrew..."

        if ! command -v brew &> /dev/null; then
            echo "Installing Homebrew first..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi

        brew install python

        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}Failed to install Python 3. Please install it manually from python.org${NC}"
            exit 1
        fi
    else
        echo "Please install Python 3 from https://www.python.org/downloads/ and run this script again."
        exit 1
    fi
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"

if ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}Installing pip for Python 3...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

echo -e "${YELLOW}Setting up virtual environment...${NC}"
python3 -m venv venv 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Virtual environment creation failed, continuing with system Python...${NC}"
    PYTHON_CMD="python3"
    PIP_CMD="python3 -m pip"
else
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
    source venv/bin/activate
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo -e "${YELLOW}Upgrading pip...${NC}"
$PIP_CMD install --upgrade pip

echo -e "${YELLOW}Installing dependencies...${NC}"
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}Error installing dependencies.${NC}"
    echo "Trying alternative installation method..."

    $PIP_CMD install six
    $PIP_CMD install pynput==1.7.6
    $PIP_CMD install pyobjc-core
    $PIP_CMD install pyobjc-framework-Cocoa
    $PIP_CMD install pyobjc-framework-ApplicationServices
    $PIP_CMD install pyobjc-framework-Quartz
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Installation failed. Please try manually:${NC}"
        echo "pip3 install -r requirements.txt"
        exit 1
    fi
fi

chmod +x autoclicker.py

echo '#!/bin/bash
cd "$(dirname "$0")"
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python3 autoclicker.py
' > speedautoclicker
chmod +x speedautoclicker

echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo -e "${YELLOW}Important:${NC} You may need to grant accessibility permissions to use SpeedAutoClicker."
echo "Go to System Preferences > Security & Privacy > Privacy > Accessibility"
echo "and add Terminal or the Python application to the list of allowed apps."
echo ""
echo -e "${GREEN}To run SpeedAutoClicker:${NC}"
echo "Option 1: ./speedautoclicker"
echo "Option 2: python3 autoclicker.py"

echo ""
echo -e "${YELLOW}Would you like to run SpeedAutoClicker now? (y/n)${NC}"
read -r run_now

if [[ $run_now == "y" || $run_now == "Y" ]]; then
    echo "Starting SpeedAutoClicker..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    python3 autoclicker.py
fi
