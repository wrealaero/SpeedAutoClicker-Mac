#!/usr/bin/env python3
"""
SpeedAutoClicker for macOS - by aero :D
A high-performance(cap), reliable auto-clicker(cap) with precise control over click rate and duty cycle.(big cap)
"""

import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import subprocess
from datetime import datetime

try:
    from Quartz import (
        CGEventCreate, CGEventGetLocation, CGEventCreateMouseEvent,
        CGEventPost, CGEventSetIntegerValueField, CGEventSourceCreate,
        kCGEventLeftMouseDown, kCGEventLeftMouseUp,
        kCGEventRightMouseDown, kCGEventRightMouseUp,
        kCGEventOtherMouseDown, kCGEventOtherMouseUp,
        kCGMouseButtonLeft, kCGMouseButtonRight, kCGMouseButtonCenter,
        kCGHIDEventTap, kCGEventSourceStateHIDSystemState
    )
    from AppKit import NSEvent, NSApplication, NSApp
    from PyObjCTools import AppHelper
except ImportError as e:
    print(f"Error importing macOS modules: {e}")
    print("Please install required dependencies:")
    print("pip3 install -r requirements.txt")
    sys.exit(1)

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
except ImportError as e:
    print(f"Error importing pynput: {e}")
    print("Please install pynput:")
    print("pip3 install pynput==1.7.6")
    sys.exit(1)

VERSION = "1.0.1"
SETTINGS_FILE = os.path.expanduser("~/.speedautoclicker.json")
DISCORD_URL = "https://discord.gg/MxGV8fGzpR"
GITHUB_REPO = "https://api.github.com/repos/wrealaero/SpeedAutoClicker-Mac"

DEFAULT_SETTINGS = {
    "interval_ms": 50.0,
    "duty_cycle": 50.0,
    "mouse_button": "left",
    "mode": "toggle",
    "limit_enabled": False,
    "click_limit": 100,
    "hotkey": {
        "type": "keyboard",
        "keys": ["shift", "q"]
    },
    "last_update_check": None
}

def load_settings():
    """Load settings from file or create with defaults"""
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
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

class HotkeyManager:
    """Manages hotkey detection and handling"""
    
    def __init__(self, callback, settings):
        self.callback = callback
        self.settings = settings
        self.current_keys = set()
        self.listener = None
        self.capturing = False
        self.capture_callback = None
        self.start_listener()
    
    def start_listener(self):
        """Start the keyboard listener"""
        try:
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.listener.start()
        except Exception as e:
            print(f"Error starting keyboard listener: {e}")
    
    def stop_listener(self):
        """Stop the keyboard listener"""
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def restart_listener(self):
        """Restart the keyboard listener"""
        self.stop_listener()
        self.start_listener()
    
    def on_press(self, key):
        """Handle key press events"""
        try:
            key_str = self._key_to_string(key)
            
            if key_str:
                if self.capturing:
                    self.current_keys.add(key_str)
                    return True

                hotkey = self.settings["hotkey"]
                if hotkey["type"] == "keyboard":
                    hotkey_keys = set(hotkey.get("keys", []))

                    self.current_keys.add(key_str)

                    if hotkey_keys and hotkey_keys.issubset(self.current_keys):
                        if self.settings["mode"] == "hold" and len(self.current_keys) == len(hotkey_keys):
                            self.callback(True) 
                        elif self.settings["mode"] == "toggle":
                            self.callback(None)
            
            return True
        except Exception as e:
            print(f"Error in on_press: {e}")
            return True
    
    def on_release(self, key):
        """Handle key release events"""
        try:
            key_str = self._key_to_string(key)
            
            if key_str:
                if self.capturing and key_str in self.current_keys:
                    if self.current_keys:
                        new_hotkey = {
                            "type": "keyboard",
                            "keys": list(self.current_keys)
                        }
                        self.settings["hotkey"] = new_hotkey
                        save_settings(self.settings)
                        
                        if self.capture_callback:
                            self.capture_callback(new_hotkey)
                    
                    self.capturing = False
                    self.current_keys = set()
                    return True

                if key_str in self.current_keys:
                    self.current_keys.remove(key_str)

                if self.settings["mode"] == "hold":
                    hotkey_keys = set(self.settings["hotkey"].get("keys", []))
                    if key_str in hotkey_keys and not hotkey_keys.issubset(self.current_keys):
                        self.callback(False)
            
            return True
        except Exception as e:
            print(f"Error in on_release: {e}")
            return True
    
    def _key_to_string(self, key):
        """Convert a key to its string representation"""
        try:
            if isinstance(key, Key):
                if key == Key.shift or key == Key.shift_r or key == Key.shift_l:
                    return "shift"
                elif key == Key.ctrl or key == Key.ctrl_r or key == Key.ctrl_l:
                    return "ctrl"
                elif key == Key.alt or key == Key.alt_r or key == Key.alt_l:
                    return "alt"
                elif key == Key.cmd or key == Key.cmd_r or key == Key.cmd_l:
                    return "cmd"
                elif key == Key.space:
                    return "space"
                elif key == Key.tab:
                    return "tab"
                elif key == Key.enter:
                    return "enter"
                elif key == Key.esc:
                    return "esc"
                else:
                    return key.name
            elif isinstance(key, KeyCode):
                if hasattr(key, 'char') and key.char:
                    return key.char.lower()
                elif hasattr(key, 'vk') and key.vk:
                    if 48 <= key.vk <= 57:
                        return chr(key.vk)
                    elif 65 <= key.vk <= 90:
                        return chr(key.vk + 32) 
            
            return None
        except Exception as e:
            print(f"Error converting key: {e}")
            return None
    
    def start_capture(self, callback):
        """Start capturing a new hotkey"""
        self.capturing = True
        self.current_keys = set()
        self.capture_callback = callback

