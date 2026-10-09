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
    links = [(desktop / 'LupiStore.lnk', 'LupiStore.pyw', 'LupiStore'),
             (ROOT / 'Open LupiStore.lnk', 'LupiStore.pyw', 'LupiStore'),
             (ROOT / 'Setup.lnk', 'LupiSetup.pyw', 'LupiStore Setup')]
    for target, script, description in links:
        pending = target.with_name(target.stem + '.pending.lnk')
        try:
            link = pylnk3.for_file(str(ROOT / 'LupiStore' / 'pyw.exe'),
                           arguments=f'-3.14 "{ROOT / script}"',
                           description=description, icon_file=str(icon), work_dir=str(ROOT))
            for entry in link.shell_item_id_list.items:
                if isinstance(entry, pylnk3.PathSegmentEntry) and not entry.short_name.isascii():
                    entry.type += ' (UNICODE)'
            link.save(str(pending))
            os.replace(pending, target)
        finally:
            pending.unlink(missing_ok=True)
