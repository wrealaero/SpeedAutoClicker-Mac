from pynput import keyboard

class HotkeyManager:
    def __init__(self, parent):
        self.parent = parent
        self.listener = None
        self.current_hotkey = None
        self.current_callback = None
        
    def register_hotkey(self, hotkey_str, callback):
        self.unregister_hotkey()
        self.current_hotkey = self.parse_hotkey(hotkey_str)
        self.current_callback = callback
        self.listener = keyboard.GlobalHotKeys({
            self.current_hotkey: self.on_hotkey
        })
        self.listener.start()
    
    def unregister_hotkey(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def parse_hotkey(self, hotkey_str):
        # Convert "Shift+F6" to "<shift>+f6" format
        parts = hotkey_str.split('+')
        parsed = []
        for part in parts:
            part = part.lower()
            if part in ['ctrl', 'control']:
                parsed.append('<ctrl>')
            elif part == 'alt':
                parsed.append('<alt>')
            elif part == 'shift':
                parsed.append('<shift>')
            elif part.startswith('f'):
                parsed.append(part)
            else:
                parsed.append(part)
        return '+'.join(parsed)
    
    def on_hotkey(self):
        if self.current_callback:
            self.current_callback()
