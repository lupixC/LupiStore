import os
import sys
import certifi
import time
from PySide6.QtCore import QFile, QObject, Signal, Slot, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import urllib.request
import zipfile
from os.path import dirname
import subprocess
import threading
app_number = 2
separator = os.path.sep


class UiSignals(QObject):
    run_button_icon_changed = Signal(str)
    
os.environ['SSL_CERT_FILE'] = certifi.where()

def run_app():
    global app_number
    if app_number == 1:
        if not os.path.exists("apps//dolphin-python-windows-x64"):
          ui_signals.run_button_icon_changed.emit(
              os.path.join(dirname(__file__), "images", "installing.png")
          )
          os.makedirs("apps//dolphin-python-windows-x64")
          current_path = dirname(__file__)
          path = os.path.join(current_path, "apps")
          link = "https://github.com/lupixC/LupiStore/releases/download/Dolphin/dolphin-python-windows-x64.zip"
          file_name = "dolphin-python-windows-x64.zip"
          urllib.request.urlretrieve(link, file_name)
          with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(path)
          os.remove("dolphin-python-windows-x64.zip")
          ui_signals.run_button_icon_changed.emit(
              os.path.join(dirname(__file__), "images", "runing.png")
          )
          subprocess.Popen(["pyw", r"apps\dolphin-python-windows-x64\main.py"])
          time.sleep(2)
          ui_signals.run_button_icon_changed.emit(
             os.path.join(dirname(__file__), "images", "minecraft-text (1).png")
         )
        else:
           ui_signals.run_button_icon_changed.emit(
               os.path.join(dirname(__file__), "images", "runing.png")
           )
           current_path = dirname(__file__)
           path = os.path.join(current_path, "apps")
           subprocess.Popen(["pyw", r"apps\dolphin-python-windows-x64\main.py"])
        time.sleep(2)
        ui_signals.run_button_icon_changed.emit(
            os.path.join(dirname(__file__), "images", "minecraft-text (1).png")
        )

    elif app_number == 2:
        if not os.path.exists("apps//LupiLauncher"):
         ui_signals.run_button_icon_changed.emit(
             os.path.join(dirname(__file__), "images", "installing.png")
         )
         current_path = dirname(__file__)
         path = os.path.join(current_path, "apps")
         link = "https://github.com/lupixC/LupiStore/releases/download/Lupilauncher/LupiLauncher.zip"
         file_name = "LupiLauncher.zip"
         urllib.request.urlretrieve(link, file_name)
         with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(path)
         os.remove("LupiLauncher.zip")
         ui_signals.run_button_icon_changed.emit(
             os.path.join(dirname(__file__), "images", "runing.png")
         )
         subprocess.Popen(["pyw", r"apps\LupiLauncher\main.py"])
         time.sleep(3)
         ui_signals.run_button_icon_changed.emit(
             os.path.join(dirname(__file__), "images", "minecraft-text (1).png")
         )
        else:
         ui_signals.run_button_icon_changed.emit(
             os.path.join(dirname(__file__), "images", "runing.png")
         )
         subprocess.Popen(["pyw", r"apps\LupiLauncher\main.py"])
        time.sleep(3)
        ui_signals.run_button_icon_changed.emit(
            os.path.join(dirname(__file__), "images", "minecraft-text (1).png")
        )

    elif app_number == 3:
         if not os.path.exists("apps//osu-lazer-python"):
           ui_signals.run_button_icon_changed.emit(
               os.path.join(dirname(__file__), "images", "installing.png")
           )
           current_path = dirname(__file__)
           path = os.path.join(current_path, "apps")
           link = "https://github.com/lupixC/LupiStore/releases/download/Osu!Lazer/osu-lazer-python-windows-x64.zip"
           file_name = "osu-lazer-python-windows-x64.zip"
           urllib.request.urlretrieve(link, file_name)
           with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(path)
           os.remove("osu-lazer-python-windows-x64.zip")
           ui_signals.run_button_icon_changed.emit(
               os.path.join(dirname(__file__), "images", "runing.png")
           )
           subprocess.Popen(["pyw", r"apps\osu-lazer-python\main.py"])
           time.sleep(4.5)
           ui_signals.run_button_icon_changed.emit(
             os.path.join(dirname(__file__), "images", "minecraft-text (1).png")
         )
         else:
           ui_signals.run_button_icon_changed.emit(
               os.path.join(dirname(__file__), "images", "runing.png")
           )
           subprocess.Popen(["pyw", r"apps\osu-lazer-python\main.py"])
         time.sleep(4.5)
         ui_signals.run_button_icon_changed.emit(
             os.path.join(dirname(__file__), "images", "minecraft-text (1).png")
         )


def thread_run_app():
    thread_run = threading.Thread(target=run_app)
    thread_run.start()


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


class UiUpdater(QObject):
    @Slot(str)
    def set_run_button_icon(self, icon_path):
        widget("runButton").setIcon(QIcon(icon_path))


ui_signals = UiSignals()
ui_updater = UiUpdater()


for _button_name in (
    "dolphinButton",
    "minecraftLauncherButton",
    "osuButton",
    "runButton",
):
    _button = widget(_button_name)
    _button_size = _button.size()
    _button.setIconSize(_button_size * 0.6)


from PySide6.QtGui import QPixmap
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
    thread_run_app()

def update_lupi_store():
    widget("update").setText("Updating...")
    app.processEvents()
    link_py = "https://raw.githubusercontent.com/lupixC/LupiStore/main/LupiStore/LupiStore.py"
    link_ui = "https://raw.githubusercontent.com/lupixC/LupiStore/main/LupiStore/mainwindow.ui"
    link_zip = "https://github.com/lupixC/LupiStore/releases/download/ImageSystem/images.zip"
    urllib.request.urlretrieve(link_py, "LupiStore.py.new")
    urllib.request.urlretrieve(link_ui, "mainwindow.ui.new")
    urllib.request.urlretrieve(link_zip, "images.zip")
    with zipfile.ZipFile("images.zip", 'r') as zip_ref:
        zip_ref.extractall("images")

    widget("update").setText("Restarting LupiStore...")
    app.processEvents()
    os.remove("images.zip")
    restart = (
            "timeout /t 1 && "
            "move /y LupiStore.py.new LupiStore.py && "
            "move /y mainwindow.ui.new mainwindow.ui && "
            "py LupiStore.py"
              )
    subprocess.Popen(restart, shell=True)
    ui.close()
    

widget("dolphinButton").clicked.connect(run_dolphin)
widget("minecraftLauncherButton").clicked.connect(run_minecraft)
widget("osuButton").clicked.connect(run_osu)
widget("runButton").clicked.connect(run_button_clicked)
widget("update").clicked.connect(update_lupi_store)
ui_signals.run_button_icon_changed.connect(
    ui_updater.set_run_button_icon, Qt.QueuedConnection
)

sys.exit(app.exec())
