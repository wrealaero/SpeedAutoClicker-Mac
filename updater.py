#!/usr/bin/env python3
# Please tell me this works saw this online, yt, and on some other githubs please work please for the love of god works 
"""
SpeedAutoClicker Updater
Handles automatic updates from GitHub repository.
"""

import os
import sys
import time
import json
import shutil
import urllib.request
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

VERSION = "1.0.1"
GITHUB_REPO = "wrealaero/SpeedAutoClicker-Mac"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"
FILES_TO_UPDATE = [
    "autoclicker.py",
    "updater.py",
    "install.sh",
    "requirements.txt",
    "README.md"
]

class UpdaterGUI:
    """GUI for the updater application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"SpeedAutoClicker Updater v{VERSION}")
        self.root.geometry("450x350")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure("TFrame", padding=10)
        self.style.configure("TLabel", padding=5)
        self.style.configure("TProgressbar", thickness=15)
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame, 
            text="SpeedAutoClicker Updater",
            style="Title.TLabel"
        )
        title_label.pack(anchor="center")

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=10)
        
        self.status_var = tk.StringVar(value="Preparing to update...")
        status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            font=("Arial", 11)
        )
        status_label.pack(anchor="w")

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            mode="determinate",
            length=400
        )
        self.progress_bar.pack(pady=20)

        self.file_var = tk.StringVar(value="")
        file_label = ttk.Label(
            main_frame, 
            textvariable=self.file_var,
            font=("Arial", 10, "italic")
        )
        file_label.pack(anchor="w")

        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        log_label = ttk.Label(
            log_frame,
            text="Update Log:",
            font=("Arial", 10, "bold")
        )
        log_label.pack(anchor="w")
        
        self.log_text = tk.Text(
            log_frame,
            height=6,
            width=50,
            font=("Courier", 9),
            wrap="word",
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        self.cancel_button = ttk.Button(
            buttons_frame, 
            text="Cancel",
            command=self.cancel_update
        )
        self.cancel_button.pack(side="right")

        self.root.protocol("WM_DELETE_WINDOW", self.cancel_update)

        self.root.after(1000, self.start_update)

        self.updating = False
        self.cancelled = False
    
    def log(self, message):
        """Add a message to the log"""
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update()
    
    def update_status(self, message):
        """Update the status message"""
        self.status_var.set(message)
        self.root.update()
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_var.set(value)
        self.root.update()
    
    def update_file(self, filename):
        """Update the current file being processed"""
        self.file_var.set(f"Processing: {filename}")
        self.root.update()
    
    def cancel_update(self):
        """Cancel the update process"""
        if self.updating:
            result = messagebox.askyesno(
                "Cancel Update",
                "Are you sure you want to cancel the update?\n\n"
                "This may leave your installation in an inconsistent state."
            )
            
            if result:
                self.cancelled = True
                self.update_status("Update cancelled.")
                self.log("Update cancelled by user.")
                self.root.after(2000, self.root.destroy)
        else:
            self.root.destroy()
    
    def start_update(self):
        """Start the update process"""
        self.updating = True
        self.cancelled = False
        
        try:
            self.update_status("Checking for latest version...")
            self.update_progress(5)
            
            latest_version, download_url = self.get_latest_version()
            if not latest_version:
                self.update_status("Failed to get latest version information.")
                self.log("Error: Could not retrieve version information from GitHub.")
                self.finish_update(False)
                return
            
            self.log(f"Latest version: {latest_version}")
            self.update_progress(10)
            
            if self.cancelled:
                return

            backup_dir = self.create_backup()
            if not backup_dir:
                self.update_status("Failed to create backup.")
                self.log("Error: Could not create backup directory.")
                self.finish_update(False)
                return
            
            self.log(f"Created backup in: {backup_dir}")
            self.update_progress(20)
            
            if self.cancelled:
                return

            success = self.update_files()
            if not success:
                self.update_status("Update failed. Restoring backup...")
                self.log("Error during update. Restoring from backup...")
                self.restore_backup(backup_dir)
                self.finish_update(False)
                return
            
            self.update_progress(95)

            try:
                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)
                self.log("Backup cleaned up successfully.")
            except Exception as e:
                self.log(f"Warning: Could not clean up backup: {str(e)}")
            
            self.update_progress(100)
            self.update_status("Update completed successfully!")
            self.log("Update completed successfully.")
            self.finish_update(True)
            
        except Exception as e:
            self.update_status(f"Update failed: {str(e)}")
            self.log(f"Error: {str(e)}")
            self.finish_update(False)
    
    def get_latest_version(self):
        """Get the latest version information from GitHub"""
        try:
            req = urllib.request.Request(
                f"{GITHUB_API}/releases/latest",
                headers={"User-Agent": f"SpeedAutoClicker-Updater/{VERSION}"}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").lstrip("v")
                download_url = data.get("zipball_url")
                
                return latest_version, download_url
        except Exception as e:
            self.log(f"Error getting latest version: {str(e)}")
            return None, None
    
    def create_backup(self):
        """Create a backup of the current installation"""
        try:
            self.update_status("Creating backup...")

            current_dir = os.path.dirname(os.path.abspath(__file__))

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(current_dir, f"backup_{timestamp}")
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            for filename in FILES_TO_UPDATE:
                src_path = os.path.join(current_dir, filename)
                if os.path.exists(src_path):
                    self.update_file(filename)
                    shutil.copy2(src_path, os.path.join(backup_dir, filename))
            
            return backup_dir
        except Exception as e:
            self.log(f"Error creating backup: {str(e)}")
            return None
    
    def restore_backup(self, backup_dir):
        """Restore files from backup"""
        try:
            self.update_status("Restoring from backup...")
            
            if not os.path.exists(backup_dir):
                self.log("Error: Backup directory not found.")
                return False

            current_dir = os.path.dirname(os.path.abspath(__file__))

            for filename in FILES_TO_UPDATE:
                backup_path = os.path.join(backup_dir, filename)
                if os.path.exists(backup_path):
                    self.update_file(filename)
                    shutil.copy2(backup_path, os.path.join(current_dir, filename))
            
            self.log("Restored from backup successfully.")
            return True
        except Exception as e:
            self.log(f"Error restoring backup: {str(e)}")
            return False
    
    def update_files(self):
        """Download and update all files"""
        try:
            self.update_status("Downloading updates...")

            current_dir = os.path.dirname(os.path.abspath(__file__))

            total_files = len(FILES_TO_UPDATE)
            for i, filename in enumerate(FILES_TO_UPDATE):
                if self.cancelled:
                    return False
                
                progress = 20 + (i / total_files) * 70
                self.update_progress(progress)
                self.update_file(filename)

                file_url = f"{GITHUB_RAW}/{filename}"
                try:
                    req = urllib.request.Request(
                        file_url,
                        headers={"User-Agent": f"SpeedAutoClicker-Updater/{VERSION}"}
                    )
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        content = response.read()

                        file_path = os.path.join(current_dir, filename)
                        with open(file_path, 'wb') as f:
                            f.write(content)
                        
                        self.log(f"Updated: {filename}")
                except Exception as e:
                    self.log(f"Error updating {filename}: {str(e)}")
                    return False
            
            return True
        except Exception as e:
            self.log(f"Error updating files: {str(e)}")
            return False
    
    def finish_update(self, success):
        """Finish the update process"""
        self.updating = False
        
        if success:
            self.cancel_button.config(text="Close")

            result = messagebox.askyesno(
                "Update Complete",
                "Update completed successfully!\n\n"
                "Would you like to restart SpeedAutoClicker now?"
            )
            
            if result:
                self.restart_application()
            else:
                self.root.after(2000, self.root.destroy)
        else:
            self.cancel_button.config(text="Close")
            
            messagebox.showerror(
                "Update Failed",
                "The update process encountered errors.\n\n"
                "Please check the log for details."
            )
    
    def restart_application(self):
        """Restart the main application"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            main_script = os.path.join(current_dir, "autoclicker.py")
            
            if os.path.exists(main_script):
                self.root.destroy()

                subprocess.Popen([sys.executable, main_script])
        except Exception as e:
            messagebox.showerror(
                "Restart Failed",
                f"Failed to restart the application: {str(e)}\n\n"
                "Please start SpeedAutoClicker manually."
            )
            self.root.destroy()
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

def main():
    """Main entry point for the updater"""
    try:
        gui = UpdaterGUI()
        gui.run()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror(
            "Error",
            f"An error occurred: {str(e)}\n\n"
            "Please download the latest version manually."
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
