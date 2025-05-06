#!/usr/bin/env python3
import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import webbrowser
import subprocess
from datetime import datetime
import platform
import re

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

VERSION = "2.0.0"
SETTINGS_FILE = os.path.expanduser("~/.aeroutclicker.json")
DISCORD_URL = "https://discord.com/shA7X2Wesr"
GITHUB_REPO = "https://github.com/wrealaero/SpeedAutoClicker-Mac"

DEFAULT_SETTINGS = {
    "interval_ms": 50.0,
    "duty_cycle": 50.0,
    "hold_time": 0.0,
    "mouse_button": "left",
    "mode": "toggle",
    "limit_enabled": False,
    "click_limit": 100,
    "theme": "default",
    "custom_colors": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "accent": "#0078d7"
    },
    "hotkey": {
        "type": "keyboard",
        "keys": ["shift", "q"]
    },
    "last_update_check": None
}

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                    elif key == "custom_colors" and isinstance(value, dict):
                        for color_key, color_value in value.items():
                            if color_key not in settings[key]:
                                settings[key][color_key] = color_value
                return settings
        return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

def import_config(file_path):
    try:
        with open(file_path, 'r') as f:
            imported_settings = json.load(f)
            current_settings = load_settings()
            
            for key, value in imported_settings.items():
                if key in current_settings:
                    current_settings[key] = value
            
            save_settings(current_settings)
        return True, "Configuration imported successfully!"
    except Exception as e:
        return False, f"Error importing configuration: {e}"

def export_config(file_path):
    try:
        settings = load_settings()
        with open(file_path, 'w') as f:
            json.dump(settings, f, indent=2)
        return True, "Configuration exported successfully!"
    except Exception as e:
        return False, f"Error exporting configuration: {e}"

class EnhancedHotkeyManager:
    def __init__(self, callback, settings):
        self.callback = callback
        self.settings = settings
        self.current_keys = set()
        self.listener = None
        self.capturing = False
        self.capture_callback = None
        self.start_listener()
        
    def start_listener(self):
        try:
            if self.listener and self.listener.is_alive():
                self.listener.stop()
                
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release,
                suppress=False
            )
            self.listener.daemon = True
            self.listener.start()
        except Exception as e:
            print(f"Error starting keyboard listener: {e}")
        
    def stop_listener(self):
        if self.listener:
            try:
                self.listener.stop()
                self.listener = None
            except Exception as e:
                print(f"Error stopping keyboard listener: {e}")
        
    def restart_listener(self):
        self.stop_listener()
        time.sleep(0.5)
        self.start_listener()
        
    def on_press(self, key):
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
        except Exception as e:
            print(f"Error in on_press: {e}")
        return True
        
    def on_release(self, key):
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
        except Exception as e:
            print(f"Error in on_release: {e}")
        return True
        
    def _key_to_string(self, key):
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
        self.capturing = True
        self.current_keys = set()
        self.capture_callback = callback

class AdvancedClickerEngine:
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
        event = CGEventCreate(None)
        return CGEventGetLocation(event)
        
    def perform_click(self, position, button_type="left"):
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

            hold_time = self.settings.get("hold_time", 0.0)
            if hold_time > 0:
                time.sleep(hold_time / 1000.0)
            else:
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
                hold_time = self.settings.get("hold_time", 0.0)
                
                if hold_time > 0:
                    wait_time = interval_ms / 1000.0
                else:
                    duty_cycle = self.settings["duty_cycle"]
                    on_time = (interval_ms * duty_cycle) / 100.0 / 1000.0
                    wait_time = (interval_ms / 1000.0) - on_time
                    
                if wait_time > 0 and not self.stop_event.is_set():
                    time.sleep(wait_time)
            
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
        if not self.clicking:
            self.clicking = True
            self.stop_event.clear()
            self.click_thread = threading.Thread(target=self.clicking_loop)
            self.click_thread.daemon = True
            self.click_thread.start()
            return True
        return False
        
    def stop_clicking(self):
        if self.clicking:
            self.stop_event.set()
            if self.click_thread and self.click_thread.is_alive():
                try:
                    self.click_thread.join(timeout=1.0)
                except Exception as e:
                    print(f"Error joining click thread: {e}")
            self.clicking = False
            return True
        return False
        
    def toggle_clicking(self):
        if self.clicking:
            return self.stop_clicking()
        else:
            return self.start_clicking()
        
    def handle_hotkey(self, state=None):
        if state is None:
            return self.toggle_clicking()
        elif state:
            return self.start_clicking()
        else:
            return self.stop_clicking()

