import os
import sys
from PySide6.QtCore import QFile, QObject
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import urllib.request
import zipfile
from os.path import dirname
import subprocess
app_number = 2
separator = os.path.sep
def run_app():
    global app_number
    if app_number == 1:
        if not os.path.exists("apps//dolphin-python"):
         current_path = dirname(__file__)
         path = os.path.join(current_path, "apps")
         link = "https://github.com/lupixC/LupiStore/releases/download/Dolphin/dolphin-python-windows-x64.zip"
         file_name = "dolphin-python-windows-x64.zip"
         urllib.request.urlretrieve(link, file_name)
         with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(path)
         os.remove("dolphin-python-windows-x64.zip")
         subprocess.run(["py", r"apps\dolphin-python\launch.py"])
        else:
         subprocess.run(["py", r"apps\dolphin-python\launch.py"])
        
         
    elif app_number == 2:
        if not os.path.exists("apps//LupiLauncher"):
         current_path = dirname(__file__)
         path = os.path.join(current_path, "apps")
         link = "https://github.com/lupixC/LupiStore/releases/download/Lupilauncher/LupiLauncher.zip"
         file_name = "LupiLauncher.zip"
         urllib.request.urlretrieve(link, file_name)
         with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(path)
         os.remove("LupiLauncher.zip")
         subprocess.run(["py", r"apps\LupiLauncher\main.py"])
        else:
         subprocess.run(["py", r"apps\LupiLauncher\main.py"])
    elif app_number == 3:
        path = dirname(__file__)
app = QApplication(sys.argv)
file = QFile("mainwindow.ui")
if not file.open(QFile.ReadOnly):
    raise RuntimeError(file.errorString())
ui = QUiLoader().load(file)
file.close()
if ui is None:
    raise RuntimeError("Could not load mainwindow.ui")

def widget(name):
    obj = ui.findChild(QObject, name)
    if obj is None:
        raise RuntimeError(f"Widget not found: {name}")
    return obj


for _button_name in (
    "dolphinButton",
    "minecraftLauncherButton",
    "osuButton",
    "runButton",
):
    _button = widget(_button_name)
    _button_size = _button.size()
    _button.setIconSize(_button_size * 0.6)


# Optional: keep aspect ratio for image labels.
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
_pix_image = QPixmap(r"images/download.png")
widget("image").setPixmap(_pix_image.scaled(widget("image").size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
_pix_image3 = QPixmap(r"images/1.png")
image3 = widget("image3")
widget("image3").setPixmap(_pix_image3.scaled(widget("image3").size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
_pix_image2 = QPixmap(r"images/minecraft-text (2).png")
widget("image2").setPixmap(_pix_image2.scaled(widget("image2").size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
icon = QIcon(os.path.join(dirname(__file__), "images", "lupi.ico"))
ui.setWindowIcon(icon)
ui.show()

def run_dolphin():
    image3.move(40, 90)
    global app_number
    app_number = 1

def run_minecraft():
    image3.move(320, 90)
    global app_number
    app_number = 2

def run_osu():
    image3.move(600, 90)
    global app_number
    app_number = 3

def run_button_clicked():
    run_app()

widget("dolphinButton").clicked.connect(run_dolphin)
widget("minecraftLauncherButton").clicked.connect(run_minecraft)
widget("osuButton").clicked.connect(run_osu)
widget("runButton").clicked.connect(run_button_clicked)

sys.exit(app.exec())
