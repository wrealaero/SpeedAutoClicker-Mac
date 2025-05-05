#!/usr/bin/env python3
"""
Aerout SpeedAutoClicker for macOS
A good autoclicker with cool features :D
"""

import os
import sys
import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from datetime import datetime
import pyautogui
from pynput import keyboard, mouse
from logger import app_logger
from packaging import version

VERSION = "1.1.0"
CONFIG_DIR = os.path.expanduser("~/Documents/AeroutClicker/configs")
SETTINGS_FILE = os.path.expanduser("~/Documents/AeroutClicker/settings.json")

os.makedirs(CONFIG_DIR, exist_ok=True)

mouse_button = "left"
click_mode = "toggle"
hotkey = {"type": "keyboard", "keys": ["f6"], "button": None}
click_interval = 0.1  
duty_cycle = 50.0  
hold_time = 0.0  
limit_enabled = False
click_limit = 100
theme = "default"
custom_colors = {"bg": "#2E2E2E", "fg": "#FFFFFF", "accent": "#007BFF"}

clicking = False
click_count = 0
capturing_hotkey = False
root = None
start_btn = None
stop_btn = None
status_indicator = None
overlay_label = None
cps_var = None
duty_var = None
hold_var = None
button_var = None
mode_var = None
limit_var = None
limit_entry = None
status_var = None
click_counter_var = None
hotkey_display_var = None
theme_var = None

def load_settings():
    """Load settings from file"""
    global mouse_button, click_mode, hotkey, click_interval, duty_cycle, hold_time
    global limit_enabled, click_limit, theme, custom_colors
    
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                
                mouse_button = settings.get('mouse_button', mouse_button)
                click_mode = settings.get('click_mode', click_mode)
                hotkey = settings.get('hotkey', hotkey)
                click_interval = settings.get('click_interval', click_interval)
                duty_cycle = settings.get('duty_cycle', duty_cycle)
                hold_time = settings.get('hold_time', hold_time)
                limit_enabled = settings.get('limit_enabled', limit_enabled)
                click_limit = settings.get('click_limit', click_limit)
                theme = settings.get('theme', theme)
                custom_colors = settings.get('custom_colors', custom_colors)
                
                app_logger.info("Settings loaded successfully")
    except Exception as e:
        app_logger.error(f"Error loading settings: {e}", exc_info=True)

def save_settings():
    """Save settings to file"""
    try:
        settings = {
            'mouse_button': mouse_button,
            'click_mode': click_mode,
            'hotkey': hotkey,
            'click_interval': click_interval,
            'duty_cycle': duty_cycle,
            'hold_time': hold_time,
            'limit_enabled': limit_enabled,
            'click_limit': click_limit,
            'theme': theme,
            'custom_colors': custom_colors
        }
        
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        
        app_logger.info("Settings saved successfully")
    except Exception as e:
        app_logger.error(f"Error saving settings: {e}", exc_info=True)

def save_current_settings():
    """Save current UI settings to variables and file"""
    global mouse_button, click_mode, click_interval, duty_cycle, hold_time
    global limit_enabled, click_limit, theme
    
    try:
        mouse_button = button_var.get()
        click_mode = mode_var.get()
        
        try:
            cps = float(cps_var.get())
            if cps > 0:
                click_interval = 1.0 / cps
        except ValueError:
            pass
        
        try:
            duty_cycle = float(duty_var.get())
        except ValueError:
            pass
        
        try:
            hold_time = float(hold_var.get())
        except ValueError:
            pass
        
        limit_enabled = limit_var.get()
        
        try:
            click_limit = int(limit_entry.get())
        except ValueError:
            pass
        
        theme = theme_var.get()

        save_settings()
        
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")
        app_logger.info("Current settings saved by user")
    
    except Exception as e:
        app_logger.error(f"Error saving current settings: {e}", exc_info=True)
        messagebox.showerror("Error", f"Failed to save settings: {e}")

