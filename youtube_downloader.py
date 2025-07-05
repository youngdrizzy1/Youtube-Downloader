import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from pytubefix import YouTube

def download_video():
    url = url_entry.get()
    save_path = path_label.cget("text")
    
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL!")
        return
    if not save_path or save_path == "Not Selected":
        messagebox.showerror("Error", "Please select a save location!")
        return
    
    try:
        status_label.config(text="Downloading...", fg="blue")
        download_button.config(state=tk.DISABLED)
        threading.Thread(
            target=perform_download, 
            args=(url, save_path),
            daemon=True
        ).start()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def perform_download(url, save_path):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension="mp4").get_highest_resolution()
        stream.download(output_path=save_path)
        status_label.config(text=f"Download Complete!\nSaved to: {save_path}", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
    finally:
        download_button.config(state=tk.NORMAL)

def open_file_dialog():
    folder = filedialog.askdirectory()
    if folder:
        path_label.config(text=folder)

root = tk.Tk()
root.title("YouTube Downloader (pytubefix)")
root.geometry("500x250")

tk.Label(root, text="YouTube URL:").pack(pady=(10, 0))
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5, padx=20)

path_frame = tk.Frame(root)
path_frame.pack(fill=tk.X, padx=20, pady=10)

tk.Label(path_frame, text="Save Location:").pack(side=tk.LEFT)
path_label = tk.Label(
    path_frame, 
    text="Not Selected", 
    bg="white", 
    relief=tk.SUNKEN,
    anchor="w",
    width=40
)
path_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

browse_button = tk.Button(
    path_frame, 
    text="Browse", 
    command=open_file_dialog
)
browse_button.pack(side=tk.RIGHT)

download_button = tk.Button(
    root, 
    text="Download Video", 
    command=download_video,
    bg="#4CAF50",
    fg="white",
    padx=10,
    pady=5
)
download_button.pack(pady=10)

status_label = tk.Label(root, text="", fg="black", wraplength=450)
status_label.pack()

root.mainloop()