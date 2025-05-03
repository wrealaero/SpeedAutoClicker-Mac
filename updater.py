#!/usr/bin/env python3

import os
import sys
import time
import json
import shutil
import tempfile
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

VERSION = "1.0.0"
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
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"SpeedAutoClicker Updater v{VERSION}")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure("TFrame", padding=5)
        self.style.configure("TLabel", padding=2)
        self.style.configure("TButton", padding=5)
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"), padding=10)
        self.style.configure("TProgressbar", thickness=15)

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(main_frame, text="SpeedAutoClicker Updater", style="Title.TLabel")
        title_label.pack(fill="x", pady=(0, 20))

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=10)

        self.status_var = tk.StringVar(value="Preparing to update...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(anchor="w")

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, mode="determinate", length=450)
        self.progress_bar.pack(pady=20)

        self.file_var = tk.StringVar(value="")
        file_label = ttk.Label(main_frame, textvariable=self.file_var, font=("Arial", 9, "italic"))
        file_label.pack(anchor="w")

        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=10)

        log_label = ttk.Label(log_frame, text="Update Log:", anchor="w")
        log_label.pack(fill="x")

        self.log_text = tk.Text(log_frame, height=8, width=50, wrap="word")
        self.log_text.pack(side="left", fill="both", expand=True)

        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=log_scrollbar.set)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(20, 0))

        self.cancel_button = ttk.Button(buttons_frame, text="Cancel", command=self.cancel_update)
        self.cancel_button.pack(side="right")

        self.root.protocol("WM_DELETE_WINDOW", self.cancel_update)
        self.root.after(500, self.start_update)

    def update_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()

    def update_file_progress(self, filename):
        self.file_var.set(f"Updating: {filename}")
        self.root.update_idletasks()

    def update_progress(self, value):
        self.progress_var.set(value)
        self.root.update_idletasks()

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def cancel_update(self):
        result = messagebox.askyesno(
            "Cancel Update",
            "Are you sure you want to cancel the update?\n\n"
            "The application may be in an inconsistent state."
        )
        if result:
            self.log("Update cancelled by user")
            self.root.destroy()
            sys.exit(0)

    def show_error(self, message):
        self.log(f"ERROR: {message}")
        messagebox.showerror("Update Error", message)
        self.root.destroy()
        sys.exit(1)

    def complete_update(self):
        self.log("Update completed successfully")
        messagebox.showinfo(
            "Update Complete",
            "SpeedAutoClicker has been successfully updated!\n\n"
            "The application will now restart."
        )
        try:
            subprocess.Popen([sys.executable, "autoclicker.py"])
        except Exception as e:
            self.log(f"Failed to restart application: {e}")
        self.root.destroy()
        sys.exit(0)

    def start_update(self):
        try:
            try:
                import urllib.request
                import json
            except ImportError as e:
                self.show_error(
                    f"Could not import required modules: {str(e)}\n"
                    "Please make sure you have the required dependencies installed."
                )
                return

            if not os.path.exists("autoclicker.py"):
                self.show_error(
                    "Updater must be run from the SpeedAutoClicker directory.\n"
                    "Please run the updater from the correct location."
                )
                return

            backup_dir = os.path.join(tempfile.gettempdir(), f"speedautoclicker_backup_{int(time.time())}")
            os.makedirs(backup_dir, exist_ok=True)
            self.log(f"Created backup directory: {backup_dir}")

            self.update_status("Creating backup...")
            self.update_progress(10)

            for file in FILES_TO_UPDATE:
                if os.path.exists(file):
                    self.update_file_progress(file)
                    shutil.copy2(file, os.path.join(backup_dir, file))
                    self.log(f"Backed up: {file}")

            self.update_status("Checking for latest version...")
            self.update_progress(20)

            try:
                req = urllib.request.Request(
                    f"{GITHUB_API}/releases/latest",
                    headers={'User-Agent': f'SpeedAutoClicker-Updater/{VERSION}'}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    release_data = json.loads(response.read().decode('utf-8'))
                    latest_version = release_data.get('tag_name', '').lstrip('v')
                    if not latest_version:
                        self.show_error("Could not determine latest version")
                        return
                    self.log(f"Latest version: {latest_version}")
                    self.update_status(f"Updating to version {latest_version}...")
            except Exception as e:
                self.show_error(f"Failed to get latest release info: {str(e)}")
                return

            self.update_progress(30)
            total_files = len(FILES_TO_UPDATE)
            progress_per_file = 60 / total_files

            for i, file in enumerate(FILES_TO_UPDATE):
                try:
                    self.update_file_progress(file)
                    file_url = f"{GITHUB_RAW}/{file}"
                    self.log(f"Downloading: {file}")
                    req = urllib.request.Request(
                        file_url,
                        headers={'User-Agent': f'SpeedAutoClicker-Updater/{VERSION}'}
                    )
                    with urllib.request.urlopen(req, timeout=10) as response:
                        content = response.read()
                        with open(file, 'wb') as f:
                            f.write(content)
                        self.log(f"Updated: {file}")
                except Exception as e:
                    self.log(f"Error updating {file}: {str(e)}")
                    try:
                        backup_file = os.path.join(backup_dir, file)
                        if os.path.exists(backup_file):
                            shutil.copy2(backup_file, file)
                            self.log(f"Restored {file} from backup")
                    except Exception as restore_error:
                        self.log(f"Failed to restore {file}: {str(restore_error)}")
                progress = 30 + (i + 1) * progress_per_file
                self.update_progress(progress)

            self.update_status("Finalizing update...")
            self.update_progress(90)

            try:
                if os.path.exists("autoclicker.py"):
                    with open("autoclicker.py", 'r') as f:
                        content = f.read()
                    content = content.replace(f'VERSION = "{VERSION}"', f'VERSION = "{latest_version}"')
                    with open("autoclicker.py", 'w') as f:
                        f.write(content)
                    self.log("Updated version in autoclicker.py")

                if os.path.exists("updater.py"):
                    with open("updater.py", 'r') as f:
                        content = f.read()
                    content = content.replace(f'VERSION = "{VERSION}"', f'VERSION = "{latest_version}"')
                    with open("updater.py", 'w') as f:
                        f.write(content)
                    self.log("Updated version in updater.py")
            except Exception as e:
                self.log(f"Error updating version strings: {str(e)}")

            self.update_progress(95)

            try:
                if sys.platform == 'darwin' or sys.platform.startswith('linux'):
                    for script in ["autoclicker.py", "updater.py", "install.sh"]:
                        if os.path.exists(script):
                            os.chmod(script, 0o755)
                            self.log(f"Made {script} executable")
            except Exception as e:
                self.log(f"Error making scripts executable: {str(e)}")

            self.update_status("Update completed successfully!")
            self.update_progress(100)

            self.cancel_button.config(text="Finish", command=self.complete_update)
            self.root.after(1500, self.complete_update)
        except Exception as e:
            self.show_error(f"An unexpected error occurred: {str(e)}")

    def run(self):
        self.root.mainloop()

def main():
    try:
        updater = UpdaterGUI()
        updater.run()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