def export_config(name):
    """Export current configuration to a file"""
    if not name:
        messagebox.showerror("Error", "Please enter a configuration name")
        return
    
    try:
        config = {
            'mouse_button': button_var.get(),
            'click_mode': mode_var.get(),
            'cps': cps_var.get(),
            'duty_cycle': duty_var.get(),
            'hold_time': hold_var.get(),
            'limit_enabled': limit_var.get(),
            'click_limit': limit_entry.get(),
            'export_date': datetime.now().isoformat()
        }

        safe_name = "".join(c for c in name if c.isalnum() or c in "._- ").strip()
        if not safe_name:
            safe_name = "config"

        filename = os.path.join(CONFIG_DIR, f"{safe_name}.json")
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)
        
        messagebox.showinfo("Configuration Exported", f"Configuration '{name}' has been exported successfully.")
        app_logger.info(f"Configuration exported: {filename}")
    
    except Exception as e:
        app_logger.error(f"Error exporting configuration: {e}", exc_info=True)
        messagebox.showerror("Error", f"Failed to export configuration: {e}")

def import_config(name):
    """Import configuration from a file"""
    if not name:
        messagebox.showerror("Error", "Please enter a configuration name")
        return
    
    try:
        safe_name = "".join(c for c in name if c.isalnum() or c in "._- ").strip()
        if not safe_name:
            safe_name = "config"

        filename = os.path.join(CONFIG_DIR, f"{safe_name}.json")
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"Configuration '{name}' not found")
            return
        
        with open(filename, 'r') as f:
            config = json.load(f)

        button_var.set(config.get('mouse_button', 'left'))
        mode_var.set(config.get('click_mode', 'toggle'))
        cps_var.set(config.get('cps', '10.0'))
        duty_var.set(config.get('duty_cycle', '50.0'))
        hold_var.set(config.get('hold_time', '0.0'))
        limit_var.set(config.get('limit_enabled', False))
        limit_entry.delete(0, tk.END)
        limit_entry.insert(0, str(config.get('click_limit', 100)))
        toggle_limit_entry()
        
        messagebox.showinfo("Configuration Imported", f"Configuration '{name}' has been imported successfully.")
        app_logger.info(f"Configuration imported: {filename}")
    
    except Exception as e:
        app_logger.error(f"Error importing configuration: {e}", exc_info=True)
        messagebox.showerror("Error", f"Failed to import configuration: {e}")

def validate_numeric_input(P):
    """Validate that input is numeric"""
    if P == "" or P == ".":
        return True
    try:
        float(P)
        return True
    except ValueError:
        return False

def toggle_limit_entry():
    """Enable or disable the limit entry based on checkbox"""
    if limit_var.get():
        limit_entry.config(state="normal")
    else:
        limit_entry.config(state="disabled")

def update_click_interval(*args):
    """Update click interval from CPS"""
    global click_interval
    try:
        cps = float(cps_var.get())
        if cps > 0:
            click_interval = 1.0 / cps
    except ValueError:
        pass

def update_duty_cycle(*args):
    """Update duty cycle"""
    global duty_cycle
    try:
        duty_cycle = float(duty_var.get())
    except ValueError:
        pass

def update_hold_time(*args):
    """Update hold time"""
    global hold_time
    try:
        hold_time = float(hold_var.get())
    except ValueError:
        pass

def choose_custom_color():
    """Open color chooser dialog for custom theme"""
    try:
        bg_color = colorchooser.askcolor(
            title="Choose Background Color",
            initialcolor=custom_colors["bg"]
        )
        if bg_color[1]:
            custom_colors["bg"] = bg_color[1]

        fg_color = colorchooser.askcolor(
            title="Choose Text Color",
            initialcolor=custom_colors["fg"]
        )
        if fg_color[1]:
            custom_colors["fg"] = fg_color[1]

        accent_color = colorchooser.askcolor(
            title="Choose Accent Color",
            initialcolor=custom_colors["accent"]
        )
        if accent_color[1]:
            custom_colors["accent"] = accent_color[1]

        if theme_var.get() == "custom":
            apply_theme()
        
        app_logger.info("Custom colors updated")
    except Exception as e:
        app_logger.error(f"Error choosing custom colors: {e}", exc_info=True)

