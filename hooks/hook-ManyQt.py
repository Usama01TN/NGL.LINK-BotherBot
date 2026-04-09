# coding=utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2024, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
# Determine which Qt binding is being used.
from os import environ

try:
    from PyInstaller.utils.hooks.qt import exclude_extraneous_qt_bindings
except:
    # Custom implementation of exclude_extraneous_qt_bindings for older PyInstaller versions.
    def exclude_extraneous_qt_bindings(hook_name, qt_bindings_order=None):
        """
        Custom implementation of exclude_extraneous_qt_bindings for PyInstaller versions
        that don't have this function (e.g., 3.6 and below).
        Args:
            hook_name: Name of the hook (for logging)
            qt_bindings_order: List of Qt bindings in order of preference

        Returns:
            List of module names to exclude
        """
        # All known Qt bindings
        allQtBindings = ['PyQt4', 'PyQt5', 'PyQt6', 'PySide', 'PySide2', 'PySide6']
        # If no order specified, use default preference.
        if qt_bindings_order is None:
            qt_bindings_order = ['PyQt5', 'PySide2', 'PyQt6', 'PySide6', 'PyQt4', 'PySide']
        # Find which bindings are actually installed.
        installedBindings = []
        for binding in allQtBindings:
            if find_spec(binding):
                installedBindings.append(binding)
        print('ManyQt hook: Installed Qt bindings: {}'.format(installedBindings))
        # If only one binding is installed, exclude all others.
        if len(installedBindings) == 1:
            toExclude = [b for b in allQtBindings if b != installedBindings[0]]
            print('ManyQt hook: Single binding found, excluding: {}'.format(toExclude))
            return toExclude
        # If multiple bindings installed, prefer the first one in qt_bindings_order.
        if installedBindings:
            # Find the highest priority binding that's installed.
            preferred = None
            for binding in qt_bindings_order:
                if binding in installedBindings:
                    preferred = binding
                    break
            if preferred:
                toExclude = [b for b in installedBindings if b != preferred]
                print('ManyQt hook: Multiple bindings found, preferring {} and excluding: {}'.format(
                    preferred, toExclude))
                return toExclude
        # Fallback: exclude all bindings except the most common (PyQt5 for Python 2.7)
        print('ManyQt hook: No clear preference, defaulting to keep PyQt5')
        return [b for b in allQtBindings if b.lower() != environ['QT_API'].lower()]

try:
    from importlib.util import find_spec
except:
    from pkgutil import iter_modules


    def find_spec(moduleName):
        """
        :param moduleName: str | unicode
        :return: bool
        """
        return moduleName in {name for loader, name, isPkg in iter_modules()}


# Detect the active Qt binding.
def getActiveQtBinding():
    """
    Detect which Qt binding is actually available in the environment.
    :return: (str | unicode | None) Qt binding or None.
    """
    # Check in order of preference (adjust as needed)
    if 'QT_API' in environ and environ['QT_API']:
        return environ['QT_API']
    for b in ['PyQt4', 'PyQt5', 'PyQt6', 'PySide', 'PySide2', 'PySide6']:
        if find_spec(b):
            return b
    return None


# Get the active Qt binding.
activeBinding = getActiveQtBinding()  # type: str | None
print('ManyQt hook: Active Qt binding detected: {}'.format(activeBinding))
# Exclude all Qt bindings except the active one.
excludedimports = []  # type: list[str]
if activeBinding:
    # Exclude all other Qt bindings.
    for binding in ['PyQt4', 'PyQt5', 'PyQt6', 'PySide', 'PySide2', 'PySide6']:
        if binding.lower() != activeBinding.lower() and (find_spec(binding)):
            excludedimports.append(binding)
            print('ManyQt hook: Excluding {}'.format(binding))
# Alternative: Use the helper function with custom order.
# This will automatically exclude extraneous bindings based on your preference.
excludedimports = exclude_extraneous_qt_bindings(
    hook_name='hook-ManyQt', qt_bindings_order=[activeBinding] + excludedimports)
print('ManyQt hook: Final excluded imports: {}'.format(excludedimports))
