import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QComboBox, 
                            QDoubleSpinBox, QCheckBox, QSystemTrayIcon, 
                            QMenu, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
from hotkeys import HotkeyManager
from clicker import AutoClicker
from updater import check_for_updates
from version import __version__

class SpeedAutoClicker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Speed Auto Clicker (Mac) v{__version__}")
        self.setWindowIcon(QIcon(os.path.join('assets', 'icon.icns')))
        self.setFixedSize(400, 300)
        
        # Initialize auto clicker
        self.clicker = AutoClicker()
        self.hotkey_manager = HotkeyManager(self)
        
        # System tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join('assets', 'icon.icns')))
        
        self.init_ui()
        self.init_tray()
        
        # Check for updates on startup
        QTimer.singleShot(1000, self.check_updates)
    
    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # CPS Control
        cps_layout = QHBoxLayout()
        cps_layout.addWidget(QLabel("Clicks Per Second:"))
        self.cps_spin = QDoubleSpinBox()
        self.cps_spin.setRange(0.01, 100.0)
        self.cps_spin.setValue(10.0)
        self.cps_spin.setSingleStep(0.1)
        self.cps_spin.setDecimals(2)
        cps_layout.addWidget(self.cps_spin)
        layout.addLayout(cps_layout)
        
        # Duty Cycle
        duty_layout = QHBoxLayout()
        duty_layout.addWidget(QLabel("Click Duty Cycle (%):"))
        self.duty_spin = QDoubleSpinBox()
        self.duty_spin.setRange(1.0, 99.0)
        self.duty_spin.setValue(50.0)
        self.duty_spin.setSingleStep(0.1)
        self.duty_spin.setDecimals(2)
        duty_layout.addWidget(self.duty_spin)
        layout.addLayout(duty_layout)
        
        # Hotkey Selection
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("Start/Stop Hotkey:"))
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems([
            "F6", "F7", "F8", "F9", "F10",
            "Shift+F6", "Shift+F7", "Shift+F8",
            "Ctrl+F6", "Ctrl+F7", "Ctrl+F8",
            "Alt+F6", "Alt+F7", "Alt+F8"
        ])
        hotkey_layout.addWidget(self.hotkey_combo)
        layout.addLayout(hotkey_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start (F6)")
        self.start_btn.clicked.connect(self.toggle_clicker)
        btn_layout.addWidget(self.start_btn)
        
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings)
        btn_layout.addWidget(settings_btn)
        layout.addLayout(btn_layout)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
        # Set initial hotkey
        self.hotkey_manager.register_hotkey("F6", self.toggle_clicker)
    
    def init_tray(self):
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def toggle_clicker(self):
        if self.clicker.is_clicking:
            self.clicker.stop()
            self.start_btn.setText("Start (F6)")
        else:
            cps = self.cps_spin.value()
            duty_cycle = self.duty_spin.value() / 100.0
            self.clicker.start(cps, duty_cycle)
            self.start_btn.setText("Stop (F6)")
    
    def check_updates(self):
        update_available = check_for_updates(__version__)
        if update_available:
            reply = QMessageBox.question(
                self, 'Update Available',
                'A new version is available. Would you like to update now?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.update_application()
    
    def update_application(self):
        # This would be handled by the updater.py
        pass
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Speed Auto Clicker",
            "The application is still running in the background.",
            QSystemTrayIcon.Information, 2000
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ensure single instance
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    
    window = SpeedAutoClicker()
    window.show()
    sys.exit(app.exec_())