def apply_theme():
    """Apply the selected theme to the UI"""
    global theme
    
    theme = theme_var.get()
    
    try:
        if theme == "dark":
            style = ttk.Style()
            style.theme_use("clam")
            style.configure(".", 
                            background="#2E2E2E",
                            foreground="#FFFFFF",
                            fieldbackground="#3E3E3E",
                            troughcolor="#3E3E3E",
                            darkcolor="#2E2E2E",
                            lightcolor="#4E4E4E")
            style.configure("TButton", 
                            background="#007BFF",
                            foreground="#FFFFFF")
            style.map("TButton",
                     background=[("active", "#0069D9"), ("disabled", "#5C636A")],
                     foreground=[("disabled", "#C0C0C0")])
            style.configure("TCheckbutton", 
                            background="#2E2E2E",
                            foreground="#FFFFFF")
            style.configure("TRadiobutton", 
                            background="#2E2E2E",
                            foreground="#FFFFFF")
            style.configure("TLabel", 
                            background="#2E2E2E",
                            foreground="#FFFFFF")
            style.configure("TFrame", 
                            background="#2E2E2E")
            style.configure("TLabelframe", 
                            background="#2E2E2E",
                            foreground="#FFFFFF")
            style.configure("TLabelframe.Label", 
                            background="#2E2E2E",
                            foreground="#FFFFFF")
            style.configure("TNotebook", 
                            background="#2E2E2E",
                            foreground="#FFFFFF",
                            tabmargins=[2, 5, 2, 0])
            style.configure("TNotebook.Tab", 
                            background="#3E3E3E",
                            foreground="#FFFFFF",
                            padding=[10, 2])
            style.map("TNotebook.Tab",
                     background=[("selected", "#007BFF"), ("active", "#4E4E4E")],
                     foreground=[("selected", "#FFFFFF"), ("active", "#FFFFFF")])
            
            root.configure(bg="#2E2E2E")

            for widget in root.winfo_children():
                if isinstance(widget, tk.Text):
                    widget.configure(bg="#3E3E3E", fg="#FFFFFF", insertbackground="#FFFFFF")
        
        elif theme == "light":
            style = ttk.Style()
            style.theme_use("clam")
            style.configure(".", 
                            background="#F8F9FA",
                            foreground="#212529",
                            fieldbackground="#FFFFFF",
                            troughcolor="#E9ECEF",
                            darkcolor="#CED4DA",
                            lightcolor="#F8F9FA")
            style.configure("TButton", 
                            background="#007BFF",
                            foreground="#FFFFFF")
            style.map("TButton",
                     background=[("active", "#0069D9"), ("disabled", "#6C757D")],
                     foreground=[("disabled", "#DEE2E6")])
            style.configure("TCheckbutton", 
                            background="#F8F9FA",
                            foreground="#212529")
            style.configure("TRadiobutton", 
                            background="#F8F9FA",
                            foreground="#212529")
            style.configure("TLabel", 
                            background="#F8F9FA",
                            foreground="#212529")
            style.configure("TFrame", 
                            background="#F8F9FA")
            style.configure("TLabelframe", 
                            background="#F8F9FA",
                            foreground="#212529")
            style.configure("TLabelframe.Label", 
                            background="#F8F9FA",
                            foreground="#212529")
            style.configure("TNotebook", 
                            background="#F8F9FA",
                            foreground="#212529",
                            tabmargins=[2, 5, 2, 0])
            style.configure("TNotebook.Tab", 
                            background="#E9ECEF",
                            foreground="#212529",
                            padding=[10, 2])
            style.map("TNotebook.Tab",
                     background=[("selected", "#007BFF"), ("active", "#CED4DA")],
                     foreground=[("selected", "#FFFFFF"), ("active", "#212529")])
            
            root.configure(bg="#F8F9FA")

            for widget in root.winfo_children():
                if isinstance(widget, tk.Text):
                    widget.configure(bg="#FFFFFF", fg="#212529", insertbackground="#212529")
        
        elif theme == "custom":
            style = ttk.Style()
            style.theme_use("clam")
            style.configure(".", 
                            background=custom_colors["bg"],
                            foreground=custom_colors["fg"],
                            fieldbackground=custom_colors["bg"],
                            troughcolor=custom_colors["bg"])
            style.configure("TButton", 
                            background=custom_colors["accent"],
                            foreground=custom_colors["fg"])
            style.map("TButton",
                     background=[("active", custom_colors["accent"]), ("disabled", "#5C636A")],
                     foreground=[("disabled", "#C0C0C0")])
            style.configure("TCheckbutton", 
                            background=custom_colors["bg"],
                            foreground=custom_colors["fg"])
            style.configure("TRadiobutton", 
                            background=custom_colors["bg"],
                            foreground=custom_colors["fg"])
            style.configure("TLabel", 
                            background=custom_colors["bg"],
                            foreground=custom_colors["fg"])
            style.configure("TFrame", 
                            background=custom_colors["bg"])
            style.configure("TLabelframe", 
                            background=custom_colors["bg"],
                            foreground=custom_colors["fg"])
            style.configure("TLabelframe.Label", 
                            background=custom_colors["bg"],
                            foreground=custom_colors["fg"])
            style.configure("TNotebook", 
                            background=custom_colors["bg"],
                            foreground=custom_colors["fg"],
                            tabmargins=[2, 5, 2, 0])
            style.configure("TNotebook.Tab", 
                            background=custom_colors["bg"],
                            foreground=custom_colors["fg"],
                            padding=[10, 2])
            style.map("TNotebook.Tab",
                     background=[("selected", custom_colors["accent"]), ("active", custom_colors["bg"])],
                     foreground=[("selected", custom_colors["fg"]), ("active", custom_colors["fg"])])
            
            root.configure(bg=custom_colors["bg"])
            
            # Configure any Text widgets
            for widget in root.winfo_children():
                if isinstance(widget, tk.Text):
                    widget.configure(bg=custom_colors["bg"], fg=custom_colors["fg"], insertbackground=custom_colors["fg"])
        
        else:
            style = ttk.Style()
            style.theme_use("default")

            root.configure(bg=style.lookup("TFrame", "background"))

            for widget in root.winfo_children():
                if isinstance(widget, tk.Text):
                    widget.configure(bg="white", fg="black", insertbackground="black")
        
        app_logger.info(f"Applied theme: {theme}")
    
    except Exception as e:
        app_logger.error(f"Error applying theme: {e}", exc_info=True)

