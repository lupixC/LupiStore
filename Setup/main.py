import math
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


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

details = tk.Label(
    root,
    text=(
        "After clicking install, there will be a notification that says that the IT "
        "admin will get notified if you press unblock. unblock doesnt unblocks the "
        "computer or tries to bypass it in some way, is a mechanism made by the IT "
        "for unblocking websites only when you need it. If you are worried about "
        "pressing unblock you can check the School rules, I have some emails from "
        "the IT of HWDSB talking about this, this doesnt means that every school of "
        "HWDSB will accept this without previous approval."
    ),
    font=("Arial", 14),
    fg="#111111",
    bg="#ffffff",
    justify="left",
    anchor="nw",
    wraplength=760,
)
details.place(x=70, y=300, width=760, height=200)


def _show_install_result(error):
    if error is None:
        install_button.configure(state="normal", text="Installed!")
    else:
        install_button.configure(state="normal", text="Install")
        messagebox.showerror("Installation failed", str(error), parent=root)


def _install_dependencies():
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "Pillow", "minecraft-launcher-lib"],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        root.after(0, _show_install_result, error)
    else:
        root.after(0, _show_install_result, None)


def install_dependencies():
    install_button.configure(state="disabled", text="Installing...")
    threading.Thread(target=_install_dependencies, daemon=True).start()


install_button = tk.Button(
    root,
    text="Install",
    font=("Arial", 10),
    fg="#111111",
    bg="#ffffff",
    command=install_dependencies,
)
install_button.place(x=400, y=520, width=120, height=38)

root.mainloop()
