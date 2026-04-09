# -*- coding: utf-8 -*-
"""
Nuitka project builder.
"""
# Import builder requirements.
from os.path import join, dirname, exists, isdir, basename
from sys import version_info, platform, executable
from os import system, path, environ
from subprocess import call
from pip import _internal

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
buildDir = appName + '_' + pyVers + '_' + environ['QT_API'] + '_Nuitka'  # type: str
hooksPath = join(dirname(__file__), 'hooks')  # type: str
try:
    runApp = input('Open App (Y/N): ')
except NameError as wrd:
    runApp = str(wrd).split("'")[1]


# Function to add data files/directories correctly for Nuitka.
def addDataFiles(sourceDir, targetDir=None):
    """
    Add a directory or file to Nuitka's includes.
    :param sourceDir: (str | unicode) Source directory.
    :param targetDir: (str | unicode) Target directory.
    :return: str | unicode | None
    """
    if targetDir is None:
        targetDir = sourceDir
    sourcePath = join(dirname(__file__), sourceDir)
    if path.exists(sourcePath):
        if isdir(sourcePath):
            # Nuitka directory inclusion
            return '--include-data-dir={}={}'.format(sourcePath, targetDir)
        else:
            # Nuitka file inclusion (target requires the exact filename, not just the directory)
            if targetDir == '.':
                targetFile = basename(sourcePath)
            else:
                targetFile = join(targetDir, basename(sourcePath)).replace('\\', '/')
            return '--include-data-file={}={}'.format(sourcePath, targetFile)
    return None


# Workspace:
# Install app requirements.
if insReq.lower() in ['y', 'yes', '1', 'oui']:
    reqFile = 'requirements.txt' if exists('requirements.txt') else join(dirname(__file__), 'requirements.txt')
    if exists(reqFile):
        with open(reqFile, 'r') as fileObj:
            for reqLine in fileObj.readlines():
                _internal.main(['install', reqLine.strip()])
# Start app builder for Nuitka.
nuitkaArgs = [
    executable, '-m', 'nuitka',
    '--enable-plugin={}'.format(environ['QT_API'].lower()),  # Nuitka specific plugin.
    # Tell the plugin exactly which Qt modules to include.
    # Only list what you actually use (usually just core, gui, and widgets).
    '--include-qt-plugins=platforms,styles',
    # Specifically tell the plugin to exclude the ones you found.
    # '--noinclude-qt-plugins=multimedia,qml,quick,netrk,websockets,dbus,printsupport',
    '--include-package-data=cloudscraper',
    '--include-package-data=certifi',  # Add this to ensure SSL certificates are bundled.
    '--include-package-data=cryptography',
    '--onefile',
    # '--mode=standalone',
    # '--disable-console',
    '--output-dir={}'.format(buildDir),
]
# Set platform-specific icon flag AND output app name.
iconPath = join(dirname(__file__), 'res', 'logo.ico')  # type:str
if platform.lower() == 'win32':
    nuitkaArgs.append('--windows-icon-from-ico={}'.format(iconPath))
    nuitkaArgs.append('--output-filename={}.exe'.format(appName))
elif platform.lower() == 'darwin':
    nuitkaArgs.append('--macos-app-icon={}'.format(iconPath))
    # If using --macos-create-app-bundle later, change this to --macos-app-name:
    nuitkaArgs.append('--output-filename={}'.format(appName))
else:
    nuitkaArgs.append('--linux-icon={}'.format(iconPath))
    nuitkaArgs.append('--output-filename={}'.format(appName))
# Hidden imports conversion.
# hiddenImports = [
#     # Your main Qt binding:
#     # 'PyQt5', 'PyQt5.sip', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
#     # For uic loading:
#     # 'PyQt5.uic', 'PyQt5.uic.Loader', 'PyQt5.uic.Compiler',
#     # If using ManyQt:
#     # 'ManyQt', 'ManyQt.QtCore', 'ManyQt.QtGui', 'ManyQt.QtWidgets', 'ManyQt.uic',
#     # More libs:
#     'cloudscraper', 'nglwrapper', 'widgets', 'widgets.QtThemes', 'mainwindow',
# ]
# Add forced modules to nuitkaArgs.
# for hiddenImport in hiddenImports:
#     nuitkaArgs.append('--include-module=' + hiddenImport)
# Exclude ALL other Qt bindings.
excludeModules = [
    'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'PyQt4.QtNetwork',
    'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtNetwork',
    'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtNetwork',
    'PySide', 'PySide.QtCore', 'PySide.QtGui', 'PySide.QtNetwork',
    'PySide2', 'PySide2.QtCore', 'PySide2.QtGui', 'PySide2.QtWidgets', 'PySide2.QtNetwork',
    'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtNetwork',
    'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog',
    'tkinter.constants', 'tkinter.scrolledtext', 'tkinter.dnd', 'tkinter.commondialog',
    'tkinter.simpledialog', 'tkinter.colorchooser', 'tkinter.font', 'tkinter.tix',
    '_tkinter', 'tk', 'Tkinter'
]  # type: list[str]
for p in excludeModules:
    if not p.lower().startswith(environ['QT_API'].lower()):
        nuitkaArgs.append('--nofollow-import-to=' + p)
        print('Excluding: {}'.format(p))
extraExcludesModules = [
    'PyQt4.QtPrintSupport', 'PyQt5.QtPrintSupport', 'PyQt6.QtPrintSupport', 'PySide.QtPrintSupport',
    'PySide2.QtPrintSupport', 'PySide6.QtPrintSupport', 'tkinter.scrolledtext', 'tkinter.dnd', 'tkinter.commondialog',
    'qt5multimedia', 'qt5qmlmodels', 'qt5quick', 'qt5network', 'qt5websockets', 'qt5dbus', 'qt5printsupport'
]  # type: list[str]
for m in extraExcludesModules:
    nuitkaArgs.append('--nofollow-import-to=' + m)
# Special excludes:
formats = ['dll', 'lib', 'so', 'dylib']  # type: list[str]
if environ['QT_API'].lower() != 'pyqt4':
    for se in ['QtCore4', 'QtGui4', 'QtOpenGL4', 'QtSvg4', 'QtXml4']:
        for f in formats:
            nuitkaArgs.append('--nofollow-import-to={}.{}'.format(se, f))
# Also try to exclude via nofollow pattern.
for t in ['tk85', 'tcl85']:
    for f in formats:
        nuitkaArgs.append('--nofollow-import-to={}.{}'.format(t, f))
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
        nuitkaArgs.append(dataSpec)
        resourcesList.append("('{}', '{}')".format(join(dirname(__file__), src), dst))
        print(u'  Added: {} -> {}'.format(src, dst))
    else:
        print(u'  Warning: {} not found'.format(src))
nuitkaArgs.append('main.py')
# Run Nuitka compilation.
print('\nRunning Nuitka...')
call(nuitkaArgs)
# Launch App after installing.
if runApp.lower() in ['y', 'yes', '1', 'oui']:
    exePathWin = join(buildDir, appName + '.exe')
    exePathBin = join(buildDir, appName + '.bin')
    exePathMac = join(buildDir, appName)
    if platform.lower() == 'win32' and exists(exePathWin):
        system(exePathWin)
    elif exists(exePathBin):
        system('./' + exePathBin)
    elif exists(exePathMac):
        system('./' + exePathMac)
