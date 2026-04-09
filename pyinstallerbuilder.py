# -*- coding: utf-8 -*-
"""
PyInstaller project builder.
"""
# Import builder requirements.
from os.path import join, dirname, exists
from sys import version_info, platform
from os import system, path, environ
from pip import _internal

# Import setuptools.
try:
    from PyInstaller.__main__ import run
except:
    _internal.main(['install', 'PyInstaller'])
    from PyInstaller.__main__ import run

# Config space.
# Requirements installer config.
try:
    insReq = str(input('Install requirements (Y/N): '))  # type: str
except NameError as wrd:
    insReq = str(wrd).split("'")[1]  # type: str

# Release selection config.
appName = 'NGLv5'  # type: str
# Check for python version.
pyVers = 'Py2' if version_info[0] == 2 else 'Py3'  # type: str
# Setup Qt environment.
environ['QT_API'] = 'PyQt5'  # type: str
# Other Vars.
__buildDir__ = appName + '_' + pyVers + '_' + environ['QT_API'] + '_PyInstaller'  # type: str
hooksPath = join(dirname(__file__), 'hooks')  # type: str
try:
    runApp = input('Open App (Y/N): ')
except NameError as wrd:
    runApp = str(wrd).split("'")[1]


# Function to add data files/directories correctly.
def addDataFiles(sourceDir, targetDir=None):
    """
    Add a directory or file to PyInstaller's --add-data.
    :param sourceDir: (str | unicode) Source directory.
    :param targetDir: (str | unicode) Target directory.
    :return: str | unicode | None
    """
    if targetDir is None:
        targetDir = sourceDir
    sourcePath = join(dirname(__file__), sourceDir)
    if path.exists(sourcePath):
        # For Windows use ';', for Linux/Mac use ':'
        return '{}{}{}'.format(sourcePath, ';' if platform.lower() == 'win32' else ':', targetDir)
    return None


# Workspace:
# Install app requirements.
if insReq.lower() in ['y', 'yes', '1', 'oui']:
    for r in open('requirements.txt' if exists('requirements.txt') else join(
            dirname(__file__), 'requirements.txt'), 'r').readlines():
        _internal.main(['install', r.strip()])
        # setuptools._install_setup_requires([open('requirements.txt', 'r').readlines()])
# Start app builder.
pyinstallerArgs = [
    'main.py',
    '--onefile',
    # '--windowed',
    '--icon', join(dirname(__file__), 'res/logo.ico'),
    '--specpath', __buildDir__,
    '--distpath', __buildDir__,
    '--workpath', __buildDir__ + '/build',
    '--name', appName,  # Set the executable name.
]
# builder.py - Updated hidden imports.
# Add these to your pyinstallerArgs or spec file.
hiddenimports = [
    # Your main Qt binding:
    'PyQt5',
    'PyQt5.sip',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    # For uic loading:
    'PyQt5.uic',
    'PyQt5.uic.Loader',
    'PyQt5.uic.Compiler',
    # If using ManyQt:
    'ManyQt',
    'ManyQt.QtCore',
    'ManyQt.QtGui',
    'ManyQt.QtWidgets',
    'ManyQt.uic',
    # More libs:
    'cloudscraper',
    'nglwrapper',
    'widgets',
    'widgets.QtThemes',
    'mainwindow',
]

# Add to pyinstallerArgs.
for hi in hiddenimports:
    pyinstallerArgs.extend(['--hidden-import', hi])
# Exclude ALL other Qt bindings.
excludeModules = [
    'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'PyQt4.QtNetwork',
    'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtNetwork',
    'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtNetwork',
    'PySide', 'PySide.QtCore', 'PySide.QtGui', 'PySide.QtNetwork',
    'PySide2', 'PySide2.QtCore', 'PySide2.QtGui', 'PySide2.QtWidgets', 'PySide2.QtNetwork',
    'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtNetwork',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinter.constants',
    'tkinter.scrolledtext',
    'tkinter.dnd',
    'tkinter.commondialog',
    'tkinter.simpledialog',
    'tkinter.colorchooser',
    'tkinter.font',
    'tkinter.tix',
    '_tkinter',  # The underlying C module.
    'tk',  # Tk library binding.
    'Tkinter',  # Capitalized version (Python 2).
]  # type: list[str]
for p in excludeModules:
    if not p.lower().startswith(environ['QT_API'].lower()):
        pyinstallerArgs.extend(['--exclude-module', p])
        print('Excluding: {}'.format(p))
extra_excludes_modules = ['PyQt4.QtPrintSupport', 'PyQt5.QtPrintSupport', 'PyQt6.QtPrintSupport',
                          'PySide.QtPrintSupport', 'PySide2.QtPrintSupport', 'PySide6.QtPrintSupport',
                          'tkinter.scrolledtext',  # Add tkinter submodules if needed.
                          'tkinter.dnd', 'tkinter.commondialog']  # type: list[str]
for m in extra_excludes_modules:
    pyinstallerArgs.extend(['--exclude-module', m])
# Special excludes:
formats = ['dll', 'lib', 'so', 'dylib']  # type: list[str]
if environ['QT_API'].lower() != 'pyqt4':
    for se in ['QtCore4', 'QtGui4', 'QtOpenGL4', 'QtSvg4', 'QtXml4']:
        for f in formats:
            pyinstallerArgs.extend(['--exclude-module', '{}.{}'.format(se, f)])
# Also try to exclude via --exclude-module with .dll pattern.
for t in ['tk85', 'tcl85']:
    for f in formats:
        pyinstallerArgs.extend(['--exclude-module', '{}.{}'.format(t, f)])
# Define all resources to include.
resources = [
    # UI files.
    ('mainwindow.ui', '.'),
    # Resource directory.
    ('res', 'res'),
    # Widgets directory - include all subdirectories.
    ('widgets', 'widgets'),
]
# Process all resources.
print(u'\nAdding resources:')
resourcesList = []
for src, dst in resources:
    dataSpec = addDataFiles(src, dst)
    if dataSpec:
        pyinstallerArgs.extend(['--add-data', dataSpec])
        resourcesList.append("('{}', '{}')".format(join(dirname(__file__), src), dst))
        print(u'  Added: {} -> {}'.format(src, dst))
    else:
        print(u'  Warning: {} not found'.format(src))
# Add hooks directory if specified and exists.
if hooksPath and exists(hooksPath):
    pyinstallerArgs.extend(['--additional-hooks-dir', hooksPath])
    print(u'Using hooks from: {}'.format(hooksPath))
# Run PyInstaller with the spec file.
print('\nRunning PyInstaller...')
run(pyinstallerArgs)
# Launch App after installing.
if runApp.lower() in ['y', 'yes', '1', 'oui']:
    exePath = join(__buildDir__, appName)  # type: str
    if platform.lower() == 'win32':
        exePath += '.exe'  # type: str
    if exists(exePath):
        system(exePath)
