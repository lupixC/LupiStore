import math
from posixpath import dirname
import os
import threading
import tkinter as tk
from tkinter import messagebox
import zipfile
import urllib.request
from pathlib import Path
import subprocess
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()

root = tk.Tk()
root.title("Lupi Setup")
root.geometry("900x650")
root.resizable(False, False)
root.configure(background="#ffffff")

title = tk.Label(
    root,
    text="Welcome to LupiStore Setup!",
    font=("Arial", 20),
    fg="#111111",
    bg="#ffffff",
    anchor="w",
)
title.place(x=310, y=30, width=550, height=70)

image_path = Path(__file__).resolve().parent / "images" / "Untitled design-modified.png"
image = tk.PhotoImage(file=str(image_path))
scale = max(1, math.ceil(max(image.width(), image.height()) / 130))
image = image.subsample(scale, scale)
image_label = tk.Label(root, image=image, bg="#ffffff")
image_label.image = image
image_label.place(x=60, y=30, width=130, height=130)

intro = tk.Label(
    root,
    text=(
        'When clicking the "Install" button, LupiSetup will install libraries from '
        "python, these libraries are 100% safe, opensource and monitored by community."
    ),
    font=("Arial", 16),
    fg="#111111",
    bg="#ffffff",
    justify="left",
    anchor="nw",
    wraplength=760,
)
intro.place(x=70, y=200, width=760, height=80)


def _show_install_result(error):
    if error is None:
        install_button.configure(state="normal", text="Installed!")
    else:
        install_button.configure(state="normal", text="Install")
        messagebox.showerror("Installation failed", str(error), parent=root)


def install_dependencies():
            current_path = dirname(__file__)
            path = os.path.join(current_path, "dependencies")
            link = "https://github.com/lupixC/LupiStore/releases/download/Dependencies/Dependencies.zip"
            file_name = "Dependencies.zip"
            install_button.configure(state="disabled", text="Downloading...")
            urllib.request.urlretrieve(link, file_name)
            install_button.configure(state="disabled", text="Installing...")
            with zipfile.ZipFile(file_name, 'r') as zip_ref:
               zip_ref.extractall(path)
            os.remove("Dependencies.zip")
            subprocess.run(["py", "-m", "pip", "install", "--no-index", "--find-links=" + path, "-r", os.path.join(path, "requirements.txt")])
            install_button.configure(state="disabled", text="Installed!")


def Install_command():
    threading.Thread(target=install_dependencies, daemon=True).start()    



install_button = tk.Button(
    root,
    text="Install",
    font=("Arial", 10),
    fg="#111111",
    bg="#ffffff",
    command=Install_command,
)
install_button.place(x=400, y=520, width=120, height=38)

root.mainloop()
