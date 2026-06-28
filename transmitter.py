import socket
import struct
import time
import cv2
import numpy as np
from mss import MSS  # Capitalized constructor eliminates the deprecation warning

def start_transmitter(host='127.0.0.1', port=9999, fps_cap=30):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Transmitter listening on {host}:{port}...")

    frame_target_time = 1.0 / fps_cap

    try:
        while True:
            print("Waiting for ScreenLink Receiver to connect...")
            conn, addr = server_socket.accept()
            print(f"Connected securely by {addr}")
            
            with MSS() as sct:
                # Debug logging: Check what monitors your Linux display server exposes
                print(f"Detected Display System Geometries: {sct.monitors}")
                
                # On Windows, sct.monitors[0] is the virtual geometry of ALL monitors combined.
                # sct.monitors[1] is almost always the primary physical monitor.
                if len(sct.monitors) > 1:
                    monitor = sct.monitors[1]
                    print(f"Streaming primary monitor: {monitor}")
                else:
                    monitor = sct.monitors[0]
                    print(f"Streaming fallback monitor canvas: {monitor}")
                
                while True:
                    start_time = time.time()
                    
                    screen_shot = sct.grab(monitor)
                    img = np.array(screen_shot)
                    
                    if img.size == 0:
                        print("Warning: Captured an empty frame buffer. Check display server permissions.")
                        time.sleep(0.5)
                        continue
                        
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    result, encoded_img = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    if not result:
                        continue
                        
                    jpeg_bytes = encoded_img.tobytes()
                    header = struct.pack('!I', len(jpeg_bytes))
                    
                    try:
                        conn.sendall(header + jpeg_bytes)
                    except (ConnectionResetError, BrokenPipeError):
                        print("Receiver disconnected.")
                        break
                    
                    elapsed = time.time() - start_time
                    sleep_time = frame_target_time - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)
            conn.close()
    except KeyboardInterrupt:
        print("\nShutting down transmitter module safely.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_transmitter()