def check_for_updates(show_message=True):
    """Check for updates from GitHub"""
    try:
        import requests
        from packaging import version

        response = requests.get(
            "https://api.github.com/repos/wrealaero/SpeedAutoClicker-Mac/releases/latest",
            headers={"User-Agent": f"AeroutClicker/{VERSION}"},
            timeout=5
        )
        
        if response.status_code == 200:
            release_info = response.json()
            latest_version = release_info["tag_name"].lstrip("v")

            if version.parse(latest_version) > version.parse(VERSION):
                message = f"A new version ({latest_version}) is available!\n\nWould you like to update now?"
                if messagebox.askyesno("Update Available", message):
                    subprocess.Popen([sys.executable, "updater.py"])
                    root.destroy()
                return True
            else:
                if show_message:
                    messagebox.showinfo("No Updates", "You are using the latest version.")
                return False
        else:
            if show_message:
                messagebox.showerror("Update Check Failed", "Failed to check for updates. Please try again later.")
            return False
    
    except Exception as e:
        app_logger.error(f"Error checking for updates: {e}", exc_info=True)
        if show_message:
            messagebox.showerror("Update Check Failed", f"Error checking for updates: {e}")
        return False

def perform_click():
    """Perform a single click"""
    global click_count
    
    try:
        if hold_time > 0:
            press_duration = hold_time / 1000.0 
        else:
            press_duration = click_interval * (duty_cycle / 100.0)

        if mouse_button == "left":
            pyautogui.mouseDown(button="left")
            time.sleep(press_duration)
            pyautogui.mouseUp(button="left")
        elif mouse_button == "right":
            pyautogui.mouseDown(button="right")
            time.sleep(press_duration)
            pyautogui.mouseUp(button="right")
        elif mouse_button == "middle":
            pyautogui.mouseDown(button="middle")
            time.sleep(press_duration)
            pyautogui.mouseUp(button="middle")

        click_count += 1
        if click_counter_var:
            click_counter_var.set(f"Clicks: {click_count}")

        x, y = pyautogui.position()
        app_logger.log_click_event("click", mouse_button, x, y)

        if limit_enabled and click_count >= click_limit:
            stop_clicking()
            messagebox.showinfo("Click Limit Reached", f"Completed {click_limit} clicks.")
    
    except Exception as e:
        app_logger.error(f"Error performing click: {e}", exc_info=True)

