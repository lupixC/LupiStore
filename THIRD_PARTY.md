# Third-party components

Setup installs official Windows x64 wheels for:

- PySide6-Essentials and shiboken6 6.11.2: https://code.qt.io/cgit/pyside/pyside-setup.git/tree/?h=v6.11.2
- Qt 6.11.2: https://download.qt.io/archive/qt/6.11/6.11.2/submodules/
- Pillow 12.3.0: https://github.com/python-pillow/Pillow
- minecraft-launcher-lib 8.0: https://github.com/JakobDev/minecraft-launcher-lib
- requests and its dependencies: see each bundled dist-info/METADATA and licenses directory.

Package metadata and license files are retained under .deps/cpython-314/. Extra Qt development executables are omitted; the store uses Qt DLLs and Python modules. Qt license texts are included in ThirdPartyLicenses/. LupiStore's own MIT notice is LICENSE. The installed Python interpreter is supplied by your school, not bundled here.

The original LupiStore/pyw.exe is the Python Software Foundation Windows launcher, retained byte-for-byte from this repository. Python license: https://docs.python.org/3/license.html

- pylnk3 0.4.3 (LGPL): https://github.com/strayge/pylnk
