#!/bin/bash

echo "Installing SpeedAutoClicker..."
ZIP_URL=$(curl -s https://api.github.com/repos/wrealaero/SpeedAutoClicker-Mac/releases/latest | grep "browser_download_url" | cut -d '"' -f 4)
curl -L "$ZIP_URL" -o /tmp/SpeedAutoClicker.zip || {
    echo "❌ Download failed!"
    exit 1
}
unzip -o /tmp/SpeedAutoClicker.zip -d /Applications/ || {
    echo "❌ Installation failed!"
    exit 1
}
xattr -rd com.apple.quarantine /Applications/SpeedAutoClicker.app
echo "✅ Installed! Launch from Spotlight or:"
echo "   open /Applications/SpeedAutoClicker.app"