def clicking_thread():
    """Thread function for continuous clicking"""
    global clicking
    
    try:
        while clicking:
            perform_click()
            release_duration = click_interval - (click_interval * (duty_cycle / 100.0))
            if release_duration < 0:
                release_duration = 0

            time.sleep(release_duration)
    
    except Exception as e:
        app_logger.error(f"Error in clicking thread: {e}", exc_info=True)
        clicking = False
        update_ui_state()

def start_clicking():
    """Start the autoclicker"""
    global clicking, click_count, click_thread
    
    if clicking:
        return
    
    try:
        if limit_enabled:
            click_count = 0
            if click_counter_var:
                click_counter_var.set(f"Clicks: {click_count}")

        clicking = True
        update_ui_state()

        click_thread = threading.Thread(target=clicking_thread)
        click_thread.daemon = True
        click_thread.start()
        
        app_logger.info("Clicking started")
    
    except Exception as e:
        app_logger.error(f"Error starting clicking: {e}", exc_info=True)
        clicking = False
        update_ui_state()

def stop_clicking():
    """Stop the autoclicker"""
    global clicking
    
    if not clicking:
        return
    
    try:
        clicking = False
        update_ui_state()
        
        app_logger.info("Clicking stopped")
    
    except Exception as e:
        app_logger.error(f"Error stopping clicking: {e}", exc_info=True)

def toggle_clicking():
    """Toggle the autoclicker on/off"""
    if clicking:
        stop_clicking()
    else:
        start_clicking()

def update_ui_state():
    """Update UI elements based on clicking state"""
    if clicking:
        if start_btn:
            start_btn.config(state="disabled")
        if stop_btn:
            stop_btn.config(state="normal")
        if status_var:
            status_var.set("Status: Running")
        if status_indicator:
            status_indicator.config(background="#4CAF50") 
    else:
        if start_btn:
            start_btn.config(state="normal")
        if stop_btn:
            stop_btn.config(state="disabled")
        if status_var:
            status_var.set("Status: Stopped")
        if status_indicator:
            status_indicator.config(background="#F44336")  

def on_key_press(key):
    """Handle key press events"""
    global capturing_hotkey
    
    try:

        if capturing_hotkey:

            if hasattr(key, 'char') and key.char:
                key_str = key.char
            elif hasattr(key, 'name'):
                key_str = key.name
            else:
                key_str = str(key).replace("Key.", "")

            hotkey["type"] = "keyboard"
            hotkey["keys"] = [key_str.lower()]
            hotkey["button"] = None

            if hotkey_display_var:
                hotkey_display_var.set(f"Current Hotkey: {key_str}")

            capturing_hotkey = False
            
            app_logger.log_hotkey_event("set", hotkey["keys"])
            return False

        if hotkey["type"] == "keyboard" and not clicking:

            if hasattr(key, 'char') and key.char:
                key_str = key.char
            elif hasattr(key, 'name'):
                key_str = key.name
            else:
                key_str = str(key).replace("Key.", "")

            if key_str.lower() in hotkey["keys"]:
                if click_mode == "toggle":
                    toggle_clicking()
                elif click_mode == "hold":
                    start_clicking()
                
                app_logger.log_hotkey_event("pressed", hotkey["keys"])
    
    except Exception as e:
        app_logger.error(f"Error in key press handler: {e}", exc_info=True)
    
    return True
    