class ClickerEngine:
    """Handles the actual mouse clicking functionality"""
    
    def __init__(self, settings, status_callback=None):
        self.settings = settings
        self.status_callback = status_callback
        self.clicking = False
        self.click_thread = None
        self.stop_event = threading.Event()
        self.click_count = 0

        self.event_source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

        self.button_map = {
            "left": {
                "down": kCGEventLeftMouseDown,
                "up": kCGEventLeftMouseUp,
                "button": kCGMouseButtonLeft
            },
            "right": {
                "down": kCGEventRightMouseDown,
                "up": kCGEventRightMouseUp,
                "button": kCGMouseButtonRight
            },
            "middle": {
                "down": kCGEventOtherMouseDown,
                "up": kCGEventOtherMouseUp,
                "button": kCGMouseButtonCenter
            }
        }
    
    def get_mouse_position(self):
        """Get the current mouse position"""
        event = CGEventCreate(None)
        return CGEventGetLocation(event)
    
    def perform_click(self, position, button_type="left"):
        """Perform a single click at the specified position"""
        try:
            button_info = self.button_map.get(button_type, self.button_map["left"])

            mouse_down = CGEventCreateMouseEvent(
                self.event_source,
                button_info["down"],
                position,
                button_info["button"]
            )

            mouse_up = CGEventCreateMouseEvent(
                self.event_source,
                button_info["up"],
                position,
                button_info["button"]
            )

            CGEventPost(kCGHIDEventTap, mouse_down)

            interval_ms = self.settings["interval_ms"]
            duty_cycle = self.settings["duty_cycle"]
            on_time = (interval_ms * duty_cycle) / 100.0 / 1000.0

            time.sleep(on_time)

            CGEventPost(kCGHIDEventTap, mouse_up)
            
            return True
        except Exception as e:
            print(f"Error performing click: {e}")
            return False
    
    def clicking_loop(self):
        """Main clicking loop that runs in a separate thread"""
        try:
            self.click_count = 0
            limit_enabled = self.settings["limit_enabled"]
            click_limit = self.settings["click_limit"] if limit_enabled else 0

            if self.status_callback:
                self.status_callback("Running")
            
            while not self.stop_event.is_set():
                position = self.get_mouse_position()

                success = self.perform_click(position, self.settings["mouse_button"])
                
                if success:
                    self.click_count += 1

                    if limit_enabled and self.click_count >= click_limit:
                        break

                interval_ms = self.settings["interval_ms"]
                duty_cycle = self.settings["duty_cycle"]
                on_time = (interval_ms * duty_cycle) / 100.0 / 1000.0
                off_time = (interval_ms / 1000.0) - on_time

                if off_time > 0 and not self.stop_event.is_set():
                    time.sleep(off_time)

            if self.status_callback:
                if limit_enabled and self.click_count >= click_limit:
                    self.status_callback(f"Completed {self.click_count} clicks")
                else:
                    self.status_callback("Stopped")
            
            self.clicking = False
        except Exception as e:
            print(f"Error in clicking loop: {e}")
            if self.status_callback:
                self.status_callback(f"Error: {str(e)}")
            self.clicking = False
    
    def start_clicking(self):
        """Start the clicking process"""
        if not self.clicking:
            self.clicking = True
            self.stop_event.clear()
            self.click_thread = threading.Thread(target=self.clicking_loop)
            self.click_thread.daemon = True
            self.click_thread.start()
            return True
        return False
    
    def stop_clicking(self):
        """Stop the clicking process"""
        if self.clicking:
            self.stop_event.set()
            if self.click_thread:
                self.click_thread.join(timeout=1.0)
            self.clicking = False
            return True
        return False
    
    def toggle_clicking(self):
        """Toggle the clicking state"""
        if self.clicking:
            return self.stop_clicking()
        else:
            return self.start_clicking()
    
    def handle_hotkey(self, state=None):
        """Handle hotkey press based on mode"""
        if state is None:
            return self.toggle_clicking()
        elif state:
            return self.start_clicking()
        else:
            return self.stop_clicking()

