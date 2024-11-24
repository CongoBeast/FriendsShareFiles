# import tkinter as tk
# from tkinter import simpledialog, filedialog
# import json
# import os
# from file_download import *

# # Load or create metadata for available files
# def load_metadata():
#     if not os.path.exists("metadata.json"):
#         with open("metadata.json", "w") as f:
#             json.dump({"files": []}, f)
    
#     with open("metadata.json", "r") as f:
#         try:
#             return json.load(f)
#         except json.JSONDecodeError:
#             return {"files": []}

# # Prompt for username if not already saved
# def get_username():
#     if not os.path.exists("user_info.json"):
#         username = simpledialog.askstring("Enter Username", "Please enter your username:")
#         with open("user_info.json", "w") as f:
#             json.dump({"username": username}, f)
#     else:
#         with open("user_info.json", "r") as f:
#             user_data = json.load(f)
#             username = user_data.get("username", "User")
#     return username

# # Upload file to shared folder and update metadata
# def upload_file():
#     file_path = filedialog.askopenfilename()
#     PORT = 5001

#     if file_path:
#         file_name = os.path.basename(file_path)
#         destination = os.path.join("shared", file_name)
#         os.makedirs("shared", exist_ok=True)
#         os.rename(file_path, destination)
        
#         # Update metadata
#         with open("metadata.json", "r+") as f:
#             data = json.load(f)
#             data["files"].append({"file_name": file_name, "ip": "localhost", "port": PORT})
#             f.seek(0)
#             json.dump(data, f)
        
#         file_listbox.insert(tk.END, file_name)
#         print(f"File {file_name} uploaded and available for sharing.")

# # Download selected file
# def download_selected_file():
#     selection = file_listbox.curselection()
#     if not selection:
#         print("No file selected. Please select a file to download.")
#         return

#     selected_file = file_listbox.get(selection)
#     metadata = load_metadata()

#     for file_info in metadata["files"]:
#         if file_info["file_name"] == selected_file:
#             download_file(file_info["ip"], file_info["port"], file_info["file_name"])
#             break

# # Set up the GUI
# root = tk.Tk()
# root.title("P2P File Sharing System")
# root.geometry("400x400")  # Larger window size

# # Username entry
# username = get_username()
# username_label = tk.Label(root, text=f"Welcome, {username}!", font=("Helvetica", 12, "bold"))
# username_label.pack(pady=5)

# # File upload and download buttons with color styling
# upload_button = tk.Button(root, text="Upload File", command=upload_file, bg="green", fg="white", font=("Helvetica", 10))
# upload_button.pack(pady=10)

# # Filename list label
# list_label = tk.Label(root, text="Filename List:", font=("Helvetica", 10, "italic"))
# list_label.pack()

# file_listbox = tk.Listbox(root)
# file_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

# download_button = tk.Button(root, text="Download File", command=download_selected_file, bg="blue", fg="white", font=("Helvetica", 10))
# download_button.pack(pady=10)

# # Load available files into listbox
# metadata = load_metadata()
# for file_info in metadata["files"]:
#     file_listbox.insert(tk.END, file_info["file_name"])

# root.mainloop()
import tkinter as tk
from tkinter import simpledialog, filedialog
import json
import os
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

# Refresh the file list with updated metadata
def refresh_file_list():
    file_listbox.delete(0, tk.END)
    metadata = load_metadata()
    
    for file_info in metadata["files"]:
        file_display = (f"{file_info['file_name']} | Uploaded by: {file_info['username']} | "
                        f"Time: {file_info['upload_time']} | Downloads: {file_info['download_count']}")
        file_listbox.insert(tk.END, file_display)

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

# Buttons arranged side-by-side
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

upload_button = tk.Button(button_frame, text="Upload File", command=upload_file, bg="green", fg="white", font=("Helvetica", 10))
upload_button.grid(row=0, column=0, padx=5)

download_button = tk.Button(button_frame, text="Download File", command=download_selected_file, bg="blue", fg="white", font=("Helvetica", 10))
download_button.grid(row=0, column=1, padx=5)

# Initial load of available files
refresh_file_list()

root.mainloop()