class FloatEntry(ttk.Entry):
    def __init__(self, master=None, decimal_places=2, min_value=0.0, max_value=float('inf'), **kwargs):
        self.decimal_places = decimal_places
        self.min_value = min_value
        self.max_value = max_value
        self.var = kwargs.pop('textvariable', tk.StringVar())
        super().__init__(master, textvariable=self.var, **kwargs)
        
        self.var.trace_add('write', self._validate)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<Return>', self._on_focus_out)
        
    def _validate(self, *args):
        current = self.var.get()

        if current == '' or current == '.':
            return

        filtered = re.sub(r'[^\d.]', '', current)

        parts = filtered.split('.')
        if len(parts) > 2:
            filtered = parts[0] + '.' + ''.join(parts[1:])
            
        try:
            value = float(filtered)

            if value < self.min_value:
                value = self.min_value
            elif value > self.max_value:
                value = self.max_value

            if filtered != current:
                self.var.set(filtered)
        except ValueError:
            if hasattr(self, 'last_valid'):
                self.var.set(self.last_valid)
            else:
                self.var.set('')
    
    def _on_focus_out(self, *args):
        current = self.var.get()

        if current == '' or current == '.':
            value = self.min_value
        else:
            try:
                value = float(current)
                if value < self.min_value:
                    value = self.min_value
                elif value > self.max_value:
                    value = self.max_value
            except ValueError:
                value = self.min_value

        formatted = f"{value:.{self.decimal_places}f}"
        self.var.set(formatted)
        self.last_valid = formatted
        
        return True
        
    def get_float(self):
        try:
            return float(self.var.get())
        except ValueError:
            return self.min_value

