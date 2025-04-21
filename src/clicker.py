import time
import threading
from pynput.mouse import Controller, Button
from pynput import keyboard

class AutoClicker:
    def __init__(self):
        self.mouse = Controller()
        self.is_clicking = False
        self.click_thread = None
        
    def start(self, cps, duty_cycle):
        if self.is_clicking:
            return
            
        self.is_clicking = True
        click_interval = 1.0 / cps
        press_duration = click_interval * duty_cycle
        
        def click_loop():
            while self.is_clicking:
                start_time = time.time()
                self.mouse.press(Button.left)
                time.sleep(press_duration)
                self.mouse.release(Button.left)
                elapsed = time.time() - start_time
                remaining = click_interval - elapsed
                if remaining > 0:
                    time.sleep(remaining)
        
        self.click_thread = threading.Thread(target=click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()
    
    def stop(self):
        self.is_clicking = False
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join()
