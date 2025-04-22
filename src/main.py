import sys
import time
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from pynput.mouse import Controller, Button
from pynput import keyboard

class AutoClicker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mouse = Controller()
        self.setWindowTitle("Speed AutoClicker")
        self.setFixedSize(400, 300)
        
        # CPS Control (supports decimals)
        self.cps_spin = QDoubleSpinBox()
        self.cps_spin.setRange(0.1, 100.0)
        self.cps_spin.setValue(10.0)
        self.cps_spin.setSingleStep(0.1)
        self.cps_spin.setDecimals(2)
        
        # Duty Cycle (1-99%)
        self.duty_spin = QDoubleSpinBox()
        self.duty_spin.setRange(1.0, 99.0)
        self.duty_spin.setValue(50.0)
        self.duty_spin.setSingleStep(0.1)
        self.duty_spin.setDecimals(2)
        
        # Hotkey Selection
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems([
            "F6", "F7", "F8", 
            "Shift+F6", "Ctrl+F6", "Alt+F6",
            "Shift+Q", "Ctrl+Q"
        ])
        
        # Start/Stop Button
        self.toggle_btn = QPushButton("Start (F6)")
        self.toggle_btn.clicked.connect(self.toggle)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Clicks Per Second (0.1-100.0):"))
        layout.addWidget(self.cps_spin)
        layout.addWidget(QLabel("Duty Cycle % (1.0-99.0):"))
        layout.addWidget(self.duty_spin)
        layout.addWidget(QLabel("Hotkey:"))
        layout.addWidget(self.hotkey_combo)
        layout.addWidget(self.toggle_btn)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Clicking control
        self.clicking = False
        self.current_hotkey = "<f6>"
        self.listener = keyboard.GlobalHotKeys({
            self.current_hotkey: self.toggle
        })
        self.listener.start()
    
    def toggle(self):
        self.clicking = not self.clicking
        if self.clicking:
            self.toggle_btn.setText("Stop")
            threading.Thread(target=self.click_loop, daemon=True).start()
        else:
            self.toggle_btn.setText("Start")
    
    def click_loop(self):
        cps = self.cps_spin.value()
        duty = self.duty_spin.value() / 100
        click_duration = duty / cps
        between_clicks = (1 - duty) / cps
        
        while self.clicking:
            self.mouse.press(Button.left)
            time.sleep(click_duration)
            self.mouse.release(Button.left)
            time.sleep(between_clicks)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoClicker()
    window.show()
    sys.exit(app.exec_())