class IntEntry(ttk.Entry):
    def __init__(self, master=None, min_value=0, max_value=sys.maxsize, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        self.var = kwargs.pop('textvariable', tk.StringVar())
        super().__init__(master, textvariable=self.var, **kwargs)
        
        self.var.trace_add('write', self._validate)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<Return>', self._on_focus_out)
        
    def _validate(self, *args):
        current = self.var.get()

        if current == '':
            return

        filtered = re.sub(r'[^\d]', '', current)
        
        try:
            value = int(filtered)

            if filtered != current:
                self.var.set(filtered)
        except ValueError:
            if hasattr(self, 'last_valid'):
                self.var.set(self.last_valid)
            else:
                self.var.set('')
    
    def _on_focus_out(self, *args):
        current = self.var.get()

        if current == '':
            value = self.min_value
        else:
            try:
                value = int(current)
                if value < self.min_value:
                    value = self.min_value
                elif value > self.max_value:
                    value = self.max_value
            except ValueError:
                value = self.min_value
        
        formatted = str(value)
        self.var.set(formatted)
        self.last_valid = formatted
        
        return True
        
    def get_int(self):
        try:
            return int(self.var.get())
        except ValueError:
            return self.min_value

class AeroutSpeedAutoClickerGUI:
    def __init__(self):
        self.settings = load_settings()
        self.clicker_engine = AdvancedClickerEngine(self.settings, self.update_status)
        self.hotkey_manager = EnhancedHotkeyManager(self.clicker_engine.handle_hotkey, self.settings)
        
        self.root = tk.Tk()
        self.root.title(f"Aerout SpeedAutoClicker v{VERSION}")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        self.style = ttk.Style()
        self.apply_theme()
        
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)
        
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="Aerout SpeedAutoClicker",
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
        self.settings_tab = ttk.Frame(self.notebook, padding=10)
        self.about_tab = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.main_tab, text="Main")
        self.notebook.add(self.advanced_tab, text="Advanced")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.about_tab, text="About")
        
        self.build_main_tab()
        self.build_advanced_tab()
        self.build_settings_tab()
        self.build_about_tab()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(1000, self.check_for_updates_silently)

        self.root.after(500, self.update_click_count_display)
        
    def apply_theme(self):
        theme = self.settings.get("theme", "default")
        
        if theme == "dark":
            self.root.configure(bg="#2d2d2d")
            self.style.configure("TFrame", background="#2d2d2d")
            self.style.configure("TLabel", background="#2d2d2d", foreground="#ffffff")
            self.style.configure("TButton", background="#3d3d3d", foreground="#ffffff")
            self.style.configure("TCheckbutton", background="#2d2d2d", foreground="#ffffff")
            self.style.configure("TRadiobutton", background="#2d2d2d", foreground="#ffffff")
            self.style.configure("TNotebook", background="#2d2d2d", foreground="#ffffff")
            self.style.configure("TNotebook.Tab", background="#3d3d3d", foreground="#ffffff")
            self.style.configure("Header.TLabel", font=("Arial", 12, "bold"), background="#2d2d2d", foreground="#ffffff")
            self.style.configure("Title.TLabel", font=("Arial", 16, "bold"), background="#2d2d2d", foreground="#ffffff")
        elif theme == "light":
            self.root.configure(bg="#f0f0f0")
            self.style.configure("TFrame", background="#f0f0f0")
            self.style.configure("TLabel", background="#f0f0f0", foreground="#000000")
            self.style.configure("TButton", background="#e0e0e0", foreground="#000000")
            self.style.configure("TCheckbutton", background="#f0f0f0", foreground="#000000")
            self.style.configure("TRadiobutton", background="#f0f0f0", foreground="#000000")
            self.style.configure("TNotebook", background="#f0f0f0", foreground="#000000")
            self.style.configure("TNotebook.Tab", background="#e0e0e0", foreground="#000000")
            self.style.configure("Header.TLabel", font=("Arial", 12, "bold"), background="#f0f0f0", foreground="#000000")
            self.style.configure("Title.TLabel", font=("Arial", 16, "bold"), background="#f0f0f0", foreground="#000000")
        elif theme == "custom":
            colors = self.settings.get("custom_colors", {})
            bg_color = colors.get("bg", "#f0f0f0")
            fg_color = colors.get("fg", "#000000")
            accent_color = colors.get("accent", "#0078d7")
            
            self.root.configure(bg=bg_color)
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TButton", background=accent_color, foreground=fg_color)
            self.style.configure("TCheckbutton", background=bg_color, foreground=fg_color)
            self.style.configure("TRadiobutton", background=bg_color, foreground=fg_color)
            self.style.configure("TNotebook", background=bg_color, foreground=fg_color)
            self.style.configure("TNotebook.Tab", background=accent_color, foreground=fg_color)
            self.style.configure("Header.TLabel", font=("Arial", 12, "bold"), background=bg_color, foreground=fg_color)
            self.style.configure("Title.TLabel", font=("Arial", 16, "bold"), background=bg_color, foreground=fg_color)
        else:
            self.style.configure("TFrame", padding=5)
            self.style.configure("TLabel", padding=2)
            self.style.configure("TButton", padding=5)
            self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
            self.style.configure("Title.TLabel", font=("Arial", 16, "bold"))

    def build_main_tab(self):
        self.create_section_label(self.main_tab, "Click Interval")
        
        interval_frame = ttk.Frame(self.main_tab)
        interval_frame.pack(fill="x", pady=5)
        
        ttk.Label(interval_frame, text="Interval:").pack(side="left")
        
        self.interval_var = tk.StringVar(value=f"{self.settings['interval_ms']:.2f}")
        self.interval_entry = FloatEntry(
            interval_frame, 
            textvariable=self.interval_var, 
            width=10,
            decimal_places=2,
            min_value=1.0,
            max_value=10000.0
        )
        self.interval_entry.pack(side="left", padx=(5, 5))
        
        ttk.Label(interval_frame, text="ms").pack(side="left")
        
        self.cps_label = ttk.Label(interval_frame, text=f"= {1000.0/float(self.settings['interval_ms']):.2f} CPS")
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
        self.toggle_button.pack(side="left", padx=(0, 10))
        
        self.status_label = ttk.Label(
            control_frame, 
            text="Ready",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side="left")

        self.click_count_label = ttk.Label(
            control_frame, 
            text="Clicks: 0",
            font=("Arial", 10)
        )
        self.click_count_label.pack(side="right")

        self.interval_var.trace_add('write', self.update_cps_display)
        
    def build_advanced_tab(self):
        self.create_section_label(self.advanced_tab, "Click Timing")

        duty_frame = ttk.Frame(self.advanced_tab)
        duty_frame.pack(fill="x", pady=5)
        
        ttk.Label(duty_frame, text="Click Duty:").pack(side="left")
        
        self.duty_var = tk.StringVar(value=f"{self.settings['duty_cycle']:.2f}")
        self.duty_entry = FloatEntry(
            duty_frame, 
            textvariable=self.duty_var, 
            width=10,
            decimal_places=2,
            min_value=1.0,
            max_value=99.0
        )
        self.duty_entry.pack(side="left", padx=(5, 5))
        
        ttk.Label(duty_frame, text="%").pack(side="left")
        
        ttk.Label(duty_frame, text="(% of interval mouse button is held down)").pack(side="left", padx=(10, 0))

        hold_frame = ttk.Frame(self.advanced_tab)
        hold_frame.pack(fill="x", pady=5)
        
        ttk.Label(hold_frame, text="Hold Time:").pack(side="left")
        
        self.hold_var = tk.StringVar(value=f"{self.settings.get('hold_time', 0.0):.2f}")
        self.hold_entry = FloatEntry(
            hold_frame, 
            textvariable=self.hold_var, 
            width=10,
            decimal_places=2,
            min_value=0.0,
            max_value=10000.0
        )
        self.hold_entry.pack(side="left", padx=(5, 5))
        
        ttk.Label(hold_frame, text="ms").pack(side="left")
        
        ttk.Label(hold_frame, text="(0 = use duty cycle instead)").pack(side="left", padx=(10, 0))

        self.create_section_label(self.advanced_tab, "Click Limit")
        
        limit_frame = ttk.Frame(self.advanced_tab)
        limit_frame.pack(fill="x", pady=5)
        
        self.limit_var = tk.BooleanVar(value=self.settings["limit_enabled"])
        limit_check = ttk.Checkbutton(
            limit_frame, 
            text="Stop after",
            variable=self.limit_var,
            command=self.update_limit_enabled
        )
        limit_check.pack(side="left")
        
        self.limit_count_var = tk.StringVar(value=str(self.settings["click_limit"]))
        self.limit_entry = IntEntry(
            limit_frame, 
            textvariable=self.limit_count_var, 
            width=10,
            min_value=1,
            max_value=1000000
        )
        self.limit_entry.pack(side="left", padx=(5, 5))
        
        ttk.Label(limit_frame, text="clicks").pack(side="left")

        self.duty_var.trace_add('write', self.update_duty_cycle)
        self.hold_var.trace_add('write', self.update_hold_time)
        self.limit_count_var.trace_add('write', self.update_click_limit)
        
    def build_settings_tab(self):
        self.create_section_label(self.settings_tab, "Theme Settings")
        
        theme_frame = ttk.Frame(self.settings_tab)
        theme_frame.pack(fill="x", pady=5)
        
        self.theme_var = tk.StringVar(value=self.settings["theme"])
        
        themes = [
            ("Default", "default"),
            ("Light", "light"),
            ("Dark", "dark"),
            ("Custom", "custom")
        ]
        
        for i, (text, value) in enumerate(themes):
            rb = ttk.Radiobutton(
                theme_frame, 
                text=text,
                variable=self.theme_var,
                value=value,
                command=self.update_theme
            )
            rb.grid(row=0, column=i, padx=(0, 10))

        custom_frame = ttk.Frame(self.settings_tab)
        custom_frame.pack(fill="x", pady=5)
        
        custom_colors = self.settings.get("custom_colors", {})
        
        color_options = [
            ("Background", "bg", custom_colors.get("bg", "#f0f0f0")),
            ("Text", "fg", custom_colors.get("fg", "#000000")),
            ("Accent", "accent", custom_colors.get("accent", "#0078d7"))
        ]
        
        for i, (text, key, default) in enumerate(color_options):
            ttk.Label(custom_frame, text=f"{text}:").grid(row=i, column=0, sticky="w", pady=2)
            
            color_frame = ttk.Frame(custom_frame)
            color_frame.grid(row=i, column=1, sticky="w", padx=(5, 10), pady=2)
            
            color_preview = tk.Frame(color_frame, bg=default, width=20, height=20)
            color_preview.pack(side="left")
            
            color_button = ttk.Button(
                color_frame, 
                text="Choose",
                command=lambda k=key, p=color_preview: self.choose_color(k, p)
            )
            color_button.pack(side="left", padx=(5, 0))

        self.create_section_label(self.settings_tab, "Configuration")
        
        config_frame = ttk.Frame(self.settings_tab)
        config_frame.pack(fill="x", pady=5)
        
        import_button = ttk.Button(
            config_frame, 
            text="Import Settings",
            command=self.import_settings
        )
        import_button.pack(side="left", padx=(0, 10))
        
        export_button = ttk.Button(
            config_frame, 
            text="Export Settings",
            command=self.export_settings
        )
        export_button.pack(side="left")

        reset_frame = ttk.Frame(self.settings_tab)
        reset_frame.pack(fill="x", pady=10)
        
        reset_button = ttk.Button(
            reset_frame, 
            text="Reset to Default Settings",
            command=self.reset_settings
        )
        reset_button.pack(side="left")
        
    def build_about_tab(self):
        about_frame = ttk.Frame(self.about_tab)
        about_frame.pack(fill="both", expand=True)
        
        ttk.Label(
            about_frame, 
            text="Aerout SpeedAutoClicker",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 5))
        
        ttk.Label(
            about_frame, 
            text=f"Version {VERSION}",
            font=("Arial", 10)
        ).pack(pady=(0, 10))
        
        ttk.Label(
            about_frame, 
            text="A good auto-clicker for macOS",
            font=("Arial", 10)
        ).pack(pady=(0, 5))
        
        ttk.Label(
            about_frame, 
            text="Compatible with Intel and Apple Silicon Macs",
            font=("Arial", 10)
        ).pack(pady=(0, 20))
        
        ttk.Label(
            about_frame, 
            text="© 2024 Aerout - Realaero <3",
            font=("Arial", 9)
        ).pack(pady=(0, 5))
        
        links_frame = ttk.Frame(about_frame)
        links_frame.pack(pady=10)
        
        discord_button = ttk.Button(
            links_frame, 
            text="Join Discord",
            command=lambda: webbrowser.open(DISCORD_URL)
        )
        discord_button.pack(side="left", padx=(0, 10))
        
        github_button = ttk.Button(
            links_frame, 
            text="GitHub Repository",
            command=lambda: webbrowser.open(GITHUB_REPO)
        )
        github_button.pack(side="left")
        
        update_frame = ttk.Frame(about_frame)
        update_frame.pack(pady=10)
        
        self.update_status_label = ttk.Label(
            update_frame, 
            text="",
            font=("Arial", 9)
        )
        self.update_status_label.pack(side="left", padx=(0, 10))
        
        check_update_button = ttk.Button(
            update_frame, 
            text="Check for Updates",
            command=self.check_for_updates
        )
        check_update_button.pack(side="left")
        
    def create_section_label(self, parent, text):
        label = ttk.Label(
            parent, 
            text=text,
            style="Header.TLabel"
        )
        label.pack(anchor="w", pady=(10, 5))
        
    def update_cps_display(self, *args):
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                interval = 1.0
            cps = 1000.0 / interval
            self.cps_label.config(text=f"= {cps:.2f} CPS")
        except ValueError:
            self.cps_label.config(text="= ? CPS")
            
    def update_mouse_button(self):
        self.settings["mouse_button"] = self.mouse_button_var.get()
        save_settings(self.settings)
        
    def update_mode(self):
        self.settings["mode"] = self.mode_var.get()
        save_settings(self.settings)
        
    def update_duty_cycle(self, *args):
        try:
            duty = float(self.duty_var.get())
            if 1.0 <= duty <= 99.0:
                self.settings["duty_cycle"] = duty
                save_settings(self.settings)
        except ValueError:
            pass
            
    def update_hold_time(self, *args):
        try:
            hold_time = float(self.hold_var.get())
            if hold_time >= 0:
                self.settings["hold_time"] = hold_time
                save_settings(self.settings)
        except ValueError:
            pass
            
    def update_limit_enabled(self):
        self.settings["limit_enabled"] = self.limit_var.get()
        save_settings(self.settings)
        
    def update_click_limit(self, *args):
        try:
            limit = int(self.limit_count_var.get())
            if limit > 0:
                self.settings["click_limit"] = limit
                save_settings(self.settings)
        except ValueError:
            pass
            
    def update_theme(self):
        theme = self.theme_var.get()
        self.settings["theme"] = theme
        save_settings(self.settings)
        self.apply_theme()
        
    def choose_color(self, key, preview_widget):
        current_color = self.settings.get("custom_colors", {}).get(key, "#f0f0f0")
        color = colorchooser.askcolor(initialcolor=current_color)
        
        if color and color[1]:
            if "custom_colors" not in self.settings:
                self.settings["custom_colors"] = {}
            self.settings["custom_colors"][key] = color[1]
            preview_widget.config(bg=color[1])
            save_settings(self.settings)
            
            if self.settings["theme"] == "custom":
                self.apply_theme()
                
    def format_hotkey_display(self):
        hotkey = self.settings.get("hotkey", {"type": "keyboard", "keys": ["shift", "q"]})
        if hotkey["type"] == "keyboard":
            keys = hotkey.get("keys", [])
            if keys:
                return "Current Hotkey: " + " + ".join(key.upper() for key in keys)
        return "No hotkey set"
        
    def start_hotkey_capture(self):
        self.hotkey_button.config(text="Press Keys...")
        self.hotkey_display.config(text="Press the keys you want to use...")
        self.hotkey_manager.start_capture(self.finish_hotkey_capture)
        
    def finish_hotkey_capture(self, new_hotkey):
        self.hotkey_button.config(text="Set Hotkey")
        self.hotkey_display.config(text=self.format_hotkey_display())
        
    def toggle_clicking(self):
        if self.clicker_engine.clicking:
            self.clicker_engine.stop_clicking()
            self.toggle_button.config(text="Start")
            self.update_status("Stopped")
        else:
            self.settings["interval_ms"] = self.interval_entry.get_float()
            self.settings["duty_cycle"] = self.duty_entry.get_float()
            self.settings["hold_time"] = self.hold_entry.get_float()
            self.settings["click_limit"] = self.limit_entry.get_int()
            save_settings(self.settings)
            
            self.clicker_engine.start_clicking()
            self.toggle_button.config(text="Stop")
            self.update_status("Running")
            
    def update_status(self, status_text):
        self.status_label.config(text=status_text)
        
    def update_click_count_display(self):
        if hasattr(self.clicker_engine, 'click_count'):
            self.click_count_label.config(text=f"Clicks: {self.clicker_engine.click_count}")
        self.root.after(500, self.update_click_count_display)
        
    def import_settings(self):
        file_path = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            success, message = import_config(file_path)
            messagebox.showinfo("Import Settings", message)
            
            if success:
                self.settings = load_settings()
                self.reload_settings_to_ui()
                self.apply_theme()
                
    def export_settings(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            success, message = export_config(file_path)
            messagebox.showinfo("Export Settings", message)
            
    def reset_settings(self):
        confirm = messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to default values?"
        )
        
        if confirm:
            self.settings = DEFAULT_SETTINGS.copy()
            save_settings(self.settings)
            self.reload_settings_to_ui()
            self.apply_theme()
            messagebox.showinfo("Reset Settings", "Settings have been reset to default values.")
            
    def reload_settings_to_ui(self):
        self.interval_var.set(f"{self.settings['interval_ms']:.2f}")
        self.mouse_button_var.set(self.settings["mouse_button"])
        self.mode_var.set(self.settings["mode"])
        self.hotkey_display.config(text=self.format_hotkey_display())

        self.duty_var.set(f"{self.settings['duty_cycle']:.2f}")
        self.hold_var.set(f"{self.settings.get('hold_time', 0.0):.2f}")
        self.limit_var.set(self.settings["limit_enabled"])
        self.limit_count_var.set(str(self.settings["click_limit"]))

        self.theme_var.set(self.settings["theme"])

        self.clicker_engine.settings = self.settings
        self.hotkey_manager.settings = self.settings
        
    def check_for_updates(self):
        self.update_status_label.config(text="Checking for updates...")
        threading.Thread(target=self._check_updates_thread, daemon=True).start()
        
    def check_for_updates_silently(self):
        threading.Thread(target=self._check_updates_thread, args=(True,), daemon=True).start()
        
    def _check_updates_thread(self, silent=False):
        try:
            import requests
            from packaging import version
            
            response = requests.get(f"{GITHUB_REPO}/releases/latest", timeout=5)
            if response.status_code == 200:
                latest_version_str = response.url.split("/")[-1]
                if latest_version_str.startswith("v"):
                    latest_version_str = latest_version_str[1:]
                    
                latest_version = version.parse(latest_version_str)
                current_version = version.parse(VERSION)
                
                if latest_version > current_version:
                    self.root.after(0, lambda: self.update_status_label.config(
                        text=f"New version available: {latest_version_str}"
                    ))
                    
                    if not silent:
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Update Available",
                            f"A new version ({latest_version_str}) is available!\n\n"
                            f"You are currently using version {VERSION}.\n\n"
                            f"Visit the GitHub repository to download the latest version."
                        ))
                else:
                    if not silent:
                        self.root.after(0, lambda: self.update_status_label.config(
                            text=f"You have the latest version ({VERSION})"
                        ))
                        self.root.after(0, lambda: messagebox.showinfo(
                            "No Updates",
                            f"You are using the latest version ({VERSION})."
                        ))
                    else:
                        self.root.after(0, lambda: self.update_status_label.config(
                            text=f"Version {VERSION} (latest)"
                        ))
            else:
                if not silent:
                    self.root.after(0, lambda: self.update_status_label.config(
                        text="Could not check for updates"
                    ))
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Update Check Failed",
                        "Could not check for updates. Please try again later."
                    ))
                
        except Exception as e:
            print(f"Error checking for updates: {e}")
            if not silent:
                self.root.after(0, lambda: self.update_status_label.config(
                    text="Error checking for updates"
                ))
                self.root.after(0, lambda: messagebox.showwarning(
                    "Update Check Failed",
                    f"Error checking for updates: {str(e)}"
                ))
                
    def on_close(self):
        try:
            self.settings["interval_ms"] = self.interval_entry.get_float()
            self.settings["duty_cycle"] = self.duty_entry.get_float()
            self.settings["hold_time"] = self.hold_entry.get_float()
            self.settings["click_limit"] = self.limit_entry.get_int()
            save_settings(self.settings)
        except Exception as e:
            print(f"Error saving settings on close: {e}")

        if self.clicker_engine.clicking:
            self.clicker_engine.stop_clicking()

        if self.hotkey_manager:
            self.hotkey_manager.stop_listener()
            
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()

