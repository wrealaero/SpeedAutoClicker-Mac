import sys
import pynput
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QDoubleSpinBox, QPushButton, QCheckBox
from pynput.mouse import Controller, Button
from pynput import keyboard
import threading
import time

class AutoClicker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mouse = Controller()
        self.setWindowTitle("Speed AutoClicker")
        self.setFixedSize(300, 200)
        
        # CPS Control
        self.cps_spin = QDoubleSpinBox()
        self.cps_spin.setRange(1, 100)
        self.cps_spin.setValue(10.0)
        self.cps_spin.setSingleStep(0.1)
        
        # Start/Stop Button
        self.toggle_btn = QPushButton("Start (F6)")
        self.toggle_btn.clicked.connect(self.toggle)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Clicks Per Second:"))
        layout.addWidget(self.cps_spin)
        layout.addWidget(self.toggle_btn)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Hotkey
        self.listener = keyboard.GlobalHotKeys({'<f6>': self.toggle})
        self.listener.start()
        
        self.clicking = False
    
    def toggle(self):
        self.clicking = not self.clicking
        if self.clicking:
            self.toggle_btn.setText("Stop (F6)")
            threading.Thread(target=self.click_loop, daemon=True).start()
        else:
            self.toggle_btn.setText("Start (F6)")
    
    def click_loop(self):
        delay = 1 / self.cps_spin.value()
        while self.clicking:
            self.mouse.click(Button.left)
            time.sleep(delay)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoClicker()
    window.show()
    sys.exit(app.exec_())
