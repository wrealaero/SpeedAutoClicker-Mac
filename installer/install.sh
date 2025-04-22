#!/bin/bash
echo "Installing SpeedAutoClicker..."

REPO_OWNER="wrealaero"
REPO_NAME="SpeedAutoClicker-Mac"

# Get latest release download URL
DOWNLOAD_URL=$(curl -s "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest" | grep "browser_download_url.*zip" | cut -d '"' -f 4)

if [ -z "$DOWNLOAD_URL" ]; then
    echo "❌ Error: No download URL found. Have you created a release?"
    echo "Go to: https://github.com/$REPO_OWNER/$REPO_NAME/releases/new"
    exit 1
fi

echo "Downloading from GitHub..."
curl -L "$DOWNLOAD_URL" -o /tmp/SpeedAutoClicker.zip || {
    echo "❌ Download failed!"
    exit 1
}

echo "Installing to Applications..."
unzip -o /tmp/SpeedAutoClicker.zip -d /Applications/ || {
    echo "❌ Installation failed!"
    exit 1
}

# Fix MacOS permissions
xattr -rd com.apple.quarantine /Applications/SpeedAutoClicker.app

echo ""
echo "✅ Installation successful!"
echo "Launch from Spotlight or run:"
echo "   open /Applications/SpeedAutoClicker.app"