def check_macos_version():
    """Check if running on macOS and return version info."""
    if platform.system() != "Darwin":
        messagebox.showerror(
            "Unsupported Operating System",
            "This application is designed for macOS only."
        )
        sys.exit(1)
        
    version_str = platform.mac_ver()[0]
    version_parts = [int(x) for x in version_str.split('.')]

    if version_parts[0] < 10 or (version_parts[0] == 10 and version_parts[1] < 12):
        messagebox.showwarning(
            "Unsupported macOS Version",
            f"You are running macOS {version_str}. This application works best on macOS 10.12 (Sierra) or newer."
        )

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import pynput
        from Quartz import CGEventCreate
        return True
    except ImportError as e:
        messagebox.showerror(
            "Missing Dependencies",
            f"Error: {str(e)}\n\n"
            "Please install the required dependencies by running:\n"
            "pip3 install -r requirements.txt"
        )
        return False

def main():
    """Main entry point for the application."""
    try:
        check_macos_version()

        if not check_dependencies():
            sys.exit(1)

        app = AeroutSpeedAutoClickerGUI()
        app.run()
        
    except Exception as e:
        error_message = f"An unexpected error occurred:\n{str(e)}"
        print(error_message)
        messagebox.showerror("Error", error_message)
        sys.exit(1)

if __name__ == "__main__":
    main()
