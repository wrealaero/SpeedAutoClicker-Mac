#!/usr/bin/env python3
import os
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, font, messagebox
import webbrowser
import platform
import subprocess
import sys
from pynput import keyboard, mouse

try:
    import updater
    UPDATER_AVAILABLE = True
except ImportError:
    UPDATER_AVAILABLE = False

IS_APPLE_SILICON = platform.machine() == 'arm64'

try:
    from Quartz.CoreGraphics import (
        CGEventCreateMouseEvent, CGEventPost, CGEventCreate, CGEventGetLocation,
        kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGEventRightMouseDown, 
        kCGEventRightMouseUp, kCGEventOtherMouseDown, kCGEventOtherMouseUp,
        kCGMouseButtonLeft, kCGMouseButtonRight, kCGMouseButtonCenter, kCGHIDEventTap
    )
except ImportError:
    print("Error: Required Quartz modules not found.")
    print("Please run the install script: ./install.sh")
    sys.exit(1)

SETTINGS_PATH = os.path.expanduser("~/.aeroutclicker_settings.json")
VERSION = "1.1.0"
DISCORD_URL = "https://discord.gg/MxGV8fGzpR"

def load_settings():
    defaults = {
        "interval_ms": 100.0, 
        "duty_cycle": 50.0,
        "click_limit": 0,     
        "limit_enabled": False,
        "mouse_button": "left",
        "mode": "toggle",   
        "hotkey": {"type": "keyboard", "keys": ["f6"]}
    }
    
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r') as f:
                user_settings = json.load(f)
                defaults.update(user_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    return defaults

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Error saving settings: {e}")

class AutoClicker:
    def __init__(self):
        self.settings = load_settings()
        self.clicking = False
        self.click_thread = None
        self.click_count = 0
        self.current_keys = set()
        self.capturing_hotkey = False
        self.capture_keys = set()
        self.last_combo = set()
        self.overlay = None

        self.kb_listener = keyboard.Listener(
            on_press=self.on_key_press, 
            on_release=self.on_key_release, 
            daemon=True
        )
        self.kb_listener.start()

        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click, 
            daemon=True
        )
        self.mouse_listener.start()
    
    def get_mouse_position(self):
        try:
            ev = CGEventCreate(None)
            loc = CGEventGetLocation(ev)
            return loc.x, loc.y
        except Exception as e:
            print(f"Error getting mouse position: {e}")
            return 0, 0
    
    def mouse_click(self, button="left"):
        try:
            x, y = self.get_mouse_position()
            
            if button == "left":
                down_event = kCGEventLeftMouseDown
                up_event = kCGEventLeftMouseUp
                button_code = kCGMouseButtonLeft
            elif button == "right":
                down_event = kCGEventRightMouseDown
                up_event = kCGEventRightMouseUp
                button_code = kCGMouseButtonRight
            elif button == "middle":
                down_event = kCGEventOtherMouseDown
                up_event = kCGEventOtherMouseUp
                button_code = kCGMouseButtonCenter
            else:
                down_event = kCGEventLeftMouseDown
                up_event = kCGEventLeftMouseUp
                button_code = kCGMouseButtonLeft

            interval_ms = float(self.settings["interval_ms"])
            duty_cycle = float(self.settings["duty_cycle"])

            interval_sec = interval_ms / 1000.0

            hold_time = interval_sec * (duty_cycle / 100.0)
            release_time = interval_sec - hold_time

            ev_down = CGEventCreateMouseEvent(None, down_event, (x, y), button_code)
            CGEventPost(kCGHIDEventTap, ev_down)

            time.sleep(max(0.001, hold_time))

            ev_up = CGEventCreateMouseEvent(None, up_event, (x, y), button_code)
            CGEventPost(kCGHIDEventTap, ev_up)

            time.sleep(max(0.001, release_time))
            
            return True
        except Exception as e:
            print(f"Error during mouse click: {e}")
            return False
    
    def click_loop(self):
        limit = int(self.settings["click_limit"]) if self.settings["limit_enabled"] else 0
        self.click_count = 0
        
        while self.clicking:
            success = self.mouse_click(self.settings["mouse_button"])
            if success:
                self.click_count += 1
                
            if limit > 0 and self.click_count >= limit:
                self.clicking = False
                if hasattr(self, 'gui'):
                    self.gui.update_status("Stopped (Limit reached)")
                    self.gui.toggle_button.config(text="Start")
                break
    
    def start_clicking(self):
        if not self.clicking:
            self.clicking = True
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()
            if hasattr(self, 'gui'):
                self.gui.update_status("Clicking...")
                self.gui.toggle_button.config(text="Stop")
    
    def stop_clicking(self):
        self.clicking = False
        if hasattr(self, 'gui'):
            self.gui.update_status("Stopped")
            self.gui.toggle_button.config(text="Start")
    
    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def on_key_press(self, key):
        if self.capturing_hotkey:
            try:
                if hasattr(key, 'char') and key.char:
                    name = key.char.lower()
                else:
                    name = key.name.lower() if hasattr(key, 'name') else str(key).lower().replace("key.", "")
                
                self.capture_keys.add(name)
                self.last_combo = self.capture_keys.copy()
            except AttributeError:
                pass
            return

        try:
            if hasattr(key, 'char') and key.char:
                name = key.char.lower()
            else:
                name = key.name.lower() if hasattr(key, 'name') else str(key).lower().replace("key.", "")
            
            self.current_keys.add(name)
            if self.settings["hotkey"]["type"] == "keyboard":
                hotkey_keys = set(self.settings["hotkey"]["keys"])
                if hotkey_keys and hotkey_keys.issubset(self.current_keys):
                    if self.settings["mode"] == "toggle":
                        self.toggle_clicking()
                    else: 
                        self.start_clicking()
        except AttributeError:
            pass
    
    def on_key_release(self, key):
        if self.capturing_hotkey:
            try:
                if hasattr(key, 'char') and key.char:
                    name = key.char.lower()
                else:
                    name = key.name.lower() if hasattr(key, 'name') else str(key).lower().replace("key.", "")
                
                self.capture_keys.discard(name)
                if not self.capture_keys and self.last_combo:
                    self.settings["hotkey"] = {
                        "type": "keyboard", 
                        "keys": sorted(list(self.last_combo))
                    }
                    save_settings(self.settings)
                    self.capturing_hotkey = False
                    
                    if self.overlay:
                        self.overlay.destroy()
                        self.overlay = None
                    
                    if hasattr(self, 'gui'):
                        self.gui.update_hotkey_display()
            except AttributeError:
                pass
            return

        try:
            if hasattr(key, 'char') and key.char:
                name = key.char.lower()
            else:
                name = key.name.lower() if hasattr(key, 'name') else str(key).lower().replace("key.", "")
            
            self.current_keys.discard(name)
            if (self.settings["mode"] == "hold" and 
                self.settings["hotkey"]["type"] == "keyboard"):
                
                hotkey_keys = set(self.settings["hotkey"]["keys"])
                if not hotkey_keys.issubset(self.current_keys):
                    self.stop_clicking()
        except AttributeError:
            pass
    
    def on_mouse_click(self, x, y, button, pressed):
        button_name = str(button).lower().replace("button.", "")
        if self.clicking and button_name == self.settings["mouse_button"]:
            return
        
        if self.settings["hotkey"]["type"] == "mouse" and button_name == self.settings["hotkey"]["button"]:
            if self.settings["mode"] == "toggle" and pressed:
                self.toggle_clicking()
            elif self.settings["mode"] == "hold":
                if pressed:
                    self.start_clicking()
                else:
                    self.stop_clicking()
    
    def start_hotkey_capture(self):
        if self.capturing_hotkey:
            return
        
        self.capturing_hotkey = True
        self.capture_keys = set()
        self.last_combo = set()
        if hasattr(self, 'gui'):
            self.overlay = tk.Toplevel(self.gui.root)
            self.overlay.attributes("-topmost", True)
            self.overlay.geometry("400x200")
            self.overlay.title("Capturing Hotkey")
            self.overlay.update_idletasks()
            width = self.overlay.winfo_width()
            height = self.overlay.winfo_height()
            x = (self.overlay.winfo_screenwidth() // 2) - (width // 2)
            y = (self.overlay.winfo_screenheight() // 2) - (height // 2)
            self.overlay.geometry(f"{width}x{height}+{x}+{y}")
            
            self.overlay.configure(bg="#333333")
            
            label = tk.Label(
                self.overlay,
                text="Press key combination for hotkey\n(Press and release keys)",
                font=("Arial", 14),
                fg="white",
                bg="#333333",
                pady=20
            )
            label.pack(fill="both", expand=True)
            cancel_btn = tk.Button(
                self.overlay,
                text="Cancel",
                command=self.cancel_hotkey_capture,
                bg="#FF5555",
                fg="white",
                padx=10,
                pady=5
            )
            cancel_btn.pack(pady=20)
    
    def cancel_hotkey_capture(self):
        self.capturing_hotkey = False
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

class AutoClickerGUI:
    def __init__(self, clicker):
        self.clicker = clicker
        self.clicker.gui = self
        self.root = tk.Tk()
        self.root.title("SpeedAutoClicker")
        self.root.geometry("400x550") 
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TLabel", font=("Arial", 10), background="#f0f0f0")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TRadiobutton", font=("Arial", 10), background="#f0f0f0")
        
        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill="both", expand=True)
        
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill="x", pady=(0, 15))
        
        title_label = ttk.Label(
            title_frame, 
            text="SpeedAutoClicker",
            font=("Arial", 16, "bold")
        )
        title_label.pack(side="left")
        
        version_label = ttk.Label(
            title_frame, 
            text=f"v{VERSION}",
            font=("Arial", 8)
        )
        version_label.pack(side="right", padx=5, pady=5)

        system_info = "Apple Silicon" if IS_APPLE_SILICON else "Intel"
        system_label = ttk.Label(
            title_frame,
            text=f"({system_info})",
            font=("Arial", 8)
        )
        system_label.pack(side="right", padx=5, pady=5)
        
        self.create_section_label("Click Rate (CPS)")
        
        rate_frame = ttk.Frame(self.main_frame)
        rate_frame.pack(fill="x", pady=5)
        
        self.interval_var = tk.StringVar(value=str(self.clicker.settings["interval_ms"]))
        self.interval_entry = ttk.Entry(rate_frame, textvariable=self.interval_var, width=10)
        self.interval_entry.pack(side="left", padx=(0, 5))
        
        ttk.Label(rate_frame, text="ms").pack(side="left")
        
        self.cps_label = ttk.Label(rate_frame, text="= 10.00 CPS")
        self.cps_label.pack(side="right")
        
        self.create_section_label("Click Duty Cycle (CDC)")
        
        duty_frame = ttk.Frame(self.main_frame)
        duty_frame.pack(fill="x", pady=5)
        
        self.duty_var = tk.StringVar(value=str(self.clicker.settings["duty_cycle"]))
        self.duty_entry = ttk.Entry(duty_frame, textvariable=self.duty_var, width=10)
        self.duty_entry.pack(side="left", padx=(0, 5))
        
        ttk.Label(duty_frame, text="%").pack(side="left")
        
        duty_info = ttk.Label(duty_frame, text="(Hold time %)")
        duty_info.pack(side="right")
        
        self.create_section_label("Click Limit")
        
        limit_frame = ttk.Frame(self.main_frame)
        limit_frame.pack(fill="x", pady=5)
        
        self.limit_enabled_var = tk.BooleanVar(value=self.clicker.settings["limit_enabled"])
        limit_check = ttk.Checkbutton(
            limit_frame, 
            text="Limit number of clicks",
            variable=self.limit_enabled_var,
            command=self.toggle_limit_entry
        )
        limit_check.pack(side="left")
        
        self.limit_var = tk.StringVar(value=str(self.clicker.settings["click_limit"]))
        self.limit_entry = ttk.Entry(limit_frame, textvariable=self.limit_var, width=10)
        self.limit_entry.pack(side="right")
        
        self.create_section_label("Mouse Button")
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=5)
        
        self.mouse_button_var = tk.StringVar(value=self.clicker.settings["mouse_button"])
        mouse_buttons = ["left", "right", "middle"]
        
        for button in mouse_buttons:
            rb = ttk.Radiobutton(
                button_frame, 
                text=button.capitalize(),
                variable=self.mouse_button_var,
                value=button,
                command=self.update_mouse_button
            )
            rb.pack(side="left", padx=(0, 10))
        
        self.create_section_label("Hotkey Activation Mode")
        
        mode_frame = ttk.Frame(self.main_frame)
        mode_frame.pack(fill="x", pady=5)
        
        self.mode_var = tk.StringVar(value=self.clicker.settings["mode"])
        
        toggle_rb = ttk.Radiobutton(
            mode_frame, 
            text="Toggle Mode (Press once to start, again to stop)",
            variable=self.mode_var,
            value="toggle",
            command=self.update_mode
        )
        toggle_rb.pack(anchor="w", pady=(0, 5))
        
        hold_rb = ttk.Radiobutton(
            mode_frame, 
            text="Hold Mode (Click only while hotkey is held)",
            variable=self.mode_var,
            value="hold",
            command=self.update_mode
        )
        hold_rb.pack(anchor="w")
        
        self.create_section_label("Hotkey Setup")
        
        hotkey_frame = ttk.Frame(self.main_frame)
        hotkey_frame.pack(fill="x", pady=5)
        
        self.hotkey_display = ttk.Label(
            hotkey_frame, 
            text=self.format_hotkey_display(),
            font=("Arial", 10, "bold")
        )
        self.hotkey_display.pack(side="left", padx=(0, 10))
        
        self.hotkey_button = ttk.Button(
            hotkey_frame, 
            text="Set Hotkey",
            command=self.clicker.start_hotkey_capture
        )
        self.hotkey_button.pack(side="right")
        
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill="x", pady=15)
        
        self.toggle_button = ttk.Button(
            control_frame, 
            text="Start",
            command=self.clicker.toggle_clicking,
            style="TButton",
            width=20
        )
        self.toggle_button.pack(pady=5)
        
        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = ttk.Label(
            control_frame, 
            textvariable=self.status_var,
            font=("Arial", 10, "italic")
        )
        self.status_label.pack(pady=5)

        self.counter_var = tk.StringVar(value="Clicks: 0")
        self.counter_label = ttk.Label(
            control_frame,
            textvariable=self.counter_var,
            font=("Arial", 9)
        )
        self.counter_label.pack(pady=2)

        self.counter_thread = threading.Thread(target=self.update_counter, daemon=True)
        self.counter_thread.start()

        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill="x", pady=(15, 5))
        
        discord_button = ttk.Button(
            bottom_frame, 
            text="Join Discord Server",
            command=self.open_discord
        )
        discord_button.pack(side="left")
        
        if UPDATER_AVAILABLE:
            update_button = ttk.Button(
                bottom_frame,
                text="Check for Updates",
                command=self.check_for_updates
            )
            update_button.pack(side="right")
        
        contact_label = ttk.Label(
            self.main_frame, 
            text="DM 5qvx for bugs and issues :D",
            font=("Arial", 9)
        )
        contact_label.pack(side="right", pady=(5, 0))
        
        self.interval_var.trace_add("write", self.update_cps_display)
        self.interval_entry.bind("<FocusOut>", self.validate_interval)
        self.duty_entry.bind("<FocusOut>", self.validate_duty)
        self.limit_entry.bind("<FocusOut>", self.validate_limit)
        
        self.toggle_limit_entry()
        self.update_cps_display()

        if UPDATER_AVAILABLE:
            self.root.after(1000, self.check_for_updates_silently)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def check_for_updates_silently(self):
        """Check for updates without user interaction"""
        if not UPDATER_AVAILABLE:
            return
            
        try:
            updates_available, updated_files = updater.check_for_updates(silent=True)
            if updates_available:
                response = messagebox.askyesno(
                    "Update Available",
                    "A new version of SpeedAutoClicker is available. Would you like to update now?",
                    parent=self.root
                )
                if response:
                    self.perform_update()
        except Exception as e:
            print(f"Error checking for updates: {e}")
    
    def check_for_updates(self):
        """Check for updates with user interaction"""
        if not UPDATER_AVAILABLE:
            messagebox.showinfo(
                "Updates Unavailable",
                "The updater module is not available. Please reinstall the application.",
                parent=self.root
            )
            return
            
        try:
            updates_available, updated_files = updater.check_for_updates()
            if updates_available:
                files_text = "\n".join([f"- {f}" for f in updated_files])
                response = messagebox.askyesno(
                    "Update Available",
                    f"Updates are available for the following files:\n\n{files_text}\n\nWould you like to update now?",
                    parent=self.root
                )
                if response:
                    self.perform_update()
            else:
                messagebox.showinfo(
                    "No Updates Available",
                    "You are using the latest version of SpeedAutoClicker.",
                    parent=self.root
                )
        except Exception as e:
            messagebox.showerror(
                "Update Error",
                f"An error occurred while checking for updates:\n\n{str(e)}",
                parent=self.root
            )
    
    def perform_update(self):
        """Perform the update process"""
        try:

            progress_window = tk.Toplevel(self.root)
            progress_window.title("Updating")
            progress_window.geometry("300x100")
            progress_window.transient(self.root)
            progress_window.grab_set()

            progress_window.update_idletasks()
            width = progress_window.winfo_width()
            height = progress_window.winfo_height()
            x = (progress_window.winfo_screenwidth() // 2) - (width // 2)
            y = (progress_window.winfo_screenheight() // 2) - (height // 2)
            progress_window.geometry(f"{width}x{height}+{x}+{y}")
            
            label = ttk.Label(
                progress_window,
                text="Updating SpeedAutoClicker...\nPlease wait.",
                font=("Arial", 10),
                justify="center"
            )
            label.pack(pady=20)

            def update_thread():
                try:
                    updater.update_application()
                    progress_window.destroy()
                    messagebox.showinfo(
                        "Update Complete",
                        "SpeedAutoClicker has been updated successfully.\nThe application will now restart.",
                        parent=self.root
                    )
                    self.restart_application()
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror(
                        "Update Failed",
                        f"An error occurred during the update:\n\n{str(e)}",
                        parent=self.root
                    )
            
            threading.Thread(target=update_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror(
                "Update Error",
                f"An error occurred during the update process:\n\n{str(e)}",
                parent=self.root
            )
    
    def restart_application(self):
        """Restart the application after update"""
        python = sys.executable
        script = os.path.abspath(__file__)
        self.root.destroy()
        os.execl(python, python, script)
    
    def update_counter(self):
        """Update the click counter in a separate thread"""
        while True:
            if hasattr(self.clicker, 'click_count'):
                self.counter_var.set(f"Clicks: {self.clicker.click_count}")
            time.sleep(0.1)
    
    def create_section_label(self, text):
        """Create a section header label"""
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill="x", pady=(10, 5))
        
        label = ttk.Label(
            frame, 
            text=text,
            font=("Arial", 11, "bold")
        )
        label.pack(anchor="w")
        
        separator = ttk.Separator(frame, orient="horizontal")
        separator.pack(fill="x", pady=(2, 0))
    
    def update_cps_display(self, *args):
        """Update the CPS display based on the interval value"""
        try:
            interval_ms = float(self.interval_var.get())
            if interval_ms <= 0:
                interval_ms = 1.0
                
            cps = 1000.0 / interval_ms
            self.cps_label.config(text=f"= {cps:.2f} CPS")
            self.clicker.settings["interval_ms"] = interval_ms
            save_settings(self.clicker.settings)
        except ValueError:
            pass
    
    def validate_interval(self, event=None):
        """Validate the interval input"""
        try:
            value = float(self.interval_var.get())
            if value <= 0:
                self.interval_var.set("1.0")
                self.clicker.settings["interval_ms"] = 1.0
            else:
                self.clicker.settings["interval_ms"] = value
            save_settings(self.clicker.settings)
        except ValueError:
            self.interval_var.set(str(self.clicker.settings["interval_ms"]))
    
    def validate_duty(self, event=None):
        """Validate the duty cycle input"""
        try:
            value = float(self.duty_var.get())
            if value < 1 or value > 100:
                self.duty_var.set("50.0")
                self.clicker.settings["duty_cycle"] = 50.0
            else:
                self.clicker.settings["duty_cycle"] = value
            save_settings(self.clicker.settings)
        except ValueError:
            self.duty_var.set(str(self.clicker.settings["duty_cycle"]))
    
    def validate_limit(self, event=None):
        """Validate the click limit input"""
        try:
            value = int(self.limit_var.get())
            if value < 0:
                self.limit_var.set("0")
                self.clicker.settings["click_limit"] = 0
            else:
                self.clicker.settings["click_limit"] = value
            save_settings(self.clicker.settings)
        except ValueError:
            self.limit_var.set(str(self.clicker.settings["click_limit"]))
    
    def toggle_limit_entry(self):
        """Enable/disable the limit entry based on checkbox"""
        enabled = self.limit_enabled_var.get()
        self.limit_entry.config(state="normal" if enabled else "disabled")
        self.clicker.settings["limit_enabled"] = enabled
        save_settings(self.clicker.settings)
    
    def update_mouse_button(self):
        """Update the mouse button setting"""
        self.clicker.settings["mouse_button"] = self.mouse_button_var.get()
        save_settings(self.clicker.settings)
    
    def update_mode(self):
        """Update the hotkey activation mode"""
        self.clicker.settings["mode"] = self.mode_var.get()
        save_settings(self.clicker.settings)
    
    def format_hotkey_display(self):
        """Format the hotkey for display"""
        hotkey = self.clicker.settings["hotkey"]
        
        if hotkey["type"] == "keyboard":
            keys = hotkey.get("keys", [])
            if not keys:
                return "No hotkey set"
            formatted_keys = []
            for key in keys:
                if key == "shift":
                    formatted_keys.append("⇧ Shift")
                elif key == "ctrl" or key == "control":
                    formatted_keys.append("⌃ Ctrl")
                elif key == "alt" or key == "option":
                    formatted_keys.append("⌥ Alt")
                elif key == "cmd" or key == "command":
                    formatted_keys.append("⌘ Cmd")
                else:
                    formatted_keys.append(key.upper())
                
            return " + ".join(formatted_keys)
        else:
            return f"Mouse: {hotkey.get('button', 'left').upper()}"
    
    def update_hotkey_display(self):
        """Update the hotkey display label"""
        self.hotkey_display.config(text=self.format_hotkey_display())
    
    def update_status(self, text):
        """Update the status text"""
        self.status_var.set(text)
    
    def open_discord(self):
        """Open the Discord server link"""
        webbrowser.open(DISCORD_URL)
    
    def on_close(self):
        """Handle window close event"""
        if self.clicker.clicking:
            self.clicker.stop_clicking()
        
        save_settings(self.clicker.settings)
        self.root.destroy()
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

def check_accessibility_permissions():
    """Check if the app has accessibility permissions"""
    try:

        ev = CGEventCreate(None)
        CGEventGetLocation(ev)
        return True
    except Exception:
        return False

def main():
    root = tk.Tk()
    root.withdraw()

    if sys.version_info < (3, 6):
        messagebox.showerror(
            "Python Version Error",
            "SpeedAutoClicker requires Python 3.6 or higher.\n"
            "Please update your Python installation."
        )
        return

    if not check_accessibility_permissions():
        messagebox.showerror(
            "Accessibility Permissions Required",
            "SpeedAutoClicker needs accessibility permissions to function.\n\n"
            "Please go to System Preferences > Security & Privacy > Privacy > Accessibility\n"
            "and add this application to the list of allowed apps."
        )

        try:
            subprocess.run([
                "open", 
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
            ])
        except:
            pass
        
        return
    
    try:
        clicker = AutoClicker()
        gui = AutoClickerGUI(clicker)
        gui.run()
    except Exception as e:
        messagebox.showerror(
            "Error Starting Application",
            f"An error occurred while starting SpeedAutoClicker:\n\n{str(e)}\n\n"
            "Please report this issue on our Discord server."
        )

if __name__ == "__main__":
    main()
