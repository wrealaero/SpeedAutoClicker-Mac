#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

echo -e "${YELLOW}Checking for Python 3...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}Found $PYTHON_VERSION${NC}"
else
    echo -e "${RED}Python 3 not found. Please install Python 3 before continuing.${NC}"
    echo "You can install Python 3 from https://www.python.org/downloads/ or using Homebrew:"
    echo "  brew install python"
    exit 1
fi

echo -e "${YELLOW}Checking for pip...${NC}"
if python3 -m pip --version &>/dev/null; then
    PIP_VERSION=$(python3 -m pip --version)
    echo -e "${GREEN}Found pip: $PIP_VERSION${NC}"
else
    echo -e "${RED}pip not found. Installing pip...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

echo -e "${YELLOW}Checking for virtualenv...${NC}"
if python3 -m pip show virtualenv &>/dev/null; then
    echo -e "${GREEN}virtualenv is installed${NC}"
else
    echo -e "${YELLOW}virtualenv not found. Installing virtualenv...${NC}"
    python3 -m pip install virtualenv
fi

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m virtualenv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Trying with venv module...${NC}"
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to create virtual environment. Installing dependencies globally...${NC}"
            GLOBAL_INSTALL=1
        fi
    fi
else
    echo -e "${GREEN}Virtual environment already exists${NC}"
fi

echo -e "${YELLOW}Installing dependencies...${NC}"
if [ -z "$GLOBAL_INSTALL" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies in virtual environment. Trying global installation...${NC}"
        GLOBAL_INSTALL=1
    else
        echo -e "${GREEN}Dependencies installed successfully in virtual environment${NC}"
    fi
fi

if [ ! -z "$GLOBAL_INSTALL" ]; then
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies. Please check the error messages above.${NC}"
        exit 1
    else
        echo -e "${GREEN}Dependencies installed successfully (global installation)${NC}"
    fi
fi

chmod +x autoclicker.py
chmod +x updater.py

echo
echo -e "${GREEN}Installation completed successfully!${NC}"
echo
echo -e "To run SpeedAutoClicker:"
if [ -z "$GLOBAL_INSTALL" ]; then
    echo -e "  ${BLUE}source venv/bin/activate${NC}"
    echo -e "  ${BLUE}python autoclicker.py${NC}"
else
    echo -e "  ${BLUE}python3 autoclicker.py${NC}"
fi
echo
echo -e "${YELLOW}Note:${NC} You may need to grant accessibility permissions to Terminal or Python"
echo "in System Preferences > Security & Privacy > Privacy > Accessibility"
echo

echo -e "${YELLOW}Creating launcher script...${NC}"
cat > speedautoclicker << EOL
#!/bin/bash
# SpeedAutoClicker Launcher

# Get the directory of this script
DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

# Check if we're using a virtual environment
if [ -d "\$DIR/venv" ]; then
    # Activate virtual environment and run
    source "\$DIR/venv/bin/activate"
    python "\$DIR/autoclicker.py"
else
    # Run with system Python
    python3 "\$DIR/autoclicker.py"
fi
EOL

chmod +x speedautoclicker

echo -e "${GREEN}Created launcher script: ${BLUE}./speedautoclicker${NC}"
echo

echo -e "${YELLOW}Checking accessibility permissions...${NC}"
if ! python3 -c "import Quartz; print('Quartz available')" &>/dev/null; then
    echo -e "${RED}Warning: Quartz module not working properly.${NC}"
    echo "You may need to grant accessibility permissions to Terminal or Python."
    echo "Go to System Preferences > Security & Privacy > Privacy > Accessibility"
    echo "and add Terminal or Python to the list of allowed apps."

    read -p "Would you like to open System Preferences now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
    fi
else
    echo -e "${GREEN}Quartz module is working properly.${NC}"
fi

echo
echo -e "${GREEN}Installation complete! You can now run SpeedAutoClicker using:${NC}"
echo -e "${BLUE}./speedautoclicker${NC}"
echo
echo -e "${YELLOW}If you encounter any issues, please report them on Discord or GitHub.${NC}"
echo
