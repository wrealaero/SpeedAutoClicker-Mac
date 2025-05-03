#!/usr/bin/env python3
import os
import sys
import json
import time
import threading
import webbrowser
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    from Quartz import (
        CGEventCreate, CGEventGetLocation, CGEventCreateMouseEvent,
        CGEventPost, kCGEventLeftMouseDown, kCGEventLeftMouseUp,
        kCGEventRightMouseDown, kCGEventRightMouseUp,
        kCGEventOtherMouseDown, kCGEventOtherMouseUp,
        kCGMouseButtonLeft, kCGMouseButtonRight, kCGMouseButtonCenter,
        kCGHIDEventTap
    )
    from pynput import keyboard
    import objc
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure you have the required dependencies installed.")
    print("Run: pip3 install -r requirements.txt")
    sys.exit(1)

VERSION = "1.0.0"
SETTINGS_FILE = os.path.expanduser("~/.speedautoclicker.json")
DISCORD_URL = "https://discord.gg/MxGV8fGzpR"
GITHUB_REPO = "https://api.github.com/repos/wrealaero/SpeedAutoClicker-Mac"

DEFAULT_SETTINGS = {
    "interval_ms": 100.0,
    "duty_cycle": 50.0,
    "mouse_button": "left",
    "mode": "toggle",
    "limit_enabled": False,
    "click_limit": 100,
    "hotkey": {
        "type": "keyboard",
        "keys": ["shift", "q"]
    }
}

