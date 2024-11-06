import tkinter as tk
from tkinter import filedialog
import json
import os
from file_download import *

# # Load metadata for available files
# def load_metadata():
#     with open("metadata.json", "r") as f:
#         return json.load(f)

def load_metadata():
    # Check if the file exists
    if not os.path.exists("metadata.json"):
        # Create a new metadata file with an empty structure
        with open("metadata.json", "w") as f:
            json.dump({"files": []}, f)
    
    # Read the metadata file
    with open("metadata.json", "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or malformed, reset to an empty structure
            return {"files": []}

# Upload file to the shared folder and update metadata
def upload_file():
    file_path = filedialog.askopenfilename()

    PORT = 5001

    if file_path:
        file_name = os.path.basename(file_path)
        destination = os.path.join("shared", file_name)
        os.makedirs("shared", exist_ok=True)
        os.rename(file_path, destination)  # Move file to shared folder
        
        # Update metadata
        with open("metadata.json", "r+") as f:
            data = json.load(f)
            data["files"].append({"file_name": file_name, "ip": "localhost", "port": PORT})
            f.seek(0)
            json.dump(data, f)

        print(f"File {file_name} uploaded and available for sharing.")

# # Download selected file
# def download_selected_file():
#     selected_file = file_listbox.get(file_listbox.curselection())
#     metadata = load_metadata()

#     # Find the selected file's details in metadata
#     for file_info in metadata["files"]:
#         if file_info["file_name"] == selected_file:
#             download_file(file_info["ip"], file_info["port"], file_info["file_name"])
#             break

def download_selected_file():
    # Check if an item is selected
    selection = file_listbox.curselection()
    if not selection:
        print("No file selected. Please select a file to download.")
        return

    # Proceed with download if an item is selected
    selected_file = file_listbox.get(selection)
    metadata = load_metadata()

    # Find the selected file's details in metadata
    for file_info in metadata["files"]:
        if file_info["file_name"] == selected_file:
            download_file(file_info["ip"], file_info["port"], file_info["file_name"])
            break

# Set up the GUI
root = tk.Tk()
root.title("P2P File Sharing System")

upload_button = tk.Button(root, text="Upload File", command=upload_file)
upload_button.pack(pady=10)

file_listbox = tk.Listbox(root)
file_listbox.pack(pady=10)

download_button = tk.Button(root, text="Download File", command=download_selected_file)
download_button.pack(pady=10)

# Load available files into listbox
metadata = load_metadata()
for file_info in metadata["files"]:
    file_listbox.insert(tk.END, file_info["file_name"])

root.mainloop()
