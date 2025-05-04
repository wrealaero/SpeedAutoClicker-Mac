#!/usr/bin/env python3
"""
Aerout SpeedAutoClicker for macOS :D
A hopefully high performing autoclicker with advanced features(cap)
"""

import os
import sys
import time
import json
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import urllib.request
from pynput import keyboard, mouse
from pynput.mouse import Button, Controller as MouseController
import pyautogui
from logger import app_logger

VERSION = "1.1.0"
GITHUB_REPO = "wrealaero/SpeedAutoClicker-Mac"
CONFIG_DIR = os.path.expanduser("~/Documents/AeroutClicker/configs")

os.makedirs(CONFIG_DIR, exist_ok=True)

clicking = False
click_count = 0
click_interval_ms = 100.0 
hold_ratio = 0.5
hold_time = 0.0 
mouse_controller = MouseController()
hotkey = {"type": "keyboard", "keys": ["f6"]}
mouse_button = "left"
click_mode = "toggle"
limit_enabled = False
click_limit = 100
theme = "default"
custom_colors = {"bg": "#f0f0f0", "fg": "#000000", "accent": "#0078d7"}

capturing = False
overlay = None
capture_keys = set()
last_combo = set()

def load_settings():
    """Load settings from the configuration file"""
    try:
        settings_path = os.path.expanduser("~/Documents/AeroutClicker/settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                app_logger.info("Settings loaded successfully")
                return settings
        else:
            app_logger.info("No settings file found, using defaults")
            return {
                "cps": 10.0,
                "duty": 50.0,
                "hold_time": 0.0,
                "mode": "toggle",
                "button": "left",
                "limit_enabled": False,
                "click_limit": 100,
                "hotkey": {"type": "keyboard", "keys": ["f6"]},
                "theme": "default",
                "custom_colors": {"bg": "#f0f0f0", "fg": "#000000", "accent": "#0078d7"}
            }
    except Exception as e:
        app_logger.error(f"Error loading settings: {e}", exc_info=True)
        return {
            "cps": 10.0,
            "duty": 50.0,
            "hold_time": 0.0,
            "mode": "toggle",
            "button": "left",
            "limit_enabled": False,
            "click_limit": 100,
            "hotkey": {"type": "keyboard", "keys": ["f6"]},
            "theme": "default",
            "custom_colors": {"bg": "#f0f0f0", "fg": "#000000", "accent": "#0078d7"}
        }

def save_settings(settings):
    """Save settings to the configuration file"""
    try:
        settings_dir = os.path.expanduser("~/Documents/AeroutClicker")
        os.makedirs(settings_dir, exist_ok=True)
        settings_path = os.path.join(settings_dir, "settings.json")
        
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)
            app_logger.info("Settings saved successfully")
    except Exception as e:
        app_logger.error(f"Error saving settings: {e}", exc_info=True)
        messagebox.showerror("Error", f"Failed to save settings: {e}")

# Load settings
cfg = load_settings()
click_interval_ms = 1000.0 / cfg["cps"]
hold_ratio = cfg["duty"] / 100.0
hold_time = cfg["hold_time"]
mouse_button = cfg["button"]
click_mode = cfg["mode"]
limit_enabled = cfg["limit_enabled"]
click_limit = cfg["click_limit"]
hotkey = cfg["hotkey"]
theme = cfg["theme"]
custom_colors = cfg.get("custom_colors", {"bg": "#f0f0f0", "fg": "#000000", "accent": "#0078d7"})

def start_clicking():
    """Start the autoclicker"""
    global clicking, click_count
    
    if clicking:
        return
    
    app_logger.info("Starting autoclicker")
    app_logger.log_ui_action("start_clicking", 
                            f"CPS: {cps_var.get()}, Button: {button_var.get()}, Mode: {mode_var.get()}")
    
    clicking = True
    click_count = 0
    click_counter_var.set("Clicks: 0")
    update_status("Running")
    status_indicator.config(bg="green")
    
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")

    click_thread = threading.Thread(target=click_loop, daemon=True)
    click_thread.start()

def stop_clicking():
    """Stop the autoclicker"""
    global clicking
    
    if not clicking:
        return
    
    app_logger.info(f"Stopping autoclicker after {click_count} clicks")
    app_logger.log_ui_action("stop_clicking")
    
    clicking = False
    update_status("Stopped")
    status_indicator.config(bg="red")
    
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")

def click_loop():
    """Main clicking loop that runs in a separate thread"""
    global clicking, click_count
    
    app_logger.debug("Click loop started")

    interval = click_interval_ms / 1000.0

    try:
        timer = time.perf_counter
    except AttributeError:
        timer = time.time
    
    next_click_time = timer()
    
    while clicking:
        try:
            current_time = timer()

            if current_time >= next_click_time:
                if perform_click():
                    click_count += 1
                    click_counter_var.set(f"Clicks: {click_count}")

                    if limit_var.get() and click_count >= int(limit_entry.get()):
                        app_logger.info(f"Click limit reached: {click_count} clicks")
                        root.after(0, stop_clicking)
                        break

                next_click_time = current_time + interval

            sleep_time = min(0.001, (next_click_time - timer()) * 0.8)
            if sleep_time > 0:
                time.sleep(sleep_time)
            
        except Exception as e:
            app_logger.error(f"Error in click loop: {e}", exc_info=True)
            root.after(0, lambda: handle_click_error(e))
            break
    
    app_logger.debug("Click loop ended")

def handle_click_error(error):
    """Handle errors that occur during clicking"""
    stop_clicking()
    messagebox.showerror("Error", f"An error occurred while clicking: {error}")

def perform_click():
    """Perform a single click with the selected mouse button"""
    try:
        button = button_var.get()

        x, y = pyautogui.position()

        if sys.platform == 'darwin':
            try:
                from Quartz import CGEventCreateMouseEvent, CGEventPost, kCGEventMouseDown, kCGEventMouseUp
                from Quartz import kCGHIDEventTap, kCGMouseButtonLeft, kCGMouseButtonRight

                button_map = {
                    "left": kCGMouseButtonLeft,
                    "right": kCGMouseButtonRight,
                }
                
                if button in ["left", "right"]:
                    mouse_down = CGEventCreateMouseEvent(
                        None, kCGEventMouseDown, (x, y), button_map[button]
                    )
                    CGEventPost(kCGHIDEventTap, mouse_down)
                    app_logger.log_click_event("press", button, x, y)

                    if hold_time > 0:
                        time.sleep(hold_time / 1000.0)
                    else:
                        time.sleep((click_interval_ms * hold_ratio) / 1000.0)
                    
                    mouse_up = CGEventCreateMouseEvent(
                        None, kCGEventMouseUp, (x, y), button_map[button]
                    )
                    CGEventPost(kCGHIDEventTap, mouse_up)
                    app_logger.log_click_event("release", button, x, y)
                    
                    return True
                else:
                    return perform_click_pynput(button, x, y)
            except Exception as e:
                app_logger.warning(f"CoreGraphics click failed, falling back to pynput: {e}")
                return perform_click_pynput(button, x, y)
        else:
            return perform_click_pynput(button, x, y)
    except Exception as e:
        app_logger.error(f"Error performing click: {e}", exc_info=True)
        return False

def perform_click_pynput(button, x, y):
    """Perform a click using pynput (fallback method)"""
    try:
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle
        }

        mouse_controller.press(button_map[button])
        app_logger.log_click_event("press", button, x, y)

        if hold_time > 0:
            time.sleep(hold_time / 1000.0)
        else:
            time.sleep((click_interval_ms * hold_ratio) / 1000.0)

        mouse_controller.release(button_map[button])
        app_logger.log_click_event("release", button, x, y)
        
        return True
    except Exception as e:
        app_logger.error(f"Error in pynput click: {e}", exc_info=True)
        return False

