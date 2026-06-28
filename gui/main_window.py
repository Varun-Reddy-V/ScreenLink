import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QStatusBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from workers.receiver_worker import ReceiverWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScreenLink Receiver (v1.0)")
        self.setMinimumSize(800, 600)
        self.is_connected = False
        self.worker = None
        
        self.init_ui()
        
    def init_ui(self):
        # Main Layout container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Control Panel (Top Bar)
        control_layout = QHBoxLayout()
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Transmitter IP (e.g., 192.168.1.5)")
        self.ip_input.setText("127.0.0.1")  # Default local loopback for testing
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")
        self.port_input.setText("9999")
        self.port_input.setFixedWidth(80)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        control_layout.addWidget(QLabel("Host:"))
        control_layout.addWidget(self.ip_input)
        control_layout.addWidget(QLabel("Port:"))
        control_layout.addWidget(self.port_input)
        control_layout.addWidget(self.connect_btn)
        
        main_layout.addLayout(control_layout)
        
        # Video Display Area
        self.video_label = QLabel("Not Connected")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: #1e1e1e; color: #888888; font-size: 16px;")
        self.video_label.setScaledContents(False) 
        main_layout.addWidget(self.video_label, stretch=1)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected | FPS: 0")

    def toggle_connection(self):
        if not self.is_connected:
            host = self.ip_input.text()
            try:
                port = int(self.port_input.text())
            except ValueError:
                self.status_bar.showMessage("Invalid Port Number")
                return

            # Instantiate worker thread
            self.worker = ReceiverWorker(host, port)
            
            # Connect Signals to UI update Slots
            self.worker.frame_received.connect(self.update_frame)
            self.worker.fps_updated.connect(self.update_fps)
            self.worker.status_changed.connect(self.update_status)
            self.worker.connection_lost.connect(self.handle_disconnect)
            
            self.worker.start()
            self.connect_btn.setText("Disconnect")
            self.is_connected = True
        else:
            self.handle_disconnect()

    def handle_disconnect(self):
        if self.is_connected:
            if self.worker and self.worker.isRunning():
                self.worker.stop()
            self.connect_btn.setText("Connect")
            self.video_label.setText("Not Connected")
            self.video_label.setPixmap(QPixmap())  # Clear last frame
            self.status_bar.showMessage("Disconnected | FPS: 0")
            self.is_connected = False

    def update_frame(self, q_img):
        if not self.is_connected or q_img.isNull():
            return
            
        pixmap = QPixmap.fromImage(q_img)
        
        # Guard against zero-width canvas scales before layout loads
        target_size = self.video_label.size()
        if target_size.width() < 50 or target_size.height() < 50:
            target_size = self.size() # Fall back to overall main window dimensions
            
        scaled_pixmap = pixmap.scaled(
            target_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def update_status(self, message):
        self.status_bar.showMessage(message)

    def update_fps(self, fps):
        current_status = self.status_bar.currentMessage().split(" | ")[0]
        self.status_bar.showMessage(f"{current_status} | FPS: {fps}")

    # Ensure thread cleans up safely if window is closed directly
    def closeEvent(self, event):
        if self.is_connected and self.worker:
            self.worker.stop()
        event.accept()