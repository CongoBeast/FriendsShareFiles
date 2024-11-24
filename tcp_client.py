import tkinter as tk
from tkinter import simpledialog, filedialog
import json
import os
import socket
from datetime import datetime
from file_download import *

# Load or create metadata for available files
def load_metadata():
    if not os.path.exists("metadata.json"):
        with open("metadata.json", "w") as f:
            json.dump({"files": []}, f)
    
    with open("metadata.json", "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"files": []}

# Save metadata
def save_metadata(metadata):
    with open("metadata.json", "w") as f:
        json.dump(metadata, f)

# Merge server metadata with local metadata
def merge_metadata(local_metadata, server_metadata):
    existing_files = {file["file_name"]: file for file in local_metadata["files"]}
    
    for file in server_metadata["files"]:
        if file["file_name"] in existing_files:
            # Update download count or other fields
            existing_files[file["file_name"]]["download_count"] = max(
                existing_files[file["file_name"]]["download_count"],
                file["download_count"]
            )
        else:
            # Add new file to the metadata
            local_metadata["files"].append(file)

    return local_metadata

# Request metadata from the server
def request_metadata(server_ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, port))
            s.sendall(b"METADATA_REQUEST")
            metadata = s.recv(1024 * 10)  # Adjust buffer size if needed
            return json.loads(metadata.decode())
    except Exception as e:
        print(f"Error requesting metadata: {e}")
        return {"files": []}
    

# Prompt for username if not already saved
def get_username():
    if not os.path.exists("user_info.json"):
        username = simpledialog.askstring("Enter Username", "Please enter your username:")
        with open("user_info.json", "w") as f:
            json.dump({"username": username}, f)
    else:
        with open("user_info.json", "r") as f:
            user_data = json.load(f)
            username = user_data.get("username", "User")
    return username

# Upload file to shared folder and update metadata
def upload_file():
    file_path = filedialog.askopenfilename()
    PORT = 5001

    if file_path:
        file_name = os.path.basename(file_path)
        destination = os.path.join("shared", file_name)
        os.makedirs("shared", exist_ok=True)
        os.rename(file_path, destination)
        
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update metadata
        with open("metadata.json", "r+") as f:
            data = json.load(f)
            data["files"].append({
                "file_name": file_name, 
                "ip": "localhost", 
                "port": PORT,
                "username": username,
                "upload_time": upload_time,
                "download_count": 0
            })
            f.seek(0)
            json.dump(data, f)
        
        refresh_file_list()
        print(f"File {file_name} uploaded and available for sharing.")
        
        # Notify server of updated metadata
        notify_server_metadata("192.168.137.135", 5001 , data)

# Notify server of updated metadata
# def notify_server_metadata():
#     server_ip = "192.168.137.135"  # Replace with actual server IP
#     server_port = 5001      # Replace with actual server port
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.connect((server_ip, server_port))
#             with open("metadata.json", "r") as f:
#                 metadata = f.read()
#             s.sendall(metadata.encode())
#             print("Metadata successfully sent to the server.")
#     except Exception as e:
#         print(f"Failed to notify server: {e}")

# Download selected file
def download_selected_file():
    selection = file_listbox.curselection()
    if not selection:
        print("No file selected. Please select a file to download.")
        return

    selected_file = file_listbox.get(selection).split(" | ")[0]
    metadata = load_metadata()

    for file_info in metadata["files"]:
        if file_info["file_name"] == selected_file:
            download_file(file_info["ip"], file_info["port"], file_info["file_name"])
            
            # Update download count
            file_info["download_count"] += 1
            with open("metadata.json", "w") as f:
                json.dump(metadata, f)
            
            refresh_file_list()
            break

# Send updated metadata to the server
def notify_server_metadata(server_ip, port, metadata):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, port))
            s.sendall(json.dumps(metadata).encode())
            response = s.recv(1024).decode()
            print(response)
    except Exception as e:
        print(f"Error notifying server: {e}")

# Refresh the file list with updated metadata
def refresh_file_list():
    file_listbox.delete(0, tk.END)
    metadata = load_metadata()
    
    for file_info in metadata["files"]:
        file_display = (f"{file_info['file_name']} | Uploaded by: {file_info['username']} | "
                        f"Time: {file_info['upload_time']} | Downloads: {file_info['download_count']}")
        file_listbox.insert(tk.END, file_display)

# Request latest metadata from the server
# def request_metadata(server_ip, port):
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.connect((server_ip, port))
#             s.sendall(b"METADATA_REQUEST")
            
#             metadata = s.recv(1024*10)  # Adjust buffer size if needed
#             with open("metadata.json", "w") as f:
#                 f.write(metadata.decode())
        
#         refresh_file_list()
#         display_temporary_message("Metadata refreshed successfully!", "green")
#     except Exception as e:
#         print(f"Failed to refresh metadata: {e}")
#         display_temporary_message("Failed to refresh metadata!", "red")

def refresh_metadata():
    server_ip = "127.0.0.1"
    port = 5002

    # Request metadata from server
    server_metadata = request_metadata(server_ip, port)
    local_metadata = load_metadata()

    # Merge metadata
    updated_metadata = merge_metadata(local_metadata, server_metadata)
    save_metadata(updated_metadata)

    # Notify server about the updated metadata
    notify_server_metadata(server_ip, port, updated_metadata)

    # Refresh file list and show confirmation
    refresh_file_list()
    show_temp_message("Metadata refreshed successfully!", root)

def show_temp_message(message, parent):
    label = tk.Label(parent, text=message, fg="green", font=("Helvetica", 10, "italic"))
    label.pack()
    parent.after(3000, label.destroy)  # Remove the message after 3 seconds


# Display a temporary message
def display_temporary_message(message, color):
    message_label.config(text=message, fg=color)
    message_label.pack()
    root.after(3000, lambda: message_label.pack_forget())

# Set up the GUI
root = tk.Tk()
root.title("P2P File Sharing System")
root.geometry("500x500")  # Larger window size

# Username entry
username = get_username()
username_label = tk.Label(root, text=f"Welcome, {username}!", font=("Helvetica", 12, "bold"))
username_label.pack(pady=5)

# Filename list label
list_label = tk.Label(root, text="Filename List:", font=("Helvetica", 10, "italic"))
list_label.pack()

file_listbox = tk.Listbox(root)
file_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

# Temporary message label
message_label = tk.Label(root, font=("Helvetica", 10))

# Buttons arranged side-by-side
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

upload_button = tk.Button(button_frame, text="Upload File", command=upload_file, bg="green", fg="white", font=("Helvetica", 10))
upload_button.grid(row=0, column=0, padx=5)

download_button = tk.Button(button_frame, text="Download File", command=download_selected_file, bg="blue", fg="white", font=("Helvetica", 10))
download_button.grid(row=0, column=1, padx=5)

# refresh_button = tk.Button(button_frame, text="Refresh Metadata", 
#                            command=lambda: request_metadata("192.168.137.135", 5001), 
#                            bg="orange", fg="white", font=("Helvetica", 10))
# refresh_button.grid(row=0, column=2, padx=5)

refresh_button = tk.Button(button_frame, text="Refresh", command=refresh_metadata, bg="orange", fg="white", font=("Helvetica", 10))
refresh_button.grid(row=0, column=2, padx=5)

# Initial load of available files
refresh_file_list()

root.mainloop()
