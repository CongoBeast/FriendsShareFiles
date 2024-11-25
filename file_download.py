import socket
import os

def download_file(ip, port, file_name):
    # Define the directory where files are saved locally after download
    local_save_path = f"downloaded_{file_name}"
    
    # Create the socket connection to the peer
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(40)  # Set the timeout to 40 seconds
    
    try:
        # Connect to the peer's server
        client.connect((ip, port))
        client.sendall(file_name.encode())  # Request the file by name

        notification_message = f"DOWNLOADING:{file_name}"
        client.sendall(notification_message.encode())
        print(f"Notification sent to peer: {notification_message}")
        

        request_message = f"FILE_REQUEST:{file_name}"
        client.sendall(request_message.encode())  
        print(f"Sent request: {request_message}")


        # Receive the server's response
        response = client.recv(1024).decode()
        print(f"Server response: {response}")

        if response == "FILE_NOT_FOUND":
            print(f"Error: {file_name} not found on the server.")
            return
        
        total_bytes_received = 0
        
        with open(local_save_path, 'wb') as file:
            # Receive the file in chunks and write to the local file
            while data := client.recv(1024):
                if data:
                    file.write(data)
                    total_bytes_received += len(data)  # Update counter
                    print(f"Bytes received so far: {total_bytes_received}")
                else:
                    break  # No more data; break out of the loop

        # Check if the file size is zero, indicating an empty file
        if os.path.getsize(local_save_path) == 0:
            print(f"Error: {file_name} is empty. Download failed.")
            os.remove(local_save_path)  # Clean up the empty file
        else:
            print(f"File {file_name} downloaded successfully to {local_save_path}.")
    
    except Exception as e:
        print(f"Error during download: {e}")
    finally:
        client.close()

