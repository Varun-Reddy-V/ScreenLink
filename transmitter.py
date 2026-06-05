import socket
import struct
import subprocess
import time
import cv2
import numpy as np

HOST = "0.0.0.0"
PORT = 9999


def capture_screen():
    # Take screenshot using grim
    subprocess.run(["grim", "screenshot.png"], check=True)

    # Load image into OpenCV
    frame = cv2.imread("screenshot.png")

    return frame


def compress_frame(frame):
    # Convert image to JPEG
    success, encoded = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, 70]
    )

    if not success:
        raise Exception("JPEG compression failed")

    return encoded.tobytes()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST, PORT))
    server.listen(1)

    print(f"Listening on {HOST}:{PORT}")

    client_socket, client_address = server.accept()

    print(f"Connected: {client_address}")
    while True:
        frame = capture_screen()

        print("Screenshot captured")

        jpeg_data = compress_frame(frame)

        print(f"Compressed size: {len(jpeg_data)} bytes")

        # Pack frame size into 4 bytes
        header = struct.pack(">I", len(jpeg_data))

        client_socket.sendall(header)
        client_socket.sendall(jpeg_data)

        print("Frame sent")
        time.sleep(3)

    client_socket.close()
    server.close()


if __name__ == "__main__":
    main()