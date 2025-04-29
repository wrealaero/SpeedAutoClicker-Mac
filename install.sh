#!/bin/bash

echo "=== AeroClicker Installation ==="
echo "This script will install AeroClicker on your macOS system."

if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: This script is designed for macOS only."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

INSTALL_DIR="$HOME/.aero-clicker"
mkdir -p "$INSTALL_DIR"

echo "Copying files to $INSTALL_DIR..."
cp autoclicker.py "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"
cp README.md "$INSTALL_DIR/" 2>/dev/null || true

echo "Setting up virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

chmod +x autoclicker.py

LAUNCHER="$HOME/bin/aeroclicker"
mkdir -p "$(dirname "$LAUNCHER")"

cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
# AeroClicker Launcher

# Activate virtual environment and run the script
cd "$HOME/.aero-clicker"
source venv/bin/activate
python3 autoclicker.py "$@"
EOF

chmod +x "$LAUNCHER"

if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo "Adding $HOME/bin to PATH in your shell profile..."

    if [[ -f "$HOME/.zshrc" ]]; then
        PROFILE="$HOME/.zshrc"
    elif [[ -f "$HOME/.bash_profile" ]]; then
        PROFILE="$HOME/.bash_profile"
    elif [[ -f "$HOME/.bashrc" ]]; then
        PROFILE="$HOME/.bashrc"
    else
        PROFILE="$HOME/.profile"
        touch "$PROFILE"
    fi
    
    echo 'export PATH="$HOME/bin:$PATH"' >> "$PROFILE"
    echo "Added $HOME/bin to PATH in $PROFILE"
    echo "Please restart your terminal or run 'source $PROFILE' to update your PATH."
fi

echo ""
echo "=== Installation Complete! ==="
echo "You can now run AeroClicker by typing 'aeroclicker' in your terminal."
echo ""
echo "Note: You may need to grant accessibility permissions to Terminal or your terminal app"
echo "in System Preferences > Security & Privacy > Privacy > Accessibility"
echo ""
echo "For help, run: aeroclicker --help"
echo ""
