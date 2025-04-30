import os
import json

class Settings:
    def __init__(self):
        self.settings_path = os.path.expanduser("~/.aeroutclicker.json")
        self.defaults = {
            "click_interval_ms": 100.0,  
            "duty_cycle": 50.0,          
            "click_mode": "toggle",      
            "mouse_button": "left",      
            "hotkey": {
                "keys": [],
                "display": "None"
            },
            "click_limit": {
                "enabled": False,
                "count": 100
            }
        }
        self.current = self.load()
    
    def load(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    user_settings = json.load(f)

                    settings = self.defaults.copy()
                    settings.update(user_settings)
                    return settings
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.defaults.copy()
        return self.defaults.copy()
    
    def save(self):
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.current, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        return self.current.get(key, default)
    
    def set(self, key, value):
        self.current[key] = value
        self.save()


