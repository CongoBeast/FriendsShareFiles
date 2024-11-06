import socket
import threading
import os

HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5001       # Replace with an available port

# Start a thread to handle each incoming file request
def handle_client(conn, addr):
    print(f"Connection from {addr} established.")
    file_name = conn.recv(1024).decode()  # Get the file name
    file_path = os.path.join("shared", file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            while chunk := file.read(1024):
                conn.sendall(chunk)
    else:
        conn.sendall(b"ERROR: File not found.")

    print(f"File {file_name} sent to {addr}.")
    conn.close()

# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Server started, waiting for connections..." , flush=True)
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

start_server()