def on_key_release(key):
    """Handle key release events"""
    try:
        if click_mode == "hold" and clicking and hotkey["type"] == "keyboard":
            if hasattr(key, 'char') and key.char:
                key_str = key.char
            elif hasattr(key, 'name'):
                key_str = key.name
            else:
                key_str = str(key).replace("Key.", "")

            if key_str.lower() in hotkey["keys"]:
                stop_clicking()
                app_logger.log_hotkey_event("released", hotkey["keys"])
    
    except Exception as e:
        app_logger.error(f"Error in key release handler: {e}", exc_info=True)
    
    return True

def on_mouse_click(x, y, button, pressed):
    """Handle mouse click events"""
    global capturing_hotkey
    
    try:
        if capturing_hotkey and pressed:
            hotkey["type"] = "mouse"
            hotkey["keys"] = []
            hotkey["button"] = str(button).replace("Button.", "")

            if hotkey_display_var:
                hotkey_display_var.set(f"Current Hotkey: Mouse {hotkey['button']}")

            capturing_hotkey = False
            
            app_logger.log_hotkey_event("set", [f"Mouse {hotkey['button']}"])
            return False

        if hotkey["type"] == "mouse" and not clicking:
            button_str = str(button).replace("Button.", "")
            if button_str == hotkey["button"] and pressed:
                if click_mode == "toggle":
                    toggle_clicking()
                elif click_mode == "hold":
                    start_clicking()
                
                app_logger.log_hotkey_event("pressed", [f"Mouse {hotkey['button']}"])

        if click_mode == "hold" and clicking and hotkey["type"] == "mouse":
            button_str = str(button).replace("Button.", "")
            if button_str == hotkey["button"] and not pressed:
                stop_clicking()
                app_logger.log_hotkey_event("released", [f"Mouse {hotkey['button']}"])
    
    except Exception as e:
        app_logger.error(f"Error in mouse click handler: {e}", exc_info=True)
    
    return True

def start_hotkey_capture():
    """Start capturing a new hotkey"""
    global capturing_hotkey
    
    try:
        capturing_hotkey = True
        if hotkey_display_var:
            hotkey_display_var.set("Press any key or mouse button...")
        
        app_logger.info("Hotkey capture started")
    
    except Exception as e:
        app_logger.error(f"Error starting hotkey capture: {e}", exc_info=True)

