import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import traceback

ROOT = Path(__file__).resolve().parent
DEPENDENCIES = ROOT / '.deps' / sys.implementation.cache_tag
REQUIREMENTS = ROOT / 'requirements.txt'


def activate_dependencies():
    if DEPENDENCIES.is_dir():
        sys.path.insert(0, str(DEPENDENCIES))
    os.environ['PYTHONPATH'] = os.pathsep.join(
        [str(DEPENDENCIES)] + ([os.environ['PYTHONPATH']] if os.environ.get('PYTHONPATH') else [])
    )


def dependencies_ready():
    try:
        marker = json.loads((DEPENDENCIES / '.ready.json').read_text())
        return marker['requirements'] == REQUIREMENTS.read_text() and (DEPENDENCIES / 'pylnk3.py').is_file() and all(
            (DEPENDENCIES / name).is_dir()
            for name in ('PySide6', 'PIL', 'minecraft_launcher_lib')
        )
    except (OSError, ValueError, KeyError):
        return False


def install_dependencies(progress):
    DEPENDENCIES.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.install-', dir=DEPENDENCIES.parent) as temporary:
        stage = Path(temporary) / 'libraries'
        command = [sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check',
                   '--no-warn-script-location', '--only-binary=:all:', '--target', str(stage),
                   '--cache-dir', str(ROOT / '.cache' / 'pip'), '-r', str(REQUIREMENTS)]
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding='utf-8', errors='replace', creationflags=flags) as process:
            output = []
            for line in process.stdout:
                output.append(line)
                progress(line.strip())
            if process.wait():
                log = ROOT / 'logs' / 'setup.log'
                log.parent.mkdir(exist_ok=True)
                log.write_text(''.join(output), encoding='utf-8')
                raise RuntimeError(f'Could not install dependencies. Check your connection and {log}.')
        (stage / '.ready.json').write_text(json.dumps({'requirements': REQUIREMENTS.read_text()}))
        backup = DEPENDENCIES.with_name(DEPENDENCIES.name + '.previous')
        if backup.exists():
            shutil.rmtree(backup)
        if DEPENDENCIES.exists():
            DEPENDENCIES.rename(backup)
        try:
            stage.rename(DEPENDENCIES)
        except OSError:
            if backup.exists():
                backup.rename(DEPENDENCIES)
            raise
        if backup.exists():
            shutil.rmtree(backup)


def launch_store():
    activate_dependencies()
    store = ROOT / 'LupiStore'
    sys.path.insert(0, str(store))
    runpy.run_path(str(store / 'main.py'), run_name='__main__')


def main(setup=False):
    try:
        if sys.version_info < (3, 10):
            raise RuntimeError('LupiStore needs Python 3.10 or newer; use Python 3.14 from Software Center.')
        if os.name == 'nt' and sys.maxsize <= 2**32:
            raise RuntimeError('Use 64-bit Python; the bundled apps do not support 32-bit Python.')
        if sysconfig.get_config_var('Py_GIL_DISABLED'):
            raise RuntimeError('Use regular Python 3.14, not the experimental free-threaded build.')
        if setup or not dependencies_ready():
            runpy.run_path(str(ROOT / 'Setup' / 'main.py'), run_name='__main__')
        else:
            launch_store()
    except SystemExit:
        raise
    except Exception as error:
        logs = ROOT / 'logs'
        logs.mkdir(exist_ok=True)
        (logs / 'startup.log').write_text(traceback.format_exc(), encoding='utf-8')
        message = f'{error}\n\nDetails: {logs / "startup.log"}'
        try:
            import tkinter as tk
            from tkinter import messagebox
            window = tk.Tk()
            window.withdraw()
            messagebox.showerror('LupiStore could not start', message)
            window.destroy()
        except Exception:
            if os.name == 'nt':
                import ctypes
                ctypes.windll.user32.MessageBoxW(None, message, 'LupiStore could not start', 0x10)
            else:
                print(message, file=sys.stderr)



if __name__ == '__main__':
    main()
