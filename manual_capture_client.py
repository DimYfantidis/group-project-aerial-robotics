import socket

# Configuration
RASPBERRY_PI_IP = "192.168.45.151"  # Change this to Pi's IP address
PORT = 5000

# Connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((RASPBERRY_PI_IP, PORT))
print(f"Connected to Raspberry Pi at {RASPBERRY_PI_IP}:{PORT}")

while True:
    command = input("Enter command (c:capture/e:exit): ").strip().lower()

    if command in ["c", "e"]:
        client_socket.sendall(command.encode())

        response = client_socket.recv(1024).decode()
        print("Response:", response)

        if command == "e":
            break
    else:
        print("Invalid command. Use 'c:capture' or 'e:exit'.")

client_socket.close()
print("Connection closed.")
