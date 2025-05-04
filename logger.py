#!/usr/bin/env python3
"""
Logging system for Aerout SpeedAutoClicker
Main Handler for my application logging, click events, and reports
"""

import os
import sys
import time
import json
import logging
import platform
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

class AutoClickerLogger:
    """Logging system for the autoclicker application"""
    
    def __init__(self):
        """Initialize the logger"""
        self.log_dir = os.path.expanduser("~/Documents/AeroutClicker/logs")
        os.makedirs(self.log_dir, exist_ok=True)

        self.logger = logging.getLogger("autoclicker")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        main_log_path = os.path.join(self.log_dir, "autoclicker.log")
        file_handler = RotatingFileHandler(
            main_log_path, 
            maxBytes=5*1024*1024, 
            backupCount=3
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.click_logger = logging.getLogger("click_events")
        self.click_logger.setLevel(logging.DEBUG)

        click_log_path = os.path.join(self.log_dir, "clicks.log")
        click_handler = RotatingFileHandler(
            click_log_path,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=2
        )
        click_handler.setFormatter(formatter)
        self.click_logger.addHandler(click_handler)

        self.session_start = datetime.now()
        self.session_id = int(time.time())
        self.click_count = 0
        self.session_data = {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "system_info": self.get_system_info(),
            "events": []
        }

        self.info(f"Session started: {self.session_id}")
    
    def get_system_info(self):
        """Get system information for diagnostics"""
        try:
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "processor": platform.processor(),
                "machine": platform.machine(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version()
            }
        except Exception as e:
            self.error(f"Error getting system info: {e}")
            return {"error": str(e)}

    def debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log an info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a warning message"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """Log an error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=False):
        """Log a critical message"""
        self.logger.critical(message, exc_info=exc_info)

    def log_click_event(self, action, button, x, y):
        """Log a mouse click event"""
        try:
            self.click_count += 1
            if self.click_count % 10 == 0:
                event_data = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "click",
                    "action": action,
                    "button": button,
                    "position": {"x": x, "y": y},
                    "count": self.click_count
                }

                self.click_logger.debug(
                    f"Click {action}: button={button}, pos=({x},{y}), count={self.click_count}"
                )

                self.session_data["events"].append(event_data)
        except Exception as e:
            self.error(f"Error logging click event: {e}")
    
    def log_hotkey_event(self, action, keys=None):
        """Log a hotkey event"""
        try:
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "type": "hotkey",
                "action": action,
                "keys": keys or []
            }

            self.logger.debug(f"Hotkey {action}: keys={'+'.join(keys) if keys else 'None'}")

            self.session_data["events"].append(event_data)
        except Exception as e:
            self.error(f"Error logging hotkey event: {e}")
    
    def log_setting_change(self, setting, previous, new=None):
        """Log a setting change"""
        try:
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "type": "setting",
                "setting": setting,
                "previous": previous,
                "new": new
            }

            self.logger.debug(f"Setting changed: {setting} = {new}")

            self.session_data["events"].append(event_data)
        except Exception as e:
            self.error(f"Error logging setting change: {e}")
    
    def log_ui_action(self, action, details=None):
        """Log a UI action"""
        try:
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "type": "ui_action",
                "action": action,
                "details": details
            }

            self.logger.debug(f"UI action: {action} {details or ''}")

            self.session_data["events"].append(event_data)
        except Exception as e:
            self.error(f"Error logging UI action: {e}")
    
    def create_diagnostic_report(self):
        """Create a diagnostic report for troubleshooting"""
        try:
            self.session_data["end_time"] = datetime.now().isoformat()
            self.session_data["duration"] = (
                datetime.now() - self.session_start
            ).total_seconds()

            report_filename = f"diagnostic_report_{self.session_id}.json"
            report_path = os.path.join(self.log_dir, report_filename)

            with open(report_path, 'w') as f:
                json.dump(self.session_data, f, indent=2)
            
            self.info(f"Diagnostic report created: {report_path}")
            return report_path
        
        except Exception as e:
            self.error(f"Error creating diagnostic report: {e}", exc_info=True)
            return None
    
    def log_exception(self, exc_type, exc_value, exc_traceback):
        """Log an uncaught exception"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

app_logger = AutoClickerLogger()

sys.excepthook = app_logger.log_exception
