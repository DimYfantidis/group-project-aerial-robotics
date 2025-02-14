import socket
import os
import cv2
import time
from picamera2 import Picamera2

# Configuration
HOST = "0.0.0.0"
PORT = 5000
SAVE_DIR = "manual-captures"

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize camera
picam2 = Picamera2()
picam2.start()

# Start server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server listening on {HOST}:{PORT}...")

while True:
    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break

        if data.lower() == "c":
            # Capture and save image
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"{SAVE_DIR}/image_{timestamp}.png"
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(filename, frame)

            print(f"Image saved: {filename}")
            conn.sendall(b"Image captured successfully\n")
        elif data.lower() == "exit":
            print("Closing connection.")
            break

    conn.close()