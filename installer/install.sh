#!/bin/bash
echo "Installing SpeedAutoClicker..."
curl -L https://github.com/$USER/SpeedAutoClicker-Mac/releases/latest/download/SpeedAutoClicker-Mac.zip -o /tmp/SpeedAutoClicker.zip
unzip -o /tmp/SpeedAutoClicker.zip -d /Applications/
xattr -rd com.apple.quarantine /Applications/SpeedAutoClicker.app
echo "Done! Open from Spotlight."