class AutoClickerGUI:
    """Main GUI for the auto-clicker application"""
    
    def __init__(self):
        self.settings = load_settings()

        self.clicker_engine = ClickerEngine(self.settings, self.update_status)

        self.hotkey_manager = HotkeyManager(self.clicker_engine.handle_hotkey, self.settings)

        self.root = tk.Tk()
        self.root.title(f"SpeedAutoClicker v{VERSION}")
        self.root.geometry("450x600")
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
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"))

        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="SpeedAutoClicker",
            style="Title.TLabel"
        )
        title_label.pack(anchor="center")
        
        version_label = ttk.Label(
            title_frame, 
            text=f"v{VERSION}",
            font=("Arial", 9)
        )
        version_label.pack(anchor="center")

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=10)

        self.main_tab = ttk.Frame(self.notebook, padding=10)
        self.advanced_tab = ttk.Frame(self.notebook, padding=10)
        self.about_tab = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.main_tab, text="Main")
        self.notebook.add(self.advanced_tab, text="Advanced")
        self.notebook.add(self.about_tab, text="About")

        self.build_main_tab()

        self.build_advanced_tab()

        self.build_about_tab()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.after(1000, self.check_for_updates_silently)
    
    def build_main_tab(self):
        """Build the main tab interface"""
        self.create_section_label(self.main_tab, "Click Interval")
        
        interval_frame = ttk.Frame(self.main_tab)
        interval_frame.pack(fill="x", pady=5)
        
        ttk.Label(interval_frame, text="Interval:").pack(side="left")
        
        self.interval_var = tk.StringVar(value=str(self.settings["interval_ms"]))
        self.interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        self.interval_entry.pack(side="left", padx=(5, 5))
        
        ttk.Label(interval_frame, text="ms").pack(side="left")
        
        self.cps_label = ttk.Label(interval_frame, text="= 0.00 CPS")
        self.cps_label.pack(side="left", padx=(10, 0))

        self.create_section_label(self.main_tab, "Mouse Button")
        
        button_frame = ttk.Frame(self.main_tab)
        button_frame.pack(fill="x", pady=5)
        
        self.mouse_button_var = tk.StringVar(value=self.settings["mouse_button"])
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

        self.create_section_label(self.main_tab, "Hotkey Setup")
        
        hotkey_frame = ttk.Frame(self.main_tab)
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
            command=self.start_hotkey_capture
        )
        self.hotkey_button.pack(side="right")

        self.create_section_label(self.main_tab, "Hotkey Activation Mode")
        
        mode_frame = ttk.Frame(self.main_tab)
        mode_frame.pack(fill="x", pady=5)
        
        self.mode_var = tk.StringVar(value=self.settings["mode"])
        
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

        control_frame = ttk.Frame(self.main_tab)
        control_frame.pack(fill="x", pady=15)
        
        self.toggle_button = ttk.Button(
            control_frame, 
            text="Start",
            command=self.toggle_clicking,
            style="TButton",
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

        self.interval_var.trace_add("write", self.update_cps_display)
        self.interval_entry.bind("<FocusOut>", self.validate_interval)
    
    def build_advanced_tab(self):
        """Build the advanced tab interface"""
        self.create_section_label(self.advanced_tab, "Click Duty Cycle")
        
        duty_frame = ttk.Frame(self.advanced_tab)
        duty_frame.pack(fill="x", pady=5)
        
        ttk.Label(duty_frame, text="Duty Cycle:").pack(side="left")
        
        self.duty_var = tk.StringVar(value=str(self.settings["duty_cycle"]))
        self.duty_entry = ttk.Entry(duty_frame, textvariable=self.duty_var, width=10)
        self.duty_entry.pack(side="left", padx=(5, 5))
        
        ttk.Label(duty_frame, text="%").pack(side="left")

        duty_info_frame = ttk.Frame(self.advanced_tab)
        duty_info_frame.pack(fill="x", pady=5)
        
        duty_info = ttk.Label(
            duty_info_frame,
            text="Duty cycle controls how long each click is held down.\n"
                 "50% means the mouse button is pressed for half of the interval.",
            font=("Arial", 9),
            wraplength=400
        )
        duty_info.pack(anchor="w")

        self.create_section_label(self.advanced_tab, "Click Limit")
        
        limit_frame = ttk.Frame(self.advanced_tab)
        limit_frame.pack(fill="x", pady=5)
        
        self.limit_enabled_var = tk.BooleanVar(value=self.settings["limit_enabled"])
        limit_check = ttk.Checkbutton(
            limit_frame, 
            text="Limit number of clicks",
            variable=self.limit_enabled_var,
            command=self.toggle_limit_entry
        )
        limit_check.pack(side="left")
        
        self.limit_var = tk.StringVar(value=str(self.settings["click_limit"]))
        self.limit_entry = ttk.Entry(limit_frame, textvariable=self.limit_var, width=10)
        self.limit_entry.pack(side="right")

        self.create_section_label(self.advanced_tab, "Performance")
        
        perf_frame = ttk.Frame(self.advanced_tab)
        perf_frame.pack(fill="x", pady=5)

        ttk.Label(perf_frame, text="Clicks performed:").pack(side="left")
        
        self.click_count_var = tk.StringVar(value="0")
        click_count_label = ttk.Label(
            perf_frame,
            textvariable=self.click_count_var,
            font=("Arial", 10, "bold")
        )
        click_count_label.pack(side="left", padx=(5, 0))

        reset_button = ttk.Button(
            perf_frame,
            text="Reset",
            command=self.reset_click_counter,
            width=10
        )
        reset_button.pack(side="right")

        self.create_section_label(self.advanced_tab, "Troubleshooting")
        
        trouble_frame = ttk.Frame(self.advanced_tab)
        trouble_frame.pack(fill="x", pady=5)
        
        restart_hotkey_button = ttk.Button(
            trouble_frame,
            text="Restart Hotkey System",
            command=self.restart_hotkey_system,
            width=20
        )
        restart_hotkey_button.pack(side="left", padx=(0, 10))
        
        check_updates_button = ttk.Button(
            trouble_frame,
            text="Check for Updates",
            command=self.check_for_updates,
            width=20
        )
        check_updates_button.pack(side="right")

        self.duty_entry.bind("<FocusOut>", self.validate_duty)
        self.limit_entry.bind("<FocusOut>", self.validate_limit)

        self.toggle_limit_entry()
    
    def build_about_tab(self):
        """Build the about tab interface"""
        info_frame = ttk.Frame(self.about_tab)
        info_frame.pack(fill="x", pady=10)
        
        app_name = ttk.Label(
            info_frame,
            text="SpeedAutoClicker for macOS",
            font=("Arial", 14, "bold")
        )
        app_name.pack(anchor="center")
        
        version_info = ttk.Label(
            info_frame,
            text=f"Version {VERSION}",
            font=("Arial", 10)
        )
        version_info.pack(anchor="center", pady=(5, 15))
        
        description = ttk.Label(
            info_frame,
            text="A high-performance, reliable auto-clicker with precise\n"
                 "control over click rate, duty cycle, and more.",
            font=("Arial", 10),
            justify="center"
        )
        description.pack(anchor="center", pady=(0, 15))

        support_frame = ttk.Frame(self.about_tab)
        support_frame.pack(fill="x", pady=10)
        
        support_label = ttk.Label(
            support_frame,
            text="Support & Community",
            font=("Arial", 12, "bold")
        )
        support_label.pack(anchor="center", pady=(0, 10))
        
        discord_button = ttk.Button(
            support_frame,
            text="Join Discord Server",
            command=self.open_discord,
            width=20
        )
        discord_button.pack(anchor="center", pady=5)
        
        github_button = ttk.Button(
            support_frame,
            text="GitHub Repository",
            command=self.open_github,
            width=20
        )
        github_button.pack(anchor="center", pady=5)

        credits_frame = ttk.Frame(self.about_tab)
        credits_frame.pack(fill="x", pady=10)
        
        credits_label = ttk.Label(
            credits_frame,
            text="Credits",
            font=("Arial", 12, "bold")
        )
        credits_label.pack(anchor="center", pady=(10, 5))
        
        author_label = ttk.Label(
            credits_frame,
            text="Created by wrealaero\nDM 5qvx for bugs and issues :D",
            font=("Arial", 10),
            justify="center"
        )
        author_label.pack(anchor="center", pady=5)
    
    def create_section_label(self, parent, text):
        """Create a section header label"""
        frame = ttk.Frame(parent)
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
                interval_ms = 1.0
                
            cps = 1000.0 / interval_ms
            self.cps_label.config(text=f"= {cps:.2f} CPS")
        except ValueError:
            self.cps_label.config(text="= 0.00 CPS")
    
    def validate_interval(self, event=None):
        """Validate and update the interval value"""
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                interval = 1.0
                self.interval_var.set(str(interval))
            
            self.settings["interval_ms"] = interval
            save_settings(self.settings)
        except ValueError:
            self.interval_var.set(str(self.settings["interval_ms"]))
    
    def validate_duty(self, event=None):
        """Validate and update the duty cycle value"""
        try:
            duty = float(self.duty_var.get())
            if duty < 1:
                duty = 1.0
            elif duty > 99:
                duty = 99.0
            
            self.duty_var.set(str(duty))
            self.settings["duty_cycle"] = duty
            save_settings(self.settings)
        except ValueError:
            self.duty_var.set(str(self.settings["duty_cycle"]))
    
    def validate_limit(self, event=None):
        """Validate and update the click limit value"""
        try:
            limit = int(self.limit_var.get())
            if limit < 1:
                limit = 1
            
            self.limit_var.set(str(limit))
            self.settings["click_limit"] = limit
            save_settings(self.settings)
        except ValueError:
            self.limit_var.set(str(self.settings["click_limit"]))
    
    def toggle_limit_entry(self):
        """Enable or disable the limit entry based on checkbox"""
        enabled = self.limit_enabled_var.get()
        state = "normal" if enabled else "disabled"
        self.limit_entry.config(state=state)
        
        self.settings["limit_enabled"] = enabled
        save_settings(self.settings)
    
    def update_mouse_button(self):
        """Update the mouse button setting"""
        button = self.mouse_button_var.get()
        self.settings["mouse_button"] = button
        save_settings(self.settings)
    
    def update_mode(self):
        """Update the activation mode setting"""
        mode = self.mode_var.get()
        self.settings["mode"] = mode
        save_settings(self.settings)
    
    def format_hotkey_display(self):
        """Format the hotkey for display"""
        hotkey = self.settings["hotkey"]
        if hotkey["type"] == "keyboard":
            keys = hotkey.get("keys", [])
            if keys:
                return " + ".join(k.capitalize() for k in keys)
        
        return "No hotkey set"
    
    def start_hotkey_capture(self):
        """Start capturing a new hotkey"""
        self.hotkey_display.config(text="Press key combination...")
        self.hotkey_button.config(state="disabled")
        
        def capture_complete(new_hotkey):
            keys = new_hotkey.get("keys", [])
            if keys:
                self.hotkey_display.config(text=self.format_hotkey_display())
            else:
                self.hotkey_display.config(text="No hotkey set")
            
            self.hotkey_button.config(state="normal")
        
        self.hotkey_manager.start_capture(capture_complete)
    
    def toggle_clicking(self):
        """Toggle the clicking state"""
        if self.clicker_engine.clicking:
            self.clicker_engine.stop_clicking()
            self.toggle_button.config(text="Start")
        else:
            self.validate_interval()
            self.validate_duty()
            if self.settings["limit_enabled"]:
                self.validate_limit()
            
            self.clicker_engine.start_clicking()
            self.toggle_button.config(text="Stop")
    
    def update_status(self, status):
        """Update the status display"""
        self.status_var.set(status)
        
        if status == "Running":
            self.toggle_button.config(text="Stop")
        elif status.startswith("Stopped") or status.startswith("Completed") or status.startswith("Error"):
            self.toggle_button.config(text="Start")

        self.click_count_var.set(str(self.clicker_engine.click_count))
    
    def reset_click_counter(self):
        """Reset the click counter"""
        self.clicker_engine.click_count = 0
        self.click_count_var.set("0")
    
    def restart_hotkey_system(self):
        """Restart the hotkey system"""
        try:
            self.hotkey_manager.restart_listener()
            messagebox.showinfo("Hotkey System", "Hotkey system has been restarted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart hotkey system: {str(e)}")
    
    def check_for_updates_silently(self):
        """Check for updates without showing a message if up to date"""
        last_check = self.settings.get("last_update_check")
        if last_check:
            last_check_date = datetime.strptime(last_check, "%Y-%m-%d").date()
            today = datetime.now().date()
            if (today - last_check_date).days < 1:
                return
        
        try:
            import urllib.request
            import json

            self.settings["last_update_check"] = datetime.now().strftime("%Y-%m-%d")
            save_settings(self.settings)

            req = urllib.request.Request(
                f"{GITHUB_REPO}/releases/latest",
                headers={"User-Agent": f"SpeedAutoClicker/{VERSION}"}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").lstrip("v")
                
                if latest_version and latest_version != VERSION:
                    result = messagebox.askyesno(
                        "Update Available",
                        f"A new version (v{latest_version}) is available!\n\n"
                        f"You are currently using v{VERSION}.\n\n"
                        "Would you like to update now?"
                    )
                    
                    if result:
                        self.run_updater()
        except Exception as e:
            print(f"Error checking for updates: {e}")
    
    def check_for_updates(self):
        """Check for updates and show a message regardless of result"""
        try:
            import urllib.request
            import json

            self.settings["last_update_check"] = datetime.now().strftime("%Y-%m-%d")
            save_settings(self.settings)

            req = urllib.request.Request(
                f"{GITHUB_REPO}/releases/latest",
                headers={"User-Agent": f"SpeedAutoClicker/{VERSION}"}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").lstrip("v")
                
                if latest_version and latest_version != VERSION:
                    result = messagebox.askyesno(
                        "Update Available",
                        f"A new version (v{latest_version}) is available!\n\n"
                        f"You are currently using v{VERSION}.\n\n"
                        "Would you like to update now?"
                    )
                    
                    if result:
                        self.run_updater()
                else:
                    messagebox.showinfo(
                        "No Updates Available",
                        f"You are using the latest version (v{VERSION})."
                    )
        except Exception as e:
            messagebox.showerror(
                "Update Check Failed",
                f"Failed to check for updates: {str(e)}"
            )
    
    def run_updater(self):
        """Run the updater script"""
        try:
            updater_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "updater.py")
            if os.path.exists(updater_path):
                self.root.destroy()

                subprocess.Popen([sys.executable, updater_path])
                sys.exit(0)
            else:
                messagebox.showerror(
                    "Update Error",
                    "Updater script not found. Please download the latest version manually."
                )
        except Exception as e:
            messagebox.showerror(
                "Update Error",
                f"Failed to run updater: {str(e)}"
            )
    
    def open_discord(self):
        """Open the Discord server link"""
        webbrowser.open(DISCORD_URL)
    
    def open_github(self):
        """Open the GitHub repository"""
        webbrowser.open(f"https://github.com/{GITHUB_REPO.split('/repos/')[1]}")
    
    def on_close(self):
        """Handle window close event"""
        if self.clicker_engine.clicking:
            self.clicker_engine.stop_clicking()

        self.hotkey_manager.stop_listener()

        save_settings(self.settings)

        self.root.destroy()
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

def main():
    """Main entry point for the application"""
    try:
        gui = AutoClickerGUI()
        gui.run()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror(
            "Error",
            f"An error occurred: {str(e)}\n\n"
            "Please report this issue on Discord or GitHub."
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