def on_key_press(key):
    """Handle key press events"""
    global capturing, capture_keys, last_combo
    
    try:
        if hasattr(key, 'char') and key.char:
            key_str = key.char.lower()
        elif hasattr(key, 'name'):
            key_str = key.name.lower()
        else:
            key_str = str(key).lower().replace("key.", "")

        if capturing:
            if key_str == 'esc':
                app_logger.info("Hotkey capture cancelled")
                root.after(0, lambda: cancel_capture())
                return

            capture_keys.add(key_str)

            if overlay:
                keys_text = "+".join(sorted(capture_keys))
                root.after(0, lambda: update_overlay_text(keys_text))

        elif hotkey["type"] == "keyboard":
            hotkey_keys = set(hotkey.get("keys", []))

            last_combo.add(key_str)

            if last_combo == hotkey_keys:
                app_logger.log_hotkey_event("triggered", keys=list(hotkey_keys))
                if click_mode == "toggle":
                    if clicking:
                        root.after(0, stop_clicking)
                    else:
                        root.after(0, start_clicking)
                elif click_mode == "hold" and not clicking:
                    root.after(0, start_clicking)
    
    except Exception as e:
        app_logger.error(f"Error in key press handler: {e}", exc_info=True)

def on_key_release(key):
    """Handle key release events"""
    global last_combo
    
    try:
        if hasattr(key, 'char') and key.char:
            key_str = key.char.lower()
        elif hasattr(key, 'name'):
            key_str = key.name.lower()
        else:
            key_str = str(key).lower().replace("key.", "")

        if key_str in last_combo:
            last_combo.remove(key_str)

        if click_mode == "hold" and clicking and hotkey["type"] == "keyboard":
            hotkey_keys = set(hotkey.get("keys", []))
            if key_str in hotkey_keys:
                app_logger.log_hotkey_event("released", keys=[key_str])
                root.after(0, stop_clicking)
    
    except Exception as e:
        app_logger.error(f"Error in key release handler: {e}", exc_info=True)

def on_mouse_click(x, y, button, pressed):
    """Handle mouse click events for hotkey detection"""
    try:
        button_str = str(button).replace("Button.", "").lower()

        if hotkey["type"] == "mouse" and button_str == hotkey.get("button", ""):
            if pressed:
                app_logger.log_hotkey_event("triggered", keys=[button_str])
                if click_mode == "toggle":
                    if clicking:
                        root.after(0, stop_clicking)
                    else:
                        root.after(0, start_clicking)
                elif click_mode == "hold" and not clicking:
                    root.after(0, start_clicking)
            elif click_mode == "hold" and clicking:
                app_logger.log_hotkey_event("released", keys=[button_str])
                root.after(0, stop_clicking)
    
    except Exception as e:
        app_logger.error(f"Error in mouse click handler: {e}", exc_info=True)

