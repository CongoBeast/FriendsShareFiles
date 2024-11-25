# import socket
# import threading
# import os

# HOST = '192.168.137.135'  # Listen on all network interfaces
# PORT = 5001       # Replace with an available port

# # Start a thread to handle each incoming file request
# def handle_client(conn, addr):
#     print(f"Connection from {addr} established.")
#     file_name = conn.recv(1024).decode()  # Get the file name
#     file_path = os.path.join("shared", file_name)

#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as file:
#             while chunk := file.read(1024):
#                 conn.sendall(chunk)
#     else:
#         conn.sendall(b"ERROR: File not found.")

#     print(f"File {file_name} sent to {addr}.")
#     conn.close()

# def handle_metadata_request(conn, addr):
#     with open("metadata.json", "r") as f:
#         metadata = f.read()
#     conn.sendall(metadata.encode())
#     conn.close()

# # Start the server
# def start_server():
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((HOST, PORT))
#     server.listen()

#     print("Server started, waiting for connections..." , flush=True)
#     while True:
#         conn, addr = server.accept()
#         threading.Thread(target=handle_client, args=(conn, addr)).start()

# start_server()
import socket
import threading
import json
import os

# Load or create metadata
def load_metadata():
    if not os.path.exists("metadata.json"):
        with open("metadata.json", "w") as f:
            json.dump({"files": []}, f)
    with open("metadata.json", "r") as f:
        return json.load(f)

# Save metadata
def save_metadata(metadata):
    with open("metadata.json", "w") as f:
        json.dump(metadata, f)

# Merge client metadata with server metadata
def merge_metadata(server_metadata, client_metadata):
    existing_files = {file["file_name"]: file for file in server_metadata["files"]}
    
    for file in client_metadata["files"]:
        if file["file_name"] in existing_files:
            # Update existing file's download count or other data
            existing_files[file["file_name"]]["download_count"] = max(
                existing_files[file["file_name"]]["download_count"],
                file["download_count"]
            )
        else:
            # Add new file to the metadata
            server_metadata["files"].append(file)

    return server_metadata

# Handle client requests
def handle_client(client_socket):
    try:

        message = client_socket.recv(1024).decode().strip()
        print(f"Received request: {message}")
        
        request = client_socket.recv(1024 * 10).decode()
        server_metadata = load_metadata()

        if request == "METADATA_REQUEST":
            client_socket.send(json.dumps(server_metadata).encode())
        else:
            # Client sent its metadata for synchronization
            client_metadata = json.loads(request)
            updated_metadata = merge_metadata(server_metadata, client_metadata)
            save_metadata(updated_metadata)
            client_socket.send(b"Metadata updated successfully")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

# Start the server
def start_server():
    server_ip = "192.168.137.135"  # Change if needed
    server_port = 5001
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)
    print(f"Server listening on {server_ip}:{server_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection received from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
