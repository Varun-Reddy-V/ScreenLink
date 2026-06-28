import socket
import struct
import numpy as np
import cv2
import time
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from utils.image_converter import ImageConverter

class ReceiverWorker(QThread):
    # Signals to communicate safely with the Main UI Thread
    frame_received = pyqtSignal(QImage)
    fps_updated = pyqtSignal(int)
    status_changed = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False

    def run(self):
        self.running = True
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.status_changed.emit(f"Connecting to {self.host}:{self.port}...")
            client_socket.connect((self.host, self.port))
            self.status_changed.emit("Connected!")
        except Exception as e:
            self.status_changed.emit(f"Connection failed: {str(e)}")
            self.connection_lost.emit()
            return

        # Setup variables for FPS tracking
        frame_count = 0
        last_fps_time = time.time()
        
        # Helper function to reliably pull 'n' bytes from stream
        def recv_all(sock, n):
            data = bytearray()
            while len(data) < n:
                packet = sock.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            return data

        while self.running:
            try:
                # 1. Read the 4-byte header (frame size)
                header = recv_all(client_socket, 4)
                if not header:
                    break
                
                # Unpack network byte order integer ('!I')
                frame_size = struct.unpack('!I', header)[0]
                
                # 2. Read the actual JPEG payload
                jpeg_data = recv_all(client_socket, frame_size)
                if not jpeg_data:
                    break
                
                # 3. Decode JPEG buffer to NumPy array
                np_arr = np.frombuffer(jpeg_data, dtype=np.uint8)
                cv_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if cv_img is not None:
                    # 4. Convert and dispatch to UI Thread
                    q_img = ImageConverter.bgr_to_qimage(cv_img)
                    self.frame_received.emit(q_img)
                    
                    # Track FPS
                    frame_count += 1
                    now = time.time()
                    if now - last_fps_time >= 1.0:
                        self.fps_updated.emit(frame_count)
                        frame_count = 0
                        last_fps_time = now

            except Exception as e:
                print(f"Stream error: {e}")
                break

        # Clean up
        client_socket.close()
        self.status_changed.emit("Disconnected")
        self.connection_lost.emit()

    def stop(self):
        self.running = False
        self.wait() # Ensure the thread exits cleanly before returning