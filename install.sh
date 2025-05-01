#!/bin/bash

echo "Installing AeroutClicker dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

python3 -m venv venv 2>/dev/null || echo "Virtual environment creation failed, continuing with system Python..."

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 -m pip install -r requirements.txt

echo "Installation complete!"
echo "To run AeroutClicker, use: python3 autoclicker.py"

chmod +x autoclicker.py

echo "Note: You may need to grant accessibility permissions to use AeroutClicker."
echo "Go to System Preferences > Security & Privacy > Privacy > Accessibility"
echo "and add Terminal or the Python application to the list of allowed apps."

