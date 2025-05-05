#!/usr/bin/env python3
"""
Updater module for Aerout SpeedAutoClicker
Checks for Updates
"""

import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from packaging import version

VERSION_FILE = os.path.join(os.path.dirname(__file__), "version.txt")
GITHUB_REPO = "wrealaero/SpeedAutoClicker-Mac"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
APP_DIR = os.path.dirname(os.path.abspath(__file__))

def get_current_version():
    """Get the current version of the application"""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                return f.read().strip()
        return "0.0.0"
    except Exception as e:
        print(f"Error getting current version: {e}")
        return "0.0.0"

def check_for_updates():
    """Check for updates from GitHub"""
    try:
        current_version = get_current_version()

        response = requests.get(
            GITHUB_API_URL,
            headers={"User-Agent": f"AeroutClicker/{current_version}"},
            timeout=10
        )
        
        if response.status_code == 200:
            release_info = response.json()
            latest_version = release_info["tag_name"].lstrip("v")

            if version.parse(latest_version) > version.parse(current_version):
                return {
                    "available": True,
                    "current_version": current_version,
                    "latest_version": latest_version,
                    "release_notes": release_info["body"],
                    "download_url": release_info["assets"][0]["browser_download_url"] if release_info["assets"] else None
                }
            else:
                return {
                    "available": False,
                    "current_version": current_version,
                    "latest_version": latest_version
                }
        else:
            return {
                "available": False,
                "error": f"Failed to check for updates: HTTP {response.status_code}"
            }
    
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return {
            "available": False,
            "error": f"Error checking for updates: {e}"
        }

def download_update(url, progress_callback=None):
    """Download the update file"""
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "update.zip")

        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 
        
        with open(zip_path, 'wb') as f:
            downloaded = 0
            for data in response.iter_content(block_size):
                f.write(data)
                downloaded += len(data)
                if progress_callback and total_size > 0:
                    progress = (downloaded / total_size) * 100
                    progress_callback(progress)
        
        return zip_path
    
    except Exception as e:
        print(f"Error downloading update: {e}")
        return None

def install_update(zip_path, progress_callback=None):
    """Install the update"""
    try:
        extract_dir = tempfile.mkdtemp()

        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            total_files = len(zip_ref.namelist())
            for i, file in enumerate(zip_ref.namelist()):
                zip_ref.extract(file, extract_dir)
                if progress_callback:
                    progress = (i / total_files) * 100
                    progress_callback(progress)

        main_dir = None
        for item in os.listdir(extract_dir):
            if os.path.isdir(os.path.join(extract_dir, item)):
                main_dir = os.path.join(extract_dir, item)
                break
        
        if not main_dir:
            main_dir = extract_dir

        for item in os.listdir(main_dir):
            src = os.path.join(main_dir, item)
            dst = os.path.join(APP_DIR, item)
            
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        shutil.rmtree(extract_dir)
        os.remove(zip_path)
        
        return True
    
    except Exception as e:
        print(f"Error installing update: {e}")
        return False

class UpdaterUI:
    """UI for the updater"""
    
    def __init__(self, root):
        """Initialize the updater UI"""
        self.root = root
        self.root.title("Aerout SpeedAutoClicker Updater")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = ttk.Label(self.main_frame, text="Aerout SpeedAutoClicker Updater", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        self.status_var = tk.StringVar(value="Checking for updates...")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, wraplength=460)
        self.status_label.pack(pady=10)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, length=460, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.notes_frame = ttk.LabelFrame(self.main_frame, text="Release Notes", padding=10)
        self.notes_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.notes_text = tk.Text(self.notes_frame, height=10, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        self.notes_text.config(state=tk.DISABLED)

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.update_button = ttk.Button(self.button_frame, text="Update", command=self.start_update, state=tk.DISABLED)
        self.update_button.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=self.root.destroy)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)

        self.root.after(500, self.check_updates)
    
    def check_updates(self):
        """Check for updates"""
        try:
            self.status_var.set("Checking for updates...")
            self.progress_var.set(0)

            update_info = check_for_updates()
            
            if "error" in update_info:
                self.status_var.set(f"Error: {update_info['error']}")
                return
            
            if update_info["available"]:
                self.status_var.set(f"Update available: v{update_info['latest_version']} (Current: v{update_info['current_version']})")
                self.update_button.config(state=tk.NORMAL)

                self.notes_text.config(state=tk.NORMAL)
                self.notes_text.delete(1.0, tk.END)
                self.notes_text.insert(tk.END, update_info["release_notes"])
                self.notes_text.config(state=tk.DISABLED)

                self.download_url = update_info["download_url"]
            else:
                self.status_var.set(f"You have the latest version (v{update_info['current_version']})")
        
        except Exception as e:
            self.status_var.set(f"Error checking for updates: {e}")
    
    def update_progress(self, progress):
        """Update the progress bar"""
        self.progress_var.set(progress)
        self.root.update_idletasks()
    
    def start_update(self):
        """Start the update process"""
        try:
            self.update_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.DISABLED)

            self.status_var.set("Downloading update...")
            self.progress_var.set(0)
            
            zip_path = download_update(self.download_url, self.update_progress)
            if not zip_path:
                self.status_var.set("Error downloading update")
                self.cancel_button.config(state=tk.NORMAL)
                return

            self.status_var.set("Installing update...")
            self.progress_var.set(0)
            
            success = install_update(zip_path, self.update_progress)
            if not success:
                self.status_var.set("Error installing update")
                self.cancel_button.config(state=tk.NORMAL)
                return

            self.status_var.set("Update complete! Restarting application...")
            self.progress_var.set(100)

            self.root.after(2000, self.restart_app)
        
        except Exception as e:
            self.status_var.set(f"Error during update: {e}")
            self.cancel_button.config(state=tk.NORMAL)
    
    def restart_app(self):
        """Restart the application"""
        try:
            subprocess.Popen([sys.executable, os.path.join(APP_DIR, "autoclicker.py")])

            self.root.destroy()
        
        except Exception as e:
            self.status_var.set(f"Error restarting application: {e}")
            self.cancel_button.config(state=tk.NORMAL)

def main():
    """Main function"""
    root = tk.Tk()
    app = UpdaterUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
