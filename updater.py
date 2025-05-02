#!/usr/bin/env python3
import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

GITHUB_USER = "wrealaero"
GITHUB_REPO = "SpeedAutoClicker-Mac"
GITHUB_BRANCH = "main"

FILES_TO_CHECK = [
    "autoclicker.py",
    "install.sh",
    "requirements.txt",
    "updater.py"
]

VERSION_FILE = os.path.expanduser("~/.speedautoclicker_version.json")

def get_github_file_url(file_path):
    """Get the raw GitHub URL for a file"""
    return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{file_path}"

def get_github_api_url():
    """Get the GitHub API URL for the repository"""
    return f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/commits?path="

def download_file(url, save_path=None):
    """Download a file from a URL"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if save_path:
                with open(save_path, 'wb') as out_file:
                    out_file.write(response.read())
                return True
            else:
                return response.read().decode('utf-8')
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"Error downloading {url}: {e}")
        return None

def get_last_commit_date(file_path):
    """Get the last commit date for a file"""
    try:
        api_url = get_github_api_url() + file_path
        with urllib.request.urlopen(api_url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and len(data) > 0:
                return data[0]['commit']['committer']['date']
    except Exception as e:
        print(f"Error checking commit date: {e}")
    return None

def load_version_info():
    """Load the local version information"""
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_version_info(version_info):
    """Save the local version information"""
    try:
        with open(VERSION_FILE, 'w') as f:
            json.dump(version_info, f)
    except Exception as e:
        print(f"Error saving version info: {e}")

def check_for_updates(silent=False):
    """Check if updates are available"""
    if not silent:
        print("Checking for updates...")

    version_info = load_version_info()

    updates_available = False
    updated_files = []
    
    for file_path in FILES_TO_CHECK:
        last_commit = get_last_commit_date(file_path)
        if not last_commit:
            continue
            
        local_commit = version_info.get(file_path, "")
        
        if local_commit != last_commit:
            updates_available = True
            updated_files.append(file_path)
            version_info[file_path] = last_commit

    if updates_available:
        save_version_info(version_info)
    
    return updates_available, updated_files

def update_application(callback=None):
    """Update the application files"""
    print("Updating SpeedAutoClicker...")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    with tempfile.TemporaryDirectory() as temp_dir:

        for file_path in FILES_TO_CHECK:
            file_url = get_github_file_url(file_path)
            local_path = os.path.join(current_dir, file_path)
            temp_path = os.path.join(temp_dir, file_path)
            
            print(f"Updating {file_path}...")
            
            if download_file(file_url, temp_path):

                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                shutil.copy2(temp_path, local_path)

                if file_path.endswith('.py') or file_path.endswith('.sh'):
                    os.chmod(local_path, 0o755)
            else:
                print(f"Failed to update {file_path}")
    
    print("Update completed successfully!")

    try:
        install_script = os.path.join(current_dir, "install.sh")
        if os.path.exists(install_script):
            print("Running install script to update dependencies...")
            subprocess.run(["bash", install_script, "--update"], check=True)
    except subprocess.SubprocessError as e:
        print(f"Error running install script: {e}")

    if callback:
        callback()

def prompt_for_update():
    """Check for updates and prompt the user"""
    updates_available, updated_files = check_for_updates()
    
    if updates_available:
        print("Updates available for the following files:")
        for file in updated_files:
            print(f"- {file}")
        
        response = input("Would you like to update now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            update_application()
            print("Please restart the application to apply the updates.")
            return True
    else:
        print("No updates available.")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--silent":
        check_for_updates(silent=True)
    else:
        prompt_for_update()
