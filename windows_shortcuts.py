import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parent


def desktop_directory():
    shell = ctypes.WinDLL('shell32', use_last_error=True)
    ole = ctypes.WinDLL('ole32', use_last_error=True)
    shell.SHGetKnownFolderPath.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.HANDLE,
                                         ctypes.POINTER(ctypes.c_void_p)]
    shell.SHGetKnownFolderPath.restype = ctypes.c_long
    ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    identifier = ctypes.create_string_buffer(uuid.UUID('B4BFCC3A-DB2C-424C-B029-7FE99A87C641').bytes_le)
    location = ctypes.c_void_p()
    result = shell.SHGetKnownFolderPath(identifier, 0, None, ctypes.byref(location))
    if result < 0:
        raise OSError(f'Could not locate your Windows desktop: 0x{result & 0xffffffff:08x}')
    try:
        return Path(ctypes.wstring_at(location))
    finally:
        ole.CoTaskMemFree(location)


def create_desktop_shortcut():
    if os.name != 'nt':
        return
    import pylnk3
    icon = ROOT / 'LupiStore' / 'images' / 'lupi.ico'
    desktop = desktop_directory()
    desktop.mkdir(parents=True, exist_ok=True)
    target = desktop / 'LupiStore.lnk'
    pending = target.with_name('LupiStore.pending.lnk')
    try:
        pylnk3.for_file(str(ROOT / 'LupiStore' / 'pyw.exe'), str(pending),
                       arguments=f'-3.14 "{ROOT / "LupiStore.pyw"}"',
                       description='LupiStore', icon_file=str(icon), work_dir=str(ROOT))
        os.replace(pending, target)
    finally:
        pending.unlink(missing_ok=True)
    for name in ('Abrir LupiStore.lnk', 'Setup.lnk'):
        path = ROOT / name
        link = pylnk3.parse(str(path))
        link.icon = str(icon)
        link.save(str(path))
