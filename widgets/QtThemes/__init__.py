# coding=utf-8
"""
None
"""
from os.path import dirname
from sys import path

if dirname(__file__) not in path:
    path.append(dirname(__file__))

try:
    from .qtthemes.createheaderimage import MaskedPixmapItem, createThemeHeaderImage, createHeaderImage
    from .qtthemes._theme import Theme, getTheme, getThemes, setTheme, setWidgetTheme, updatePalette
except:
    from qtthemes.createheaderimage import MaskedPixmapItem, createThemeHeaderImage, createHeaderImage
    from qtthemes._theme import Theme, getTheme, getThemes, setTheme, setWidgetTheme, updatePalette

__version__ = '0.4.0'  # type: str
__all__ = [
    'MaskedPixmapItem', 'createThemeHeaderImage', 'createHeaderImage', 'Theme', 'getTheme', 'getThemes', 'setTheme',
    'setWidgetTheme', 'updatePalette', '__version__']  # type: list[str]
