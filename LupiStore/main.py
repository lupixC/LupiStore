import sys
from PySide6.QtCore import QFile, QObject
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
import urllib.request
import zipfile

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


from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
_pix_image = QPixmap(r"images/download.png")
widget("image").setPixmap(_pix_image.scaled(widget("image").size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
_pix_image3 = QPixmap(r"images/1.png")
image3 = widget("image3")
widget("image3").setPixmap(_pix_image3.scaled(widget("image3").size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
_pix_image2 = QPixmap(r"images/minecraft-text (2).png")
widget("image2").setPixmap(_pix_image2.scaled(widget("image2").size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

ui.show()

# button
widget("dolphinButton").clicked.connect(lambda _checked=False: image3.move(40, 90))
widget("minecraftLauncherButton").clicked.connect(lambda _checked=False: image3.move(320, 90))
widget("osuButton").clicked.connect(lambda _checked=False: image3.move(600, 90))
widget("runButton").clicked.connect(lambda _checked=False: print("Run button clicked!"))

sys.exit(app.exec())
