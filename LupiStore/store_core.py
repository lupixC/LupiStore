import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

STORE = Path(__file__).resolve().parent
ROOT = STORE.parent
APPS = {
    'dolphin': ('Dolphin', 'dolphin-python-windows-x64.zip', 'dolphin-python'),
    'minecraft': ('Lupilauncher', 'LupiLauncher.zip', 'LupiLauncher'),
    'osu': ('Osu!Lazer', 'osu-lazer-python-windows-x64.zip', 'osu-lazer-python'),
}


def download(url, destination, progress):
    request = urllib.request.Request(url, headers={'User-Agent': 'LupiStore'})
    with urllib.request.urlopen(request, timeout=30) as response, destination.open('wb') as output:
        total = int(response.headers.get('Content-Length', 0))
        received = 0
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
            received += len(chunk)
            progress(f'Downloading: {received // (1024 * 1024)} MB' +
                     (f' / {total // (1024 * 1024)} MB' if total else ''))


def extract_archive(archive_path, destination):
    destination = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            name = PurePosixPath(member.filename.replace('\\', '/'))
            if name.is_absolute() or '..' in name.parts or any(':' in part for part in name.parts):
                raise ValueError('Archive contains an invalid path.')
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Archive contains a symbolic link.')
            target = destination.joinpath(*name.parts)
            if not target.resolve().is_relative_to(destination):
                raise ValueError('Archive path leaves the install directory.')
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, target.open('wb') as output:
                    shutil.copyfileobj(source, output)


def install_app(key, progress):
    tag, filename, folder = APPS[key]
    apps = STORE / 'apps'
    apps.mkdir(exist_ok=True)
    destination = apps / folder
    if (destination / 'main.py').is_file():
        return destination
    with tempfile.TemporaryDirectory(prefix='.install-', dir=apps) as temporary:
        stage = Path(temporary)
        archive = stage / 'download.zip'
        url = f'https://github.com/lupixC/LupiStore/releases/download/{tag}/{filename}'
        download(url, archive, progress)
        progress('Extracting files…')
        extract_archive(archive, stage / 'unpacked')
        source = stage / 'unpacked' / folder
        if not (source / 'main.py').is_file():
            raise RuntimeError('The app download does not contain its expected main.py.')
        previous = None
        if destination.exists():
            previous = apps / (folder + '.incomplete-' + stage.name.removeprefix('.install-'))
            destination.rename(previous)
            progress(f'Previous incomplete files preserved in {previous.name}')
        try:
            source.rename(destination)
        except OSError:
            if previous:
                previous.rename(destination)
            raise
    return destination


def launch_app(directory):
    logs = ROOT / 'logs'
    logs.mkdir(exist_ok=True)
    log = logs / f'{directory.name}.log'

    with log.open('ab') as output:
        return subprocess.Popen([sys.executable, str(directory / 'main.py')], cwd=directory,
                                stdout=output, stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)


def update_store(progress):
    with tempfile.TemporaryDirectory(prefix='.update-', dir=ROOT) as temporary:
        stage = Path(temporary)
        archive = stage / 'update.zip'
        download('https://github.com/lupixC/LupiStore/archive/refs/heads/main.zip', archive, progress)
        extract_archive(archive, stage / 'unpacked')
        candidates = list((stage / 'unpacked').iterdir())
        if len(candidates) != 1:
            raise RuntimeError('Unexpected update archive.')
        source = candidates[0]
        if not (source / 'launcher.py').is_file():
            raise RuntimeError('Publish the new launcher files to GitHub before using Update.')

        allowed = ['launcher.py', 'LupiStore.pyw', 'LupiSetup.pyw', 'Abrir LupiStore.lnk', 'Setup.lnk', 'windows_shortcuts.py', 'requirements.txt',
                   'README.md', 'LICENSE', 'Setup/main.py', 'LupiStore/main.py',
                   'LupiStore/store_core.py', 'LupiStore/mainwindow.ui']
        allowed += [p.relative_to(source).as_posix() for base in ('LupiStore/images', 'Setup/images')
                    for p in (source / base).rglob('*') if p.is_file()]
        replaced = []
        try:
            for name in allowed:
                incoming = source / name
                if not incoming.is_file():
                    raise RuntimeError(f'Update is missing {name}.')
                target = ROOT / name
                if not target.resolve().is_relative_to(ROOT.resolve()):
                    raise RuntimeError('Update destination leaves the store folder.')
                backup = stage / 'backup' / name
                existed = target.exists()
                if existed:
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, backup)
                target.parent.mkdir(parents=True, exist_ok=True)
                pending = target.with_name(target.name + '.new')
                shutil.copy2(incoming, pending)
                os.replace(pending, target)
                replaced.append((target, backup, existed))
        except Exception:
            for target, backup, existed in reversed(replaced):
                if existed:
                    shutil.copy2(backup, target)
                else:
                    target.unlink(missing_ok=True)
            raise


def restart_store():
    return subprocess.Popen([sys.executable, str(ROOT / 'LupiStore.pyw')], cwd=ROOT,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
