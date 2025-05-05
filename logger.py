#!/usr/bin/env python3
"""
Logger module for Aerout SpeedAutoClicker
Handles logging of clicker events and click data
"""

import os
import sys
import logging
import json
import time
import platform
import shutil
import traceback
from datetime import datetime

LOG_DIR = os.path.expanduser("~/Documents/AeroutClicker/logs")
CLICK_LOG_FILE = os.path.join(LOG_DIR, "clicks.log")
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")
DIAG_DIR = os.path.expanduser("~/Documents/AeroutClicker/diagnostics")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DIAG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(APP_LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

class ClickLogger:
    """Logger for click events and application activity"""
    
    def __init__(self):
        """Initialize the logger"""
        self.logger = logging.getLogger('aerout_clicker')
        self.click_count = 0

        self.click_logger = logging.getLogger('click_logger')
        self.click_logger.setLevel(logging.INFO)
        
        click_handler = logging.FileHandler(CLICK_LOG_FILE)
        click_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.click_logger.addHandler(click_handler)

        self.info(f"Application started - Version: {self._get_version()}")
        self.info(f"System: {platform.system()} {platform.release()} ({platform.version()})")
        self.info(f"Python: {platform.python_version()}")
    
    def _get_version(self):
        """Get the application version"""
        try:
            with open(os.path.join(os.path.dirname(__file__), "version.txt"), "r") as f:
                return f.read().strip()
        except:
            return "Unknown"
    
    def info(self, message):
        """Log an info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a warning message"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """Log an error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def log_click_event(self, event_type, button, x, y):
        """Log a click event"""
        self.click_count += 1
        self.click_logger.info(f"{event_type},{button},{x},{y}")
    
    def log_hotkey_event(self, event_type, keys):
        """Log a hotkey event"""
        key_str = "+".join(keys)
        self.logger.info(f"Hotkey {event_type}: {key_str}")
    
    def create_diagnostic_report(self):
        """Create a diagnostic report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = os.path.join(DIAG_DIR, f"report_{timestamp}")
            os.makedirs(report_dir, exist_ok=True)

            shutil.copy2(APP_LOG_FILE, os.path.join(report_dir, "app.log"))
            shutil.copy2(CLICK_LOG_FILE, os.path.join(report_dir, "clicks.log"))

            system_info = {
                "os": platform.system(),
                "os_version": platform.release(),
                "os_build": platform.version(),
                "python_version": platform.python_version(),
                "processor": platform.processor(),
                "machine": platform.machine(),
                "timestamp": timestamp,
                "app_version": self._get_version(),
                "click_count": self.click_count
            }

            with open(os.path.join(report_dir, "system_info.json"), "w") as f:
                json.dump(system_info, f, indent=4)

            zip_file = os.path.join(DIAG_DIR, f"aerout_diagnostic_{timestamp}.zip")
            shutil.make_archive(zip_file.replace(".zip", ""), 'zip', report_dir)

            shutil.rmtree(report_dir)
            
            self.info(f"Diagnostic report created: {zip_file}")
            return zip_file
        
        except Exception as e:
            self.error(f"Error creating diagnostic report: {e}", exc_info=True)
            return None

app_logger = ClickLogger()
