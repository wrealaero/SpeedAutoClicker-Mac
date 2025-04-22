#!/bin/bash
echo "Installing SpeedAutoClicker..."
REPO="wrealaero/SpeedAutoClicker-Mac"
LATEST_URL=$(curl -s https://api.github.com/repos/$REPO/releases/latest | grep "browser_download_url.*zip" | cut -d '"' -f 4)

if [ -z "$LATEST_URL" ]; then
    echo "❌ Could not find download URL. Did you create a release?"
    exit 1
fi

echo "Downloading from: $LATEST_URL"
curl -L "$LATEST_URL" -o /tmp/SpeedAutoClicker.zip || {
    echo "❌ Download failed!"
    exit 1
}

unzip -o /tmp/SpeedAutoClicker.zip -d /Applications/ || {
    echo "❌ Installation failed!"
    exit 1
}

xattr -rd com.apple.quarantine /Applications/SpeedAutoClicker.app
echo "✅ Installed! Open from Spotlight or:"
echo "   open /Applications/SpeedAutoClicker.app"
