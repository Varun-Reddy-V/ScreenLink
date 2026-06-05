import socket
import cv2
import numpy as np

HOST = input("Enter transmitter IP: ")
PORT = 9999

client = socket.socket()

client.connect((HOST, PORT))

print("Connected!")

while True:

    size_data = client.recv(4)

    if not size_data:
        break

    size = int.from_bytes(
        size_data,
        "big"
    )

    data = b""

    while len(data) < size:

        packet = client.recv(4096)

        if not packet:
            break

        data += packet

    frame = cv2.imdecode(
        np.frombuffer(data, np.uint8),
        cv2.IMREAD_COLOR
    )

    cv2.imshow("ScreenLink", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()