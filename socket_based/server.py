import socket

print("Starting script")

# Instantiate the socket
server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server_socket.bind(("04:EA:56:B7:28:E7", 4)) # Unique MAC address assigned to this device
server_socket.listen(1)

client, address = server_socket.accept()

print("Listening for messages...")

try:
    while True:
        msg = client.recv(1024) # Recieve 1024 bytes

        if not msg:
            break

        print(f"Message Received: {msg.decode('utf-8')}")
except OSError:
    pass # For now, suppress eat the exception

# Cleanup
client.close()
server_socket.close()