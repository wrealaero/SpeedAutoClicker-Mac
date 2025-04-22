import requests
import json
import os
import sys
import subprocess
from version import __version__

GITHUB_REPO = "yourusername/SpeedAutoClicker-Mac"

def check_for_updates(current_version):
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url)
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release['tag_name']
            
            if self.compare_versions(current_version, latest_version) < 0:
                return True
    except Exception as e:
        print(f"Update check failed: {e}")
    return False

def compare_versions(v1, v2):
    # Simple version comparison (you might want something more robust)
    from distutils.version import StrictVersion
    try:
        return cmp(StrictVersion(v1), StrictVersion(v2))
    except:
        return 0

def update_application():
    # This would download and install the update
    # Implementation depends on your packaging method
    pass
