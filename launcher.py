import hashlib
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
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
DEPENDENCIES = ROOT / '.deps' / sys.implementation.cache_tag
REQUIREMENTS = ROOT / 'requirements.txt'
DEPENDENCY_ASSET = 'LupiStore-paquetes-windows-python314.zip'
DEPENDENCY_URL = 'https://github.com/lupixC/LupiStore/releases/download/dependencias-python314-v1/' + DEPENDENCY_ASSET
DEPENDENCY_SHA256 = '2636b949582458dedf26e27ea8187a41fdf1f03aed30d621df7459490d3bbc73'


def activate_dependencies():
    if DEPENDENCIES.is_dir():
        sys.path.insert(0, str(DEPENDENCIES))
    os.environ['PYTHONPATH'] = os.pathsep.join(
        [str(DEPENDENCIES)] + ([os.environ['PYTHONPATH']] if os.environ.get('PYTHONPATH') else [])
    )


def dependencies_ready():
    try:
        marker = json.loads((DEPENDENCIES / '.ready.json').read_text())
        return marker['requirements'] == REQUIREMENTS.read_text() and all(
            (DEPENDENCIES / name).is_dir()
            for name in ('PySide6', 'PIL', 'minecraft_launcher_lib')
        )
    except (OSError, ValueError, KeyError):
        return False


def dependency_archive(progress):
    cache = ROOT / '.cache'
    cache.mkdir(exist_ok=True)
    destination = cache / DEPENDENCY_ASSET
    if destination.is_file():
        with destination.open('rb') as existing:
            if hashlib.file_digest(existing, 'sha256').hexdigest() == DEPENDENCY_SHA256:
                progress('Using downloaded packages')
                return destination
        destination.unlink()
    progress('Downloading Windows Python 3.14 packages…')
    request = urllib.request.Request(DEPENDENCY_URL, headers={'User-Agent': 'LupiStore'})
    with tempfile.TemporaryDirectory(prefix='.download-', dir=cache) as temporary:
        pending = Path(temporary) / DEPENDENCY_ASSET
        digest = hashlib.sha256()
        try:
            with urllib.request.urlopen(request, timeout=30) as response, pending.open('wb') as output:
                total = int(response.headers.get('Content-Length', 0))
                received = 0
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
                    received += len(chunk)
                    progress(f'Downloading packages: {received // (1024 * 1024)} MB' +
                             (f' / {total // (1024 * 1024)} MB' if total else ''))
        except urllib.error.HTTPError as error:
            if error.code == 404:
                raise RuntimeError('The dependency release is not available. Publish dependencias-python314-v1 '
                                   f'with {DEPENDENCY_ASSET} on GitHub first.') from error
            raise
        if digest.hexdigest() != DEPENDENCY_SHA256:
            raise RuntimeError('The downloaded package ZIP failed verification. Please retry setup.')
        os.replace(pending, destination)
    return destination


def install_dependencies(progress):
    if sys.version_info[:2] != (3, 14) or sysconfig.get_platform() != 'win-amd64':
        raise RuntimeError('These packages require regular 64-bit Python 3.14 for Windows.')
    if sysconfig.get_config_var('Py_GIL_DISABLED'):
        raise RuntimeError('These packages require regular Python 3.14, not a free-threaded build.')
    archive_path = dependency_archive(progress)
    DEPENDENCIES.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.install-', dir=DEPENDENCIES.parent) as temporary:
        stage = Path(temporary) / 'libraries'
        wheels = Path(temporary) / 'wheels'
        wheels.mkdir()
        progress('Preparing downloaded packages…')
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                name = member.filename
                if not name.endswith('.whl'):
                    continue
                if Path(name).name != name or '\\' in name or ':' in name:
                    raise RuntimeError('Invalid package path in the dependency ZIP.')
                with archive.open(member) as source, (wheels / name).open('wb') as output:
                    shutil.copyfileobj(source, output)
        progress('Installing local packages…')
        command = [sys.executable, '-m', 'pip', '--isolated', 'install', '--disable-pip-version-check',
                   '--no-warn-script-location', '--only-binary=:all:', '--target', str(stage),
                   '--no-index', '--find-links', str(wheels), '--no-compile', '-r', str(REQUIREMENTS)]
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
                raise RuntimeError(f'Could not install dependencies. See {log}.')
        if not all((stage / name).is_dir() for name in ('PySide6', 'PIL', 'minecraft_launcher_lib')):
            raise RuntimeError('Package installation did not produce the required libraries.')
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