def start_capture():
    """Start capturing a hotkey combination"""
    global capturing, capture_keys, overlay
    
    app_logger.info("Starting hotkey capture")

    capturing = True
    capture_keys = set()

    overlay = tk.Toplevel(root)
    overlay.title("Capturing Hotkey")
    overlay.geometry("300x100")
    overlay.attributes("-topmost", True)

    overlay.update_idletasks()
    width = overlay.winfo_width()
    height = overlay.winfo_height()
    x = (overlay.winfo_screenwidth() // 2) - (width // 2)
    y = (overlay.winfo_screenheight() // 2) - (height // 2)
    overlay.geometry(f"{width}x{height}+{x}+{y}")

    ttk.Label(overlay, text="Press the key(s) for your hotkey\nPress Esc to cancel").pack(pady=10)
    
    global overlay_label
    overlay_label = ttk.Label(overlay, text="Waiting for input...")
    overlay_label.pack(pady=10)

    ttk.Button(overlay, text="Set Hotkey", command=finish_capture).pack(pady=5)

def update_overlay_text(text):
    """Update the text in the hotkey capture overlay"""
    if overlay and overlay_label:
        overlay_label.config(text=text)

def finish_capture():
    """Finish capturing a hotkey combination"""
    global capturing, hotkey
    
    if not capture_keys:
        messagebox.showwarning("No Keys", "No keys were captured. Hotkey not changed.")
        cancel_capture()
        return

    hotkey = {"type": "keyboard", "keys": sorted(list(capture_keys))}

    hotkey_text = "+".join(hotkey["keys"])
    hotkey_display_var.set(hotkey_text)
    
    app_logger.info(f"New hotkey set: {hotkey_text}")
    app_logger.log_setting_change("hotkey", "previous", hotkey_text)

    if overlay:
        overlay.destroy()
    
    capturing = False

def cancel_capture():
    """Cancel hotkey capture"""
    global capturing
    
    capturing = False

    if overlay:
        overlay.destroy()

def update_click_interval(*args):
    """Update the click interval based on CPS"""
    global click_interval_ms
    
    try:
        cps = float(cps_var.get())
        if cps <= 0:
            cps = 0.1
        
        click_interval_ms = 1000.0 / cps
        app_logger.debug(f"Click interval updated: {click_interval_ms:.2f}ms (CPS: {cps})")
        app_logger.log_setting_change("cps", "previous", cps)
    except ValueError:
        cps_var.set("10.0")
        click_interval_ms = 100.0
        app_logger.warning("Invalid CPS value, reset to default")

def update_duty_cycle(*args):
    """Update the duty cycle ratio"""
    global hold_ratio
    
    try:
        duty = float(duty_var.get())
        if duty < 1:
            duty = 1
        elif duty > 99:
            duty = 99
        
        hold_ratio = duty / 100.0
        app_logger.debug(f"Duty cycle updated: {duty}% (ratio: {hold_ratio:.2f})")
        app_logger.log_setting_change("duty_cycle", "previous", duty)
    except ValueError:
        duty_var.set("50.0")
        hold_ratio = 0.5
        app_logger.warning("Invalid duty cycle value, reset to default")

def update_hold_time(*args):
    """Update the hold time"""
    global hold_time
    
    try:
        hold_time = float(hold_var.get())
        app_logger.debug(f"Hold time updated: {hold_time:.2f}ms")
        app_logger.log_setting_change("hold_time", "previous", hold_time)
    except ValueError:
        hold_var.set("0.00")
        hold_time = 0.0
        app_logger.warning("Invalid hold time value, reset to default")

def update_status(status):
    """Update the status display"""
    status_var.set(status)

def toggle_limit_entry():
    """Enable or disable the click limit entry field"""
    if limit_var.get():
        limit_entry.config(state="normal")
        app_logger.debug("Click limit enabled")
    else:
        limit_entry.config(state="disabled")
        app_logger.debug("Click limit disabled")

def save_current_settings():
    """Save the current settings to the configuration file"""
    settings = {
        "cps": float(cps_var.get()),
        "duty": float(duty_var.get()),
        "hold_time": float(hold_var.get()),
        "mode": mode_var.get(),
        "button": button_var.get(),
        "limit_enabled": limit_var.get(),
        "click_limit": int(limit_entry.get()) if limit_entry.get().isdigit() else 100,
        "hotkey": hotkey,
        "theme": theme,
        "custom_colors": custom_colors
    }
    
    save_settings(settings)
    app_logger.info("Current settings saved")

def export_config(name):
    """Export the current configuration to a file"""
    if not name:
        messagebox.showerror("Error", "Please enter a configuration name")
        return
    
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)

        config_path = os.path.join(CONFIG_DIR, f"{name}.json")

        config = {
            "cps": float(cps_var.get()),
            "duty": float(duty_var.get()),
            "hold_time": float(hold_var.get()),
            "mode": mode_var.get(),
            "button": button_var.get(),
            "limit_enabled": limit_var.get(),
            "click_limit": int(limit_entry.get()) if limit_entry.get().isdigit() else 100,
            "hotkey": hotkey
        }

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        messagebox.showinfo("Success", f"Configuration '{name}' exported successfully")
        app_logger.info(f"Configuration exported: {name}")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export configuration: {e}")
        app_logger.error(f"Error exporting configuration: {e}", exc_info=True)

def import_config(name):
    """Import a configuration from a file"""
    if not name:
        messagebox.showerror("Error", "Please enter a configuration name")
        return
    
    try:
        config_path = os.path.join(CONFIG_DIR, f"{name}.json")
        if not os.path.exists(config_path):
            messagebox.showerror("Error", f"Configuration '{name}' not found")
            return

        with open(config_path, 'r') as f:
            config = json.load(f)

        cps_var.set(str(config["cps"]))
        duty_var.set(str(config["duty"]))
        hold_var.set(str(config["hold_time"]))
        mode_var.set(config["mode"])
        button_var.set(config["button"])
        limit_var.set(config["limit_enabled"])
        limit_entry.delete(0, tk.END)
        limit_entry.insert(0, str(config["click_limit"]))
        toggle_limit_entry()

        global hotkey
        hotkey = config["hotkey"]
        if hotkey["type"] == "keyboard":
            hotkey_display_var.set("+".join(hotkey["keys"]))
        else:
            hotkey_display_var.set(f"Mouse {hotkey['button']}")
        
        messagebox.showinfo("Success", f"Configuration '{name}' imported successfully")
        app_logger.info(f"Configuration imported: {name}")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import configuration: {e}")
        app_logger.error(f"Error importing configuration: {e}", exc_info=True)

def apply_theme():
    """Apply the selected theme to the application"""
    global theme
    theme = theme_var.get()
    
    app_logger.info(f"Applying theme: {theme}")
    
    if theme == "default":
        style = ttk.Style()
        style.theme_use('default')
    
    elif theme == "dark":
        root.configure(bg="#2d2d2d")
        style = ttk.Style()
        style.configure("TFrame", background="#2d2d2d")
        style.configure("TLabel", background="#2d2d2d", foreground="#ffffff")
        style.configure("TButton", background="#444444", foreground="#ffffff")
        style.configure("TCheckbutton", background="#2d2d2d", foreground="#ffffff")
        style.configure("TRadiobutton", background="#2d2d2d", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#444444", foreground="#ffffff")
        style.configure("TNotebook", background="#2d2d2d", foreground="#ffffff")
        style.configure("TNotebook.Tab", background="#444444", foreground="#ffffff")
    
    elif theme == "light":
        root.configure(bg="#f0f0f0")
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", foreground="#000000")
        style.configure("TButton", background="#e0e0e0", foreground="#000000")
        style.configure("TCheckbutton", background="#f0f0f0", foreground="#000000")
        style.configure("TRadiobutton", background="#f0f0f0", foreground="#000000")
        style.configure("TEntry", fieldbackground="#ffffff", foreground="#000000")
        style.configure("TNotebook", background="#f0f0f0", foreground="#000000")
        style.configure("TNotebook.Tab", background="#e0e0e0", foreground="#000000")
    
    elif theme == "custom":
        root.configure(bg=custom_colors["bg"])
        style = ttk.Style()
        style.configure("TFrame", background=custom_colors["bg"])
        style.configure("TLabel", background=custom_colors["bg"], foreground=custom_colors["fg"])
        style.configure("TButton", background=custom_colors["accent"], foreground=custom_colors["fg"])
        style.configure("TCheckbutton", background=custom_colors["bg"], foreground=custom_colors["fg"])
        style.configure("TRadiobutton", background=custom_colors["bg"], foreground=custom_colors["fg"])
        style.configure("TEntry", fieldbackground=custom_colors["bg"], foreground=custom_colors["fg"])
        style.configure("TNotebook", background=custom_colors["bg"], foreground=custom_colors["fg"])
        style.configure("TNotebook.Tab", background=custom_colors["accent"], foreground=custom_colors["fg"])
    
    app_logger.log_setting_change("theme", "previous", theme)

def choose_custom_color():
    """Open a color chooser dialog for custom theme colors"""
    global custom_colors
    
    app_logger.debug("Opening color chooser for custom theme")

    bg_color = colorchooser.askcolor(title="Choose Background Color", initialcolor=custom_colors["bg"])
    if bg_color[1]:
        custom_colors["bg"] = bg_color[1]

    fg_color = colorchooser.askcolor(title="Choose Text Color", initialcolor=custom_colors["fg"])
    if fg_color[1]:
        custom_colors["fg"] = fg_color[1]

    accent_color = colorchooser.askcolor(title="Choose Accent Color", initialcolor=custom_colors["accent"])
    if accent_color[1]:
        custom_colors["accent"] = accent_color[1]

    theme_var.set("custom")
    apply_theme()
    
    app_logger.info(f"Custom theme colors set: {custom_colors}")

def check_for_updates(show_message=True):
    """Check for updates to the application"""
    try:
        app_logger.info("Checking for updates...")

        req = urllib.request.Request(
            f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
            headers={"User-Agent": f"AeroutClicker/{VERSION}"}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", "").lstrip("v")
            
            app_logger.info(f"Current version: {VERSION}, Latest version: {latest_version}")
            
            if latest_version and latest_version != VERSION:
                if show_message:
                    update_msg = f"A new version is available: v{latest_version}\nWould you like to update now?"
                    if messagebox.askyesno("Update Available", update_msg):
                        app_logger.info(f"User initiated update to version {latest_version}")
                        subprocess.Popen([sys.executable, "updater.py"])
                        root.destroy() 
                return True
            else:
                if show_message:
                    messagebox.showinfo("No Updates", "You are using the latest version.")
                return False
    
    except Exception as e:
        app_logger.error(f"Error checking for updates: {e}", exc_info=True)
        if show_message:
            messagebox.showerror("Update Check Failed", f"Failed to check for updates: {e}")
        return False

def create_diagnostic_report():
    """Create a diagnostic report for troubleshooting"""
    try:
        report_path = app_logger.create_diagnostic_report()

        messagebox.showinfo(
            "Diagnostic Report Created", 
            f"A diagnostic report has been created at:\n{report_path}\n\n"
            "Please share this file when reporting issues."
        )

        if sys.platform == 'darwin': 
            subprocess.run(['open', os.path.dirname(report_path)])
        elif sys.platform == 'win32':  
            subprocess.run(['explorer', os.path.dirname(report_path)])
        else: 
            subprocess.run(['xdg-open', os.path.dirname(report_path)])
            
        app_logger.info(f"Diagnostic report created: {report_path}")
    
    except Exception as e:
        app_logger.error(f"Error creating diagnostic report: {e}", exc_info=True)
        messagebox.showerror("Error", f"Failed to create diagnostic report: {e}")

    """Create the application UI"""
    global root, start_btn, stop_btn, status_indicator, overlay_label
    global cps_var, duty_var, hold_var, button_var, mode_var, limit_var, limit_entry
    global status_var, click_counter_var, hotkey_display_var, theme_var

    root = tk.Tk()
    root.title(f"Aerout SpeedAutoClicker v{VERSION}")
    root.geometry("500x450")
    root.resizable(False, False)

    if sys.platform == 'darwin': 
        try:
            from Cocoa import NSImage, NSApplication
            image = NSImage.alloc().initByReferencingFile_("icon.png")
            NSApplication.sharedApplication().setApplicationIconImage_(image)
        except:
            pass

    cps_var = tk.StringVar(value="10.0")
    duty_var = tk.StringVar(value="50.0")
    hold_var = tk.StringVar(value="0.00")
    button_var = tk.StringVar(value=mouse_button)
    mode_var = tk.StringVar(value=click_mode)
    limit_var = tk.BooleanVar(value=limit_enabled)
    status_var = tk.StringVar(value="Ready")
    click_counter_var = tk.StringVar(value="Clicks: 0")
    hotkey_display_var = tk.StringVar(value="+".join(hotkey["keys"]) if hotkey["type"] == "keyboard" else f"Mouse {hotkey['button']}")
    theme_var = tk.StringVar(value=theme)

    cps_var.trace_add("write", update_click_interval)
    duty_var.trace_add("write", update_duty_cycle)
    hold_var.trace_add("write", update_hold_time)
    theme_var.trace_add("write", lambda *args: apply_theme())

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    main_tab = ttk.Frame(notebook)
    advanced_tab = ttk.Frame(notebook)
    settings_tab = ttk.Frame(notebook)
    help_tab = ttk.Frame(notebook)
    
    notebook.add(main_tab, text="Main")
    notebook.add(advanced_tab, text="Advanced")
    notebook.add(settings_tab, text="Settings")
    notebook.add(help_tab, text="Help")
    

    status_frame = ttk.Frame(main_tab)
    status_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
    ttk.Label(status_frame, textvariable=status_var).pack(side=tk.LEFT, padx=5)
    
    status_indicator = tk.Label(status_frame, width=3, bg="red")
    status_indicator.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(status_frame, textvariable=click_counter_var).pack(side=tk.RIGHT, padx=5)

    cps_frame = ttk.Frame(main_tab)
    cps_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Label(cps_frame, text="Clicks Per Second (CPS):").pack(side=tk.LEFT, padx=5)
    ttk.Entry(cps_frame, textvariable=cps_var, width=8).pack(side=tk.LEFT, padx=5)

    duty_frame = ttk.Frame(main_tab)
    duty_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Label(duty_frame, text="Click Duty Cycle (%):").pack(side=tk.LEFT, padx=5)
    ttk.Entry(duty_frame, textvariable=duty_var, width=8).pack(side=tk.LEFT, padx=5)
    ttk.Label(duty_frame, text="(50% = balanced, higher = longer press)").pack(side=tk.LEFT, padx=5)

    button_frame = ttk.Frame(main_tab)
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Label(button_frame, text="Mouse Button:").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(button_frame, text="Left", variable=button_var, value="left").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(button_frame, text="Right", variable=button_var, value="right").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(button_frame, text="Middle", variable=button_var, value="middle").pack(side=tk.LEFT, padx=5)

    mode_frame = ttk.Frame(main_tab)
    mode_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Label(mode_frame, text="Click Mode:").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(mode_frame, text="Toggle (Press to start/stop)", variable=mode_var, value="toggle").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(mode_frame, text="Hold (Click while key is down)", variable=mode_var, value="hold").pack(side=tk.LEFT, padx=5)

    hotkey_frame = ttk.Frame(main_tab)
    hotkey_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Label(hotkey_frame, text="Hotkey:").pack(side=tk.LEFT, padx=5)
    ttk.Label(hotkey_frame, textvariable=hotkey_display_var).pack(side=tk.LEFT, padx=5)
    ttk.Button(hotkey_frame, text="Set Hotkey", command=start_capture).pack(side=tk.LEFT, padx=5)

    control_frame = ttk.Frame(main_tab)
    control_frame.pack(fill=tk.X, padx=10, pady=10)
    
    start_btn = ttk.Button(control_frame, text="Start (F6)", command=start_clicking)
    start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    stop_btn = ttk.Button(control_frame, text="Stop", command=stop_clicking, state="disabled")
    stop_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    save_btn = ttk.Button(control_frame, text="Save Settings", command=save_current_settings)
    save_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    hold_frame = ttk.Frame(advanced_tab)
    hold_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Label(hold_frame, text="Hold Time (ms):").pack(side=tk.LEFT, padx=5)
    ttk.Entry(hold_frame, textvariable=hold_var, width=8).pack(side=tk.LEFT, padx=5)
    ttk.Label(hold_frame, text="(0 = use duty cycle)").pack(side=tk.LEFT, padx=5)

    limit_frame = ttk.Frame(advanced_tab)
    limit_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Checkbutton(limit_frame, text="Limit Clicks:", variable=limit_var, command=toggle_limit_entry).pack(side=tk.LEFT, padx=5)
    limit_entry = ttk.Entry(limit_frame, width=8)
    limit_entry.insert(0, str(click_limit))
    limit_entry.pack(side=tk.LEFT, padx=5)
    limit_entry.config(state="disabled" if not limit_enabled else "normal")

    config_frame = ttk.LabelFrame(advanced_tab, text="Configuration Management")
    config_frame.pack(fill=tk.X, padx=10, pady=10)
    
    config_name_frame = ttk.Frame(config_frame)
    config_name_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(config_name_frame, text="Config Name:").pack(side=tk.LEFT, padx=5)
    config_name_entry = ttk.Entry(config_name_frame, width=20)
    config_name_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    config_btn_frame = ttk.Frame(config_frame)
    config_btn_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(config_btn_frame, text="Export", 
               command=lambda: export_config(config_name_entry.get())).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    ttk.Button(config_btn_frame, text="Import", 
               command=lambda: import_config(config_name_entry.get())).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    diagnostic_frame = ttk.LabelFrame(advanced_tab, text="Diagnostics")
    diagnostic_frame.pack(fill=tk.X, padx=10, pady=10)
    
    ttk.Button(diagnostic_frame, text="Create Diagnostic Report", 
               command=create_diagnostic_report).pack(padx=5, pady=5, fill=tk.X)
    
    ttk.Label(diagnostic_frame, text="Use this to generate a report when experiencing issues.").pack(padx=5, pady=5)

    theme_frame = ttk.LabelFrame(settings_tab, text="Theme")
    theme_frame.pack(fill=tk.X, padx=10, pady=10)
    
    ttk.Radiobutton(theme_frame, text="Default", variable=theme_var, value="default").pack(anchor=tk.W, padx=10, pady=2)
    ttk.Radiobutton(theme_frame, text="Dark", variable=theme_var, value="dark").pack(anchor=tk.W, padx=10, pady=2)
    ttk.Radiobutton(theme_frame, text="Light", variable=theme_var, value="light").pack(anchor=tk.W, padx=10, pady=2)
    ttk.Radiobutton(theme_frame, text="Custom", variable=theme_var, value="custom").pack(anchor=tk.W, padx=10, pady=2)
    
    ttk.Button(theme_frame, text="Choose Custom Colors", command=choose_custom_color).pack(padx=10, pady=5, fill=tk.X)

    update_frame = ttk.LabelFrame(settings_tab, text="Updates")
    update_frame.pack(fill=tk.X, padx=10, pady=10)
    
    ttk.Label(update_frame, text=f"Current Version: {VERSION}").pack(anchor=tk.W, padx=10, pady=5)
    ttk.Button(update_frame, text="Check for Updates", command=lambda: check_for_updates(True)).pack(padx=10, pady=5, fill=tk.X)

    about_frame = ttk.LabelFrame(settings_tab, text="About")
    about_frame.pack(fill=tk.X, padx=10, pady=10)
    
    ttk.Label(about_frame, text="Aerout SpeedAutoClicker for macOS").pack(anchor=tk.W, padx=10, pady=2)
    ttk.Label(about_frame, text=f"Version {VERSION}").pack(anchor=tk.W, padx=10, pady=2)
    ttk.Label(about_frame, text="Created by Aerout").pack(anchor=tk.W, padx=10, pady=2)
    
    help_text = """
    Aerout SpeedAutoClicker Help
    
    Basic Usage:
    1. Set your desired Clicks Per Second (CPS)
    2. Choose which mouse button to click
    3. Select Toggle or Hold mode
    4. Press the hotkey (default: F6) to start/stop clicking
    
    Advanced Features:
    • Duty Cycle: Controls how long the mouse button is held down
      - 50% is balanced (equal press and release time)
      - Higher values make the press longer
      - Lower values make the release longer
    
    • Hold Time: Precise control over button press duration in milliseconds
      - Set to 0 to use the duty cycle instead
    
    • Click Limit: Automatically stop after a specific number of clicks
    
    • Configurations: Save and load different clicking profiles
    
    Troubleshooting:
    • If hotkeys don't work, try running the app with administrator privileges
    • On Apple Silicon Macs, make sure you're using the native version
    • Use the Diagnostic Report feature to help identify issues
    
    For more help or to report bugs, visit:
    https://github.com/wrealaero/SpeedAutoClicker-Mac/issues
    """
    
    help_scroll = ttk.Scrollbar(help_tab)
    help_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    help_text_widget = tk.Text(help_tab, wrap=tk.WORD, yscrollcommand=help_scroll.set)
    help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    help_text_widget.insert(tk.END, help_text)
    help_text_widget.config(state=tk.DISABLED)
    
    help_scroll.config(command=help_text_widget.yview)

    apply_theme()

    root.after(1000, lambda: check_for_updates(False))
    
    app_logger.info("UI created successfully")
    return root

def main():
    """Main application entry point"""
    app_logger.info(f"Starting Aerout SpeedAutoClicker v{VERSION}")

    root = create_ui()

    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    keyboard_listener.start()

    mouse_listener = mouse.Listener(on_click=on_mouse_click)
    mouse_listener.start()

    try:
        root.mainloop()
    except Exception as e:
        app_logger.critical(f"Error in main loop: {e}", exc_info=True)
    finally:
        keyboard_listener.stop()
        mouse_listener.stop()
        app_logger.info("Application shutting down")

if __name__ == "__main__":
    main()
