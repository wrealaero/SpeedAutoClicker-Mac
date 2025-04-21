#!/bin/bash

# Speed Auto Clicker for Mac - Installer

echo "Installing Speed Auto Clicker for Mac..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Please install it first."
    exit 1
fi

# Create application directory
APP_DIR="/Applications/SpeedAutoClicker"
mkdir -p "$APP_DIR"

# Download latest release
echo "Downloading latest version..."
curl -L "https://github.com/wrealaero/SpeedAutoClicker-Mac/releases/latest/download/SpeedAutoClicker-Mac.zip" -o /tmp/SpeedAutoClicker.zip

# Unzip
echo "Installing..."
unzip -o /tmp/SpeedAutoClicker.zip -d "$APP_DIR"

# Create symlink to /usr/local/bin for terminal access
echo "Creating symlink..."
ln -sf "$APP_DIR/SpeedAutoClicker.app/Contents/MacOS/SpeedAutoClicker" /usr/local/bin/speedautoclicker

# Cleanup
rm /tmp/SpeedAutoClicker.zip

echo "Installation complete!"
echo "You can now run Speed Auto Clicker by:"
echo "1. Opening it from your Applications folder"
echo "2. Or running 'speedautoclicker' in your terminal"