def load_settings():
    """Load settings from file or return defaults"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

class MouseController:
    """Handles mouse clicking using Quartz CGEvent API"""
    
    def __init__(self):
        self.button_map = {
            "left": (kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGMouseButtonLeft),
            "right": (kCGEventRightMouseDown, kCGEventRightMouseUp, kCGMouseButtonRight),
            "middle": (kCGEventOtherMouseDown, kCGEventOtherMouseUp, kCGMouseButtonCenter)
        }
        
    def get_current_position(self):
        """Get current mouse position"""
        event = CGEventCreate(None)
        return CGEventGetLocation(event)
    
    def click(self, button="left", hold_time=0.05):
        """
        Perform a mouse click at the current position
        
        Args:
            button: Mouse button to click ("left", "right", "middle")
            hold_time: How long to hold the button down in seconds
        """
        try:
            position = self.get_current_position()

            down_event, up_event, button_code = self.button_map.get(
                button, self.button_map["left"])

            event_down = CGEventCreateMouseEvent(
                None, down_event, position, button_code)
            CGEventPost(kCGHIDEventTap, event_down)

            time.sleep(hold_time)

            event_up = CGEventCreateMouseEvent(
                None, up_event, position, button_code)
            CGEventPost(kCGHIDEventTap, event_up)

            time.sleep(0.001)
            
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False

class HotkeyManager:
    """Manages hotkey detection and handling"""
    
    def __init__(self, callback):
        self.callback = callback
        self.listener = None
        self.current_keys = set()
        self.hotkey_keys = []
        self.capturing = False
        self.capture_callback = None
        self.is_active = False
        
    def start_listener(self):
        """Start the keyboard listener"""
        if self.listener is None or not self.listener.is_alive():
            try:
                self.listener = keyboard.Listener(
                    on_press=self._on_press,
                    on_release=self._on_release)
                self.listener.daemon = True
                self.listener.start()
            except Exception as e:
                print(f"Error starting keyboard listener: {e}")
    
    def stop_listener(self):
        """Stop the keyboard listener"""
        if self.listener and self.listener.is_alive():
            self.listener.stop()
            self.listener = None
    
    def set_hotkey(self, keys):
        """Set the hotkey to detect"""
        self.hotkey_keys = [k.lower() for k in keys]
    
    def start_capture(self, callback):
        """Start capturing a new hotkey"""
        self.capturing = True
        self.capture_callback = callback
        self.current_keys.clear()
    
    def stop_capture(self):
        """Stop capturing a new hotkey"""
        self.capturing = False
        self.capture_callback = None
    
    def _on_press(self, key):
        """Handle key press events"""
        try:
            if hasattr(key, 'char') and key.char:
                key_str = key.char.lower()
            elif hasattr(key, 'name'):
                key_str = key.name.lower()
            else:
                key_str = str(key).lower().replace("'", "")
                if key_str.startswith("key."):
                    key_str = key_str[4:]

            self.current_keys.add(key_str)

            if self.capturing and self.capture_callback:
                if len(self.current_keys) > 0:
                    self.capture_callback(list(self.current_keys))
                return

            if set(self.hotkey_keys).issubset(self.current_keys):
                self.callback()
        except Exception as e:
            print(f"Key press error: {e}")
    
    def _on_release(self, key):
        """Handle key release events"""
        try:
            if hasattr(key, 'char') and key.char:
                key_str = key.char.lower()
            elif hasattr(key, 'name'):
                key_str = key.name.lower()
            else:
                key_str = str(key).lower().replace("'", "")
                if key_str.startswith("key."):
                    key_str = key_str[4:]

            if key_str in self.current_keys:
                self.current_keys.remove(key_str)

            if self.capturing and len(self.current_keys) == 0:
                self.stop_capture()
        except Exception as e:
            print(f"Key release error: {e}")

class AutoClicker:
    """Main auto-clicker class"""
    
    def __init__(self):
        self.settings = load_settings()
        self.mouse = MouseController()
        self.hotkey_manager = HotkeyManager(self.handle_hotkey)
        
        self.clicking = False
        self.click_thread = None
        self.stop_event = threading.Event()
        self.click_count = 0
        
        self.gui = None

        self.hotkey_manager.set_hotkey(self.settings["hotkey"]["keys"])
        self.hotkey_manager.start_listener()
    
    def handle_hotkey(self):
        """Handle hotkey press based on mode"""
        if self.settings["mode"] == "toggle":
            self.toggle_clicking()
        elif self.settings["mode"] == "hold":
            if not self.clicking:
                self.start_clicking()
                threading.Thread(target=self._monitor_hold_key, daemon=True).start()
    
    def _monitor_hold_key(self):
        """Monitor if hotkey is still held down in hold mode"""
        while self.clicking:
            if not set(self.settings["hotkey"]["keys"]).issubset(self.hotkey_manager.current_keys):
                self.stop_clicking()
                break
            time.sleep(0.05)
    
    def toggle_clicking(self):
        """Toggle clicking on/off"""
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def start_clicking(self):
        """Start auto-clicking"""
        if self.clicking:
            return
        
        self.clicking = True
        self.stop_event.clear()
        self.click_count = 0

        if self.gui:
            self.gui.toggle_button.config(text="Stop")
            self.gui.update_status("Running")

        self.click_thread = threading.Thread(target=self._clicking_loop, daemon=True)
        self.click_thread.start()
    
    def stop_clicking(self):
        """Stop auto-clicking"""
        if not self.clicking:
            return
        
        self.clicking = False
        self.stop_event.set()

        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=1.0)

        if self.gui:
            self.gui.toggle_button.config(text="Start")
            self.gui.update_status(f"Stopped (Clicks: {self.click_count})")
    
    def _clicking_loop(self):
        """Main clicking loop"""
        try:
            interval_ms = float(self.settings["interval_ms"])
            duty_cycle = float(self.settings["duty_cycle"]) / 100.0
            button = self.settings["mouse_button"]
            limit_enabled = self.settings["limit_enabled"]
            click_limit = int(self.settings["click_limit"])

            if interval_ms < 10:
                interval_ms = 10

            hold_time = (interval_ms / 1000.0) * duty_cycle

            if hold_time < 0.001:
                hold_time = 0.001
            elif hold_time > (interval_ms / 1000.0) - 0.001:
                hold_time = (interval_ms / 1000.0) - 0.001

            while self.clicking and not self.stop_event.is_set():
                success = self.mouse.click(button, hold_time)
                
                if success:
                    self.click_count += 1

                    if self.gui and self.click_count % 10 == 0:
                        self.gui.update_status(f"Running (Clicks: {self.click_count})")

                    if limit_enabled and self.click_count >= click_limit:
                        self.clicking = False
                        if self.gui:
                            self.gui.root.after(0, self.stop_clicking)
                        break

                wait_time = (interval_ms / 1000.0) - hold_time
                if wait_time > 0:
                    wait_start = time.time()
                    while time.time() - wait_start < wait_time:
                        if self.stop_event.is_set():
                            break
                        time.sleep(min(0.01, wait_time))
        
        except Exception as e:
            print(f"Clicking error: {e}")
            if self.gui:
                self.gui.root.after(0, lambda: self.gui.update_status(f"Error: {str(e)}"))
                self.gui.root.after(0, self.stop_clicking)
    
    def start_hotkey_capture(self):
        """Start capturing a new hotkey"""
        if self.gui:
            self.gui.update_status("Press hotkey combination...")
            self.hotkey_manager.start_capture(self._hotkey_captured)
    
    def _hotkey_captured(self, keys):
        """Handle captured hotkey"""
        if not keys:
            return

        self.settings["hotkey"]["type"] = "keyboard"
        self.settings["hotkey"]["keys"] = keys

        self.hotkey_manager.set_hotkey(keys)

        if self.gui:
            self.gui.update_hotkey_display()
            self.gui.update_status("Hotkey set successfully")

        save_settings(self.settings)

class AutoClickerGUI:
    """GUI for the auto-clicker"""
    
    def __init__(self, clicker):
        self.clicker = clicker
        self.clicker.gui = self

        self.root = tk.Tk()
        self.root.title(f"SpeedAutoClicker v{VERSION}")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except Exception:
            pass

        self.style = ttk.Style()
        self.style.configure("TFrame", padding=5)
        self.style.configure("TLabel", padding=2)
        self.style.configure("TButton", padding=5)
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"), padding=10)

        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.main_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        self.main_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows/macOS
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # Linux

        title_label = ttk.Label(
            self.main_frame, 
            text="SpeedAutoClicker",
            style="Title.TLabel"
        )
        title_label.pack(fill="x", pady=(0, 10))

        version_frame = ttk.Frame(self.main_frame)
        version_frame.pack(fill="x", pady=(0, 10))
        
        version_label = ttk.Label(
            version_frame, 
            text=f"Version {VERSION}",
            font=("Arial", 9, "italic")
        )
        version_label.pack(side="left")

        self.create_section_label("Click Interval")
        
        interval_frame = ttk.Frame(self.main_frame)
        interval_frame.pack(fill="x", pady=5)
        
        ttk.Label(interval_frame, text="Interval:").pack(side="left")
        
        self.interval_var = tk.StringVar(value=str(self.clicker.settings["interval_ms"]))
        self.interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        self.interval_entry.pack(side="left", padx=(5, 5))
        
        ttk.Label(interval_frame, text="ms").pack(side="left")
        
        self.cps_label = ttk.Label(interval_frame, text="= 0.00 CPS")
        self.cps_label.pack(side="left", padx=(10, 0))

        self.create_section_label("Click Duty Cycle")
        
        duty_info_frame = ttk.Frame(self.main_frame)
        duty_info_frame.pack(fill="x", pady=(0, 5))
        
        duty_info = ttk.Label(
            duty_info_frame, 
            text="Controls how long each click is held down (as % of interval)",
            font=("Arial", 9, "italic"),
            wraplength=450
        )
        duty_info.pack(anchor="w")
        
        duty_frame = ttk.Frame(self.main_frame)
        duty_frame.pack(fill="x", pady=5)
        
        ttk.Label(duty_frame, text="Duty Cycle:").pack(side="left")
        
        self.duty_var = tk.StringVar(value=str(self.clicker.settings["duty_cycle"]))
        self.duty_entry = ttk.Entry(duty_frame, textvariable=self.duty_var, width=10)
        self.duty_entry.pack(side="left", padx=(5, 5))
        
        ttk.Label(duty_frame, text="%").pack(side="left")

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
            width=20
        )
        self.toggle_button.pack(pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            control_frame, 
            textvariable=self.status_var,
            font=("Arial", 10, "italic")
        )
        self.status_label.pack(pady=5)

        update_button = ttk.Button(
            control_frame,
            text="Check for Updates",
            command=self.check_for_updates
        )
        update_button.pack(pady=5)

        diagnostics_button = ttk.Button(
            control_frame,
            text="Run Diagnostics",
            command=self.run_diagnostics
        )
        diagnostics_button.pack(pady=5)

        discord_frame = ttk.Frame(self.main_frame)
        discord_frame.pack(fill="x", pady=(15, 5))
        
        discord_button = ttk.Button(
            discord_frame, 
            text="Join Discord Server",
            command=self.open_discord
        )
        discord_button.pack(side="left")
        
        contact_label = ttk.Label(
            discord_frame, 
            text="DM 5qvx for bugs and issues :D",
            font=("Arial", 9)
        )
        contact_label.pack(side="right")

        self.interval_var.trace_add("write", self.update_cps_display)
        self.interval_entry.bind("<FocusOut>", self.validate_interval)
        self.duty_entry.bind("<FocusOut>", self.validate_duty)
        self.limit_entry.bind("<FocusOut>", self.validate_limit)

        self.toggle_limit_entry()
        self.update_cps_display()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_section_label(self, text):
        """Create a section header label"""
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill="x", pady=(10, 5))
        
        label = ttk.Label(
            frame, 
            text=text,
            style="Header.TLabel"
        )
        label.pack(anchor="w")
        
        separator = ttk.Separator(frame, orient="horizontal")
        separator.pack(fill="x", pady=(2, 0))
    
    def update_cps_display(self, *args):
        """Update the CPS display based on the interval value"""
        try:
            interval_ms = float(self.interval_var.get())
            if interval_ms <= 0:
                interval_ms = 10.0
                
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
            if value < 10:
                self.interval_var.set("10.0")
                self.clicker.settings["interval_ms"] = 10.0
            else:
                self.clicker.settings["interval_ms"] = value
            save_settings(self.clicker.settings)
            self.update_cps_display()
        except ValueError:
            self.interval_var.set(str(self.clicker.settings["interval_ms"]))
    
    def validate_duty(self, event=None):
        """Validate the duty cycle input"""
        try:
            value = float(self.duty_var.get())
            if value < 1 or value > 99:
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
            if value < 1:
                self.limit_var.set("100")
                self.clicker.settings["click_limit"] = 100
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
                elif key == "space":
                    formatted_keys.append("Space")
                else:
                    formatted_keys.append(key.upper())
            
            return " + ".join(formatted_keys)
        
        return "No hotkey set"
    
    def update_hotkey_display(self):
        """Update the hotkey display"""
        self.hotkey_display.config(text=self.format_hotkey_display())
    
    def update_status(self, text):
        """Update the status text"""
        self.status_var.set(text)
    
    def open_discord(self):
        """Open the Discord server link"""
        try:
            webbrowser.open(DISCORD_URL)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Discord link: {str(e)}")
    
    def check_for_updates(self):
        """Check for updates and prompt to install if available"""
        self.update_status("Checking for updates...")

        threading.Thread(target=self._check_updates_thread, daemon=True).start()
    
    def _check_updates_thread(self):
        """Thread function to check for updates"""
        try:
            try:
                import urllib.request
                import json
            except ImportError:
                self.root.after(0, lambda: self.update_status("Error: Could not import required modules"))
                return

            req = urllib.request.Request(
                f"{GITHUB_REPO}/releases/latest",
                headers={'User-Agent': f'SpeedAutoClicker/{VERSION}'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

                latest_version = data.get('tag_name', '').lstrip('v')

                if latest_version and latest_version != VERSION:
                    self.root.after(0, lambda: self._show_update_prompt(latest_version, data.get('html_url', '')))
                else:
                    self.root.after(0, lambda: self.update_status("You have the latest version"))
        
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Update check failed: {str(e)}"))
    
    def _show_update_prompt(self, version, url):
        """Show update prompt dialog"""
        result = messagebox.askyesno(
            "Update Available",
            f"A new version (v{version}) is available!\n\n"
            f"You are currently using v{VERSION}.\n\n"
            "Would you like to update now?"
        )
        
        if result:
            try:
                subprocess.Popen([sys.executable, "updater.py"])
                self.on_close()
            except Exception as e:
                messagebox.showerror("Update Error", f"Could not start updater: {str(e)}")
        else:
            self.update_status(f"Update available: v{version}")
    
    def run_diagnostics(self):
        """Run diagnostics to check system compatibility"""
        self.update_status("Running diagnostics...")

        threading.Thread(target=self._diagnostics_thread, daemon=True).start()
    
    def _diagnostics_thread(self):
        """Thread function to run diagnostics"""
        results = []

        results.append(f"Python version: {sys.version.split()[0]}")

        try:
            import platform
            mac_ver = platform.mac_ver()[0]
            results.append(f"macOS version: {mac_ver}")
        except Exception:
            results.append("Could not determine macOS version")

        modules = {
            "pynput": "Keyboard and mouse monitoring",
            "Quartz": "macOS UI interaction",
            "objc": "Objective-C bridge"
        }
        
        for module, description in modules.items():
            try:
                __import__(module)
                results.append(f"✓ {module}: Installed ({description})")
            except ImportError:
                results.append(f"✗ {module}: Missing ({description})")

        try:
            test_result = self.clicker.mouse.click(hold_time=0.001)
            if test_result:
                results.append("✓ Accessibility permissions: Granted")
            else:
                results.append("✗ Accessibility permissions: May be missing")
        except Exception:
            results.append("✗ Accessibility permissions: Could not verify")

        if self.clicker.hotkey_manager.listener and self.clicker.hotkey_manager.listener.is_alive():
            results.append("✓ Hotkey listener: Running")
        else:
            results.append("✗ Hotkey listener: Not running")

        self.root.after(0, lambda: self._show_diagnostics_results("\n".join(results)))
    
    def _show_diagnostics_results(self, results):
        """Show diagnostics results in a dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Diagnostics Results")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="System Diagnostics", style="Title.TLabel").pack(pady=(0, 10))
        
        text_widget = tk.Text(frame, wrap="word", height=15, width=60)
        text_widget.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_widget, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)

        text_widget.insert("1.0", results)
        text_widget.config(state="disabled")

        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(results)
            copy_button.config(text="Copied!")
            dialog.after(1000, lambda: copy_button.config(text="Copy to Clipboard"))
        
        copy_button = ttk.Button(frame, text="Copy to Clipboard", command=copy_to_clipboard)
        copy_button.pack(pady=10)

        close_button = ttk.Button(frame, text="Close", command=dialog.destroy)
        close_button.pack(pady=(0, 10))

        self.update_status("Diagnostics completed")
    
    def on_close(self):
        """Handle window close event"""
        if self.clicker.clicking:
            self.clicker.stop_clicking()

        self.clicker.hotkey_manager.stop_listener()

        save_settings(self.clicker.settings)

        self.root.destroy()
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        clicker = AutoClicker()
        gui = AutoClickerGUI(clicker)
        gui.run()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
