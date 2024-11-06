import socket

def download_file(ip, port, file_name):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))

    client.sendall(file_name.encode())  # Request file by name

    with open(f"downloaded_{file_name}", 'wb') as file:
        while data := client.recv(1024):
            file.write(data)

    print(f"File {file_name} downloaded successfully.")
    client.close()