def create_ui():
    """Create the main UI"""
    global root, start_btn, stop_btn, status_indicator, cps_var, duty_var, hold_var
    global button_var, mode_var, limit_var, limit_entry, status_var, click_counter_var
    global hotkey_display_var, theme_var

    root = tk.Tk()
    root.title(f"Aerout SpeedAutoClicker v{VERSION}")
    root.geometry("500x600")
    root.minsize(500, 600)

    validate_numeric = root.register(validate_numeric_input)

    cps_var = tk.StringVar(value="10.0")
    duty_var = tk.StringVar(value=str(duty_cycle))
    hold_var = tk.StringVar(value=str(hold_time))
    button_var = tk.StringVar(value=mouse_button)
    mode_var = tk.StringVar(value=click_mode)
    limit_var = tk.BooleanVar(value=limit_enabled)
    status_var = tk.StringVar(value="Status: Stopped")
    click_counter_var = tk.StringVar(value="Clicks: 0")
    hotkey_display_var = tk.StringVar(value=f"Current Hotkey: {hotkey['keys'][0] if hotkey['type'] == 'keyboard' else 'Mouse ' + hotkey['button']}")
    theme_var = tk.StringVar(value=theme)

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    main_frame = ttk.Frame(notebook)
    notebook.add(main_frame, text="Main")

    title_frame = ttk.Frame(main_frame)
    title_frame.pack(fill=tk.X, pady=10)
    
    title_label = ttk.Label(title_frame, text="Aerout SpeedAutoClicker", font=("Helvetica", 16, "bold"))
    title_label.pack(side=tk.TOP)
    
    version_label = ttk.Label(title_frame, text=f"Version {VERSION}")
    version_label.pack(side=tk.TOP)

    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=10)
    
    status_label = ttk.Label(status_frame, textvariable=status_var)
    status_label.pack(side=tk.LEFT, padx=5)
    
    status_indicator = tk.Label(status_frame, width=3, height=1, background="#F44336")
    status_indicator.pack(side=tk.LEFT, padx=5)
    
    click_counter_label = ttk.Label(status_frame, textvariable=click_counter_var)
    click_counter_label.pack(side=tk.RIGHT, padx=5)

    cps_frame = ttk.LabelFrame(main_frame, text="Click Speed")
    cps_frame.pack(fill=tk.X, pady=10, padx=10)
    
    cps_label = ttk.Label(cps_frame, text="Clicks Per Second (CPS):")
    cps_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    cps_entry = ttk.Entry(cps_frame, textvariable=cps_var, validate="key", validatecommand=(validate_numeric, '%P'))
    cps_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    cps_var.trace_add("write", update_click_interval)
    button_frame = ttk.LabelFrame(main_frame, text="Mouse Button")
    button_frame.pack(fill=tk.X, pady=10, padx=10)
    
    left_button = ttk.Radiobutton(button_frame, text="Left", variable=button_var, value="left")
    left_button.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    right_button = ttk.Radiobutton(button_frame, text="Right", variable=button_var, value="right")
    right_button.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    
    middle_button = ttk.Radiobutton(button_frame, text="Middle", variable=button_var, value="middle")
    middle_button.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

    mode_frame = ttk.LabelFrame(main_frame, text="Click Mode")
    mode_frame.pack(fill=tk.X, pady=10, padx=10)
    
    toggle_mode = ttk.Radiobutton(mode_frame, text="Toggle (Start/Stop)", variable=mode_var, value="toggle")
    toggle_mode.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    hold_mode = ttk.Radiobutton(mode_frame, text="Hold (Press and Hold)", variable=mode_var, value="hold")
    hold_mode.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

    hotkey_frame = ttk.LabelFrame(main_frame, text="Hotkey")
    hotkey_frame.pack(fill=tk.X, pady=10, padx=10)
    
    hotkey_label = ttk.Label(hotkey_frame, textvariable=hotkey_display_var)
    hotkey_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    hotkey_button = ttk.Button(hotkey_frame, text="Set Hotkey", command=start_hotkey_capture)
    hotkey_button.grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)

    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill=tk.X, pady=20, padx=10)
    
    start_btn = ttk.Button(control_frame, text="Start (F6)", command=start_clicking)
    start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    stop_btn = ttk.Button(control_frame, text="Stop (F6)", command=stop_clicking, state="disabled")
    stop_btn.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)

    advanced_frame = ttk.Frame(notebook)
    notebook.add(advanced_frame, text="Advanced")

    duty_frame = ttk.LabelFrame(advanced_frame, text="Click Pattern")
    duty_frame.pack(fill=tk.X, pady=10, padx=10)
    
    duty_label = ttk.Label(duty_frame, text="Duty Cycle (%):")
    duty_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    duty_entry = ttk.Entry(duty_frame, textvariable=duty_var, validate="key", validatecommand=(validate_numeric, '%P'))
    duty_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    duty_var.trace_add("write", update_duty_cycle)
    
    duty_info = ttk.Label(duty_frame, text="(50% = balanced, higher = longer press)")
    duty_info.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
    
    hold_label = ttk.Label(duty_frame, text="Hold Time (ms):")
    hold_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    
    hold_entry = ttk.Entry(duty_frame, textvariable=hold_var, validate="key", validatecommand=(validate_numeric, '%P'))
    hold_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    hold_var.trace_add("write", update_hold_time)
    
    hold_info = ttk.Label(duty_frame, text="(0 = use duty cycle)")
    hold_info.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)

    limit_frame = ttk.LabelFrame(advanced_frame, text="Click Limit")
    limit_frame.pack(fill=tk.X, pady=10, padx=10)
    
    limit_check = ttk.Checkbutton(limit_frame, text="Limit Clicks", variable=limit_var, command=toggle_limit_entry)
    limit_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    limit_entry = ttk.Entry(limit_frame, validate="key", validatecommand=(validate_numeric, '%P'))
    limit_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    limit_entry.insert(0, str(click_limit))
    if not limit_enabled:
        limit_entry.config(state="disabled")

    config_frame = ttk.LabelFrame(advanced_frame, text="Configurations")
    config_frame.pack(fill=tk.X, pady=10, padx=10)
    
    config_name_label = ttk.Label(config_frame, text="Configuration Name:")
    config_name_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    config_name_entry = ttk.Entry(config_frame)
    config_name_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
    
    export_btn = ttk.Button(config_frame, text="Export", command=lambda: export_config(config_name_entry.get()))
    export_btn.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    
    import_btn = ttk.Button(config_frame, text="Import", command=lambda: import_config(config_name_entry.get()))
    import_btn.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)

    diag_frame = ttk.LabelFrame(advanced_frame, text="Diagnostic Tools")
    diag_frame.pack(fill=tk.X, pady=10, padx=10)
    
    diag_btn = ttk.Button(diag_frame, text="Create Diagnostic Report", 
                          command=lambda: messagebox.showinfo("Diagnostic Report", 
                                                             f"Report created: {app_logger.create_diagnostic_report()}"))
    diag_btn.pack(fill=tk.X, padx=5, pady=5)

    settings_frame = ttk.Frame(notebook)
    notebook.add(settings_frame, text="Settings")

    theme_frame = ttk.LabelFrame(settings_frame, text="Theme")
    theme_frame.pack(fill=tk.X, pady=10, padx=10)
    
    default_theme = ttk.Radiobutton(theme_frame, text="Default", variable=theme_var, value="default", command=apply_theme)
    default_theme.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    light_theme = ttk.Radiobutton(theme_frame, text="Light", variable=theme_var, value="light", command=apply_theme)
    light_theme.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    
    dark_theme = ttk.Radiobutton(theme_frame, text="Dark", variable=theme_var, value="dark", command=apply_theme)
    dark_theme.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
    
    custom_theme = ttk.Radiobutton(theme_frame, text="Custom", variable=theme_var, value="custom", command=apply_theme)
    custom_theme.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    
    custom_color_btn = ttk.Button(theme_frame, text="Choose Colors", command=choose_custom_color)
    custom_color_btn.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

    save_settings_btn = ttk.Button(settings_frame, text="Save Settings", command=save_current_settings)
    save_settings_btn.pack(fill=tk.X, pady=10, padx=10)

    update_frame = ttk.LabelFrame(settings_frame, text="Updates")
    update_frame.pack(fill=tk.X, pady=10, padx=10)
    
    check_update_btn = ttk.Button(update_frame, text="Check for Updates", command=lambda: check_for_updates(True))
    check_update_btn.pack(fill=tk.X, padx=5, pady=5)

    about_frame = ttk.LabelFrame(settings_frame, text="About")
    about_frame.pack(fill=tk.X, pady=10, padx=10)
    
    about_text = tk.Text(about_frame, height=8, wrap=tk.WORD)
    about_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    about_text.insert(tk.END, "Aerout SpeedAutoClicker for macOS\n\n")
    about_text.insert(tk.END, "A good autoclicker with cool features.\n\n")
    about_text.insert(tk.END, "© 2025 Aerout\n\n")
    about_text.insert(tk.END, "Join our Discord server for updates and help:\nhttps://discord.gg/shA7X2Wesr")
    about_text.config(state=tk.DISABLED)

    apply_theme()

    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    keyboard_listener.start()
    
    mouse_listener = mouse.Listener(on_click=on_mouse_click)
    mouse_listener.start()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.after(1000, lambda: check_for_updates(False))
    
    return root

def on_close():
    """Handle window close event"""
    try:
        if clicking:
            stop_clicking()

        save_settings()

        root.destroy()
        
        app_logger.info("Application closed")
    
    except Exception as e:
        app_logger.error(f"Error during application close: {e}", exc_info=True)
        root.destroy()

def main():
    """Main function"""
    try:
        load_settings()

        app = create_ui()

        app.mainloop()
    
    except Exception as e:
        app_logger.error(f"Error in main function: {e}", exc_info=True)
        messagebox.showerror("Error", f"An error occurred: {e}\n\nCheck the logs for details.")

if __name__ == "__main__":
    main()
