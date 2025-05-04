#!/usr/bin/env python3
"""
Updater for Aerout SpeedAutoClicker
Helps with handling downloades and installing updates
"""

import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
import urllib.request
import tkinter as tk
from tkinter import ttk
from threading import Thread

GITHUB_REPO = "wrealaero/SpeedAutoClicker-Mac"
APP_NAME = "AeroutClicker"

class UpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aerout SpeedAutoClicker Updater")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.create_ui()

        self.update_thread = Thread(target=self.update_process, daemon=True)
        self.update_thread.start()
    
    def create_ui(self):
        """Create the updater UI"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Updating Aerout SpeedAutoClicker", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)

        self.status_var = tk.StringVar(value="Checking for updates...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=350)
        status_label.pack(pady=10)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, length=350, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.detail_var = tk.StringVar(value="")
        detail_label = ttk.Label(main_frame, textvariable=self.detail_var, wraplength=350, foreground="gray")
        detail_label.pack(pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill=tk.X)

        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_update)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def update_status(self, message):
        """Update the status message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def update_detail(self, message):
        """Update the detail message"""
        self.detail_var.set(message)
        self.root.update_idletasks()
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def cancel_update(self):
        """Cancel the update process"""
        self.update_status("Update cancelled")
        self.root.after(1000, self.root.destroy)
    
    def update_process(self):
        """Main update process"""
        try:
            self.update_status("Checking for updates...")
            self.update_progress(10)
            
            latest_release = self.get_latest_release()
            if not latest_release:
                self.update_status("Failed to get update information")
                self.update_detail("Please try again later or download manually from GitHub")
                return
            
            self.update_progress(20)
            self.update_status(f"Found version {latest_release['tag_name']}")
            self.update_detail("Preparing to download...")

            self.update_status("Downloading update...")
            download_url = self.get_download_url(latest_release)
            if not download_url:
                self.update_status("Failed to find download URL")
                self.update_detail("Please download manually from GitHub")
                return
            
            self.update_detail(f"Downloading from {download_url}")
            download_path = self.download_file(download_url)
            if not download_path:
                self.update_status("Download failed")
                self.update_detail("Please check your internet connection and try again")
                return
            
            self.update_progress(70)
            self.update_status("Download complete")
            self.update_detail("Preparing to install...")

            self.update_status("Installing update...")
            self.update_detail("This may take a moment...")
            success = self.install_update(download_path)
            
            if success:
                self.update_progress(100)
                self.update_status("Update completed successfully!")
                self.update_detail("The application will restart momentarily...")

                self.cancel_btn.config(text="Close", command=self.restart_app)

                self.root.after(3000, self.restart_app)
            else:
                self.update_status("Update failed")
                self.update_detail("Please try again or download manually from GitHub")
        
        except Exception as e:
            self.update_status(f"Error during update: {str(e)}")
            self.update_detail("Please try again later or download manually")
    
    def get_latest_release(self):
        """Get information about the latest release from GitHub"""
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                headers={"User-Agent": f"{APP_NAME}/Updater"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        
        except Exception as e:
            self.update_detail(f"Error checking for updates: {str(e)}")
            return None
    
    def get_download_url(self, release_data):
        """Extract the download URL from the release data"""
        try:
            for asset in release_data.get("assets", []):
                name = asset.get("name", "").lower()

                if sys.platform == 'darwin' and ("mac" in name or "macos" in name or ".dmg" in name or ".zip" in name):
                    return asset.get("browser_download_url")

                elif sys.platform == 'win32' and ("win" in name or "windows" in name or ".exe" in name or ".zip" in name):
                    return asset.get("browser_download_url")

            return release_data.get("zipball_url")
        
        except Exception as e:
            self.update_detail(f"Error finding download URL: {str(e)}")
            return None
    
    def download_file(self, url):
        """Download a file from the given URL"""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
            temp_file.close()

            def report_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(block_num * block_size * 100 / total_size, 70)
                    self.update_progress(20 + percent * 0.5)  # Scale to 20-70% range
                    self.update_detail(f"Downloaded {block_num * block_size / 1024:.1f} KB of {total_size / 1024:.1f} KB")

            urllib.request.urlretrieve(url, temp_file.name, reporthook=report_progress)
            
            return temp_file.name
        
        except Exception as e:
            self.update_detail(f"Error downloading update: {str(e)}")
            return None
    
    def install_update(self, download_path):
        """Install the downloaded update"""
        try:
            temp_dir = tempfile.mkdtemp()

            self.update_detail("Extracting files...")
            shutil.unpack_archive(download_path, temp_dir)

            app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

            extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
            if extracted_dirs:
                extracted_dir = os.path.join(temp_dir, extracted_dirs[0])
            else:
                extracted_dir = temp_dir

            self.update_detail("Copying new files...")
            self.update_progress(80)

            for file in os.listdir(extracted_dir):
                if file.endswith(".py") or file == "requirements.txt":
                    src = os.path.join(extracted_dir, file)
                    dst = os.path.join(app_dir, file)
                    shutil.copy2(src, dst)

            self.update_detail("Cleaning up...")
            self.update_progress(90)
            try:
                os.unlink(download_path)
                shutil.rmtree(temp_dir)
            except:
                pass
            
            return True
        
        except Exception as e:
            self.update_detail(f"Error installing update: {str(e)}")
            return False
    
    def restart_app(self):
        """Restart the application"""
        try:
            app_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "autoclicker.py"))

            if sys.platform == 'darwin': 
                subprocess.Popen(["python3", app_path])
            else:
                subprocess.Popen([sys.executable, app_path])

            self.root.destroy()
        
        except Exception as e:
            self.update_detail(f"Error restarting application: {str(e)}")

def main():
    """Main entry point for the updater"""
    root = tk.Tk()
    app = UpdaterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
