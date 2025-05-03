#!/usr/bin/env python3
# STILL IN BETA - NOT 100% SURE IF IT WORKS D:
import os
import sys
import time
import json
import shutil
import urllib.request
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

GITHUB_REPO = "wrealaero/SpeedAutoClicker-Mac"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"
FILES_TO_UPDATE = [
    "autoclicker.py",
    "updater.py",
    "install.sh",
    "requirements.txt",
    "README.md"
]

class UpdaterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AeroutClicker Updater")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure("TFrame", padding=10)
        self.style.configure("TLabel", padding=5)
        self.style.configure("TProgressbar", thickness=10)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(
            main_frame, 
            text="AeroutClicker Updater",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(10, 20))

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=10)
        
        self.status_var = tk.StringVar(value="Preparing to update...")
        status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            font=("Arial", 10)
        )
        status_label.pack(anchor="w")

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            mode="determinate",
            length=350
        )
        self.progress_bar.pack(pady=20)

        self.file_var = tk.StringVar(value="")
        file_label = ttk.Label(
            main_frame, 
            textvariable=self.file_var,
            font=("Arial", 9, "italic")
        )
        file_label.pack(anchor="w")

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(20, 10))
        
        self.cancel_button = ttk.Button(
            buttons_frame, 
            text="Cancel",
            command=self.cancel_update
        )
        self.cancel_button.pack(side="right")

        self.root.protocol("WM_DELETE_WINDOW", self.cancel_update)

        self.root.after(500, self.start_update)
    
    def update_status(self, text):
        """Update the status text"""
        self.status_var.set(text)
        self.root.update_idletasks()
    
    def update_file_progress(self, filename):
        """Update the current file being processed"""
        self.file_var.set(f"Updating: {filename}")
        self.root.update_idletasks()
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def cancel_update(self):
        """Handle cancel button click or window close"""
        result = messagebox.askyesno(
            "Cancel Update",
            "Are you sure you want to cancel the update?\n\n"
            "The application may be in an inconsistent state."
        )
        
        if result:
            self.root.destroy()
            sys.exit(0)
    
    def show_error(self, message):
        """Show error message and exit"""
        messagebox.showerror("Update Error", message)
        self.root.destroy()
        sys.exit(1)
    
    def complete_update(self):
        """Show completion message and exit"""
        messagebox.showinfo(
            "Update Complete",
            "AeroutClicker has been successfully updated!\n\n"
            "The application will now restart."
        )

        try:
            subprocess.Popen([sys.executable, "autoclicker.py"])
        except Exception:
            pass
        
        self.root.destroy()
        sys.exit(0)
    
    def start_update(self):
        """Start the update process"""
        try:
            self.update_status("Checking for updates...")
            self.update_progress(10)

            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            self.update_status("Creating backup...")
            self.update_progress(20)
            
            for file in FILES_TO_UPDATE:
                if os.path.exists(file):
                    self.update_file_progress(file)
                    shutil.copy2(file, os.path.join(backup_dir, file))

            self.update_status("Downloading updates...")
            self.update_progress(30)
            
            total_files = len(FILES_TO_UPDATE)
            for i, file in enumerate(FILES_TO_UPDATE):
                progress = 30 + (i / total_files * 60)
                self.update_progress(progress)
                self.update_file_progress(file)

                file_url = f"{GITHUB_RAW}/{file}"
                try:
                    req = urllib.request.Request(file_url)
                    req.add_header('User-Agent', 'AeroutClicker-Updater')
                    with urllib.request.urlopen(req, timeout=10) as response:
                        content = response.read()

                    with open(file, 'wb') as f:
                        f.write(content)

                    time.sleep(0.5)
                    
                except Exception as e:
                    self.show_error(f"Failed to download {file}: {str(e)}")

            self.update_status("Setting permissions...")
            self.update_progress(95)
            
            for file in ["autoclicker.py", "updater.py", "install.sh"]:
                if os.path.exists(file):
                    try:
                        os.chmod(file, 0o755) 
                    except Exception:
                        pass

            self.update_status("Update completed successfully!")
            self.update_progress(100)

            self.root.after(1000, self.complete_update)
            
        except Exception as e:
            self.show_error(f"Update failed: {str(e)}")
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

if __name__ == "__main__":
    updater = UpdaterGUI()
    updater.run()
