import math
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from launcher import activate_dependencies, install_dependencies, launch_store
from windows_shortcuts import create_desktop_shortcut


def main():
    root = tk.Tk()
    root.title('LupiStore Setup')
    root.geometry('760x510')
    root.configure(background='white')
    messages = queue.Queue()
    busy = False
    should_launch = False
    image_path = Path(__file__).parent / 'images' / 'Untitled design-modified.png'
    if image_path.exists():
        image = tk.PhotoImage(file=str(image_path))
        image = image.subsample(max(1, math.ceil(max(image.width(), image.height()) / 110)))
        label = tk.Label(root, image=image, bg='white')
        label.image = image
        label.pack(pady=(20, 5))
    tk.Label(root, text='Welcome to LupiStore', font=('Arial', 22), bg='white').pack(pady=10)
    tk.Label(root, text='Setup downloads the Python libraries needed by the store and its apps.\n'
                       'Libraries stay inside this folder; no administrator access is needed.\n\n'
                       'Use your school’s approved Python and internet access.\n'
                       'Setup creates a LupiStore desktop shortcut and opens the store.',
             justify='center', font=('Arial', 12), bg='white', wraplength=680).pack(pady=15)
    status = tk.StringVar(value='Ready to install')
    tk.Label(root, textvariable=status, bg='white', wraplength=680).pack(pady=10)
    progress = ttk.Progressbar(root, mode='indeterminate', length=550)
    progress.pack(pady=10)

    def worker():
        try:
            install_dependencies(lambda text: messages.put(('progress', text)))
            activate_dependencies()
            create_desktop_shortcut()
            messages.put(('done', None))
        except Exception as error:
            messages.put(('error', str(error)))

    def install():
        nonlocal busy
        busy = True
        button.configure(state='disabled')
        status.set('Installing libraries…')
        progress.start()
        threading.Thread(target=worker, daemon=True).start()

    def poll():
        nonlocal busy, should_launch
        while not messages.empty():
            kind, value = messages.get_nowait()
            if kind == 'progress':
                status.set(value[:160])
            elif kind == 'error':
                busy = False
                progress.stop()
                button.configure(state='normal')
                status.set('Installation failed; you can retry.')
                messagebox.showerror('Setup failed', value, parent=root)
            elif kind == 'done':
                busy = False
                should_launch = True
                root.destroy()
                return
        root.after(100, poll)

    def close():
        if busy:
            messagebox.showinfo('Installing', 'Please wait for installation to finish.', parent=root)
        else:
            root.destroy()

    button = ttk.Button(root, text='Install and open LupiStore', command=install)
    button.pack(pady=12)
    root.protocol('WM_DELETE_WINDOW', close)
    root.after(100, poll)
    root.mainloop()
    if should_launch:
        launch_store()


if __name__ == '__main__':
    main()
