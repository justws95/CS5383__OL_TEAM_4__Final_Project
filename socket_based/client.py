import socket

# Instantiate the socket
client_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
client_socket.connect(("04:EA:56:B7:28:E7", 4)) # Unique MAC address assigned to this device

try:
    while True:
        msg = input("Enter your message: ")
        client_socket.send(msg.encode('utf-8'))
        response = client_socket.recv(1024)

        if not response:
            break
        
        print(f"Message: {response.decode('utf-8')}")
except OSError:
    pass # For now, suppress eat the exception

# Cleanup
client_socket.close()