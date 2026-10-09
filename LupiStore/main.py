import os
import subprocess
import shutil
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from launcher import activate_dependencies
activate_dependencies()

from PySide6.QtCore import QFile, QObject, QThread, Signal, Slot, Qt, QDir
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMessageBox, QLabel
from store_core import STORE, install_app, launch_app, update_store, restart_store


class Worker(QObject):
    progress = Signal(str)
    finished = Signal(str, str)

    def __init__(self, action, key):
        super().__init__()
        self.action = action
        self.key = key

    @Slot()
    def run(self):
        try:
            if self.action == 'app':
                if self.key == 'minecraft' and shutil.which('java') is None:
                    raise RuntimeError('Minecraft needs Java. Install the approved OpenJDK from Software Center first.')
                directory = install_app(self.key, self.report)
                process = launch_app(directory)

                try:
                    code = process.wait(timeout=2)
                    if code:
                        raise RuntimeError(f'The app exited with code {code}. See logs/{directory.name}.log.')
                except subprocess.TimeoutExpired:
                    pass
                self.finished.emit('app', 'App started')
            else:
                update_store(self.report)
                self.finished.emit('update', 'Update installed')
        except Exception as error:
            self.finished.emit('error', str(error))

    def report(self, message):
        if QThread.currentThread().isInterruptionRequested():
            raise RuntimeError('Operation cancelled.')
        self.progress.emit(message)


class StoreController(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.selected = 'minecraft'
        self.thread = None
        loader = QUiLoader()
        loader.setWorkingDirectory(QDir(str(STORE)))
        file = QFile(str(STORE / 'mainwindow.ui'))
        if not file.open(QFile.ReadOnly):
            raise RuntimeError(file.errorString())
        self.ui = loader.load(file)
        file.close()
        if self.ui is None:
            raise RuntimeError(loader.errorString())
        self.ui.setWindowIcon(QIcon(str(STORE / 'images/lupi.ico')))
        for name in ('dolphinButton', 'minecraftLauncherButton', 'osuButton', 'runButton'):
            button = self.widget(name)
            button.setIconSize(button.size() * .6)
        for name, image in [('image', 'download.png'), ('image2', 'minecraft-text (2).png'), ('image3', '1.png')]:
            label = self.widget(name)
            pixmap = QPixmap(str(STORE / 'images' / image))
            label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.status = QLabel('Ready', self.ui)
        self.status.setGeometry(40, 610, 820, 30)
        self.widget('dolphinButton').clicked.connect(lambda: self.select('dolphin', 40))
        self.widget('minecraftLauncherButton').clicked.connect(lambda: self.select('minecraft', 320))
        self.widget('osuButton').clicked.connect(lambda: self.select('osu', 600))
        self.widget('runButton').clicked.connect(lambda: self.start('app'))
        self.widget('update').clicked.connect(lambda: self.start('update'))
        self.select('minecraft', 320)
        self.ui.show()

    def widget(self, name):
        obj = self.ui.findChild(QObject, name)
        if obj is None:
            raise RuntimeError(f'Widget not found: {name}')
        return obj

    def select(self, key, x):
        self.selected = key
        self.widget('image3').move(x, 90)

    def start(self, action):
        if self.thread is not None:
            return
        self.busy(True)
        self.status.setText('Preparing app…' if action == 'app' else 'Checking for updates…')
        self.thread = QThread(self)
        self.worker = Worker(action, self.selected)
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.status.setText)
        self.worker.finished.connect(self.complete)
        self.worker.finished.connect(self.thread.quit, Qt.DirectConnection)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.cleanup)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def busy(self, value):
        for name in ('dolphinButton', 'minecraftLauncherButton', 'osuButton', 'runButton', 'update'):
            self.widget(name).setEnabled(not value)

    @Slot(str, str)
    def complete(self, result, message):
        self.status.setText(message)
        if result == 'error':
            QMessageBox.warning(self.ui, 'LupiStore', message)
        elif result == 'update':
            self.pending_restart = True

    @Slot()
    def cleanup(self):
        self.thread.deleteLater()
        self.thread = None
        self.worker = None
        self.busy(False)
        if getattr(self, 'pending_restart', False):
            restart_store()
            self.app.quit()

    def shutdown(self):
        if self.thread is not None:
            self.thread.requestInterruption()
            self.thread.quit()
            self.thread.wait()


def main():
    app = QApplication(sys.argv)
    controller = StoreController(app)
    app.aboutToQuit.connect(controller.shutdown)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
