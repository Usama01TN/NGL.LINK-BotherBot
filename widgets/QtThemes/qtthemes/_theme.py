# -*- coding: utf-8 -*-
"""
QtThemes module.
"""
from ManyQt.QtWidgets import QApplication, QStyleFactory
from ManyQt.QtGui import QPalette, QColor
from os.path import join, exists, splitext, dirname
from os import getenv, pathsep, listdir
from logging import getLogger
from json import load

THEMES = 'qtthemes'  # type: str
PROPERTY_NAME = 'theme'  # type: str
logger = getLogger(__package__)


class Theme(object):
    """
    Theme class.
    """

    def __init__(self, primary=None, secondary=None, magenta=None, red=None, orange=None, yellow=None, green=None,
                 cyan=None, blue=None, text=None, subtext1=None, subtext0=None, overlay2=None, overlay1=None,
                 overlay0=None, surface2=None, surface1=None, surface0=None, base=None, mantle=None, crust=None):
        """
        :param primary: QColor | None
        :param secondary: QColor | None
        :param magenta: QColor | None
        :param red: QColor | None
        :param orange: QColor | None
        :param yellow: QColor | None
        :param green: QColor | None
        :param cyan: QColor | None
        :param blue: QColor | None
        :param text: QColor | None
        :param subtext1: QColor | None
        :param subtext0: QColor | None
        :param overlay2: QColor | None
        :param overlay1: QColor | None
        :param overlay0: QColor | None
        :param surface2: QColor | None
        :param surface1: QColor | None
        :param surface0: QColor | None
        :param base: QColor | None
        :param mantle: QColor | None
        :param crust: QColor | None
        """
        self.primary = primary  # type: QColor | None
        self.secondary = secondary  # type: QColor | None
        self.magenta = magenta  # type: QColor | None
        self.red = red  # type: QColor | None
        self.orange = orange  # type: QColor | None
        self.yellow = yellow  # type: QColor | None
        self.green = green  # type: QColor | None
        self.cyan = cyan  # type: QColor | None
        self.blue = blue  # type: QColor | None
        self.text = text  # type: QColor | None
        self.subtext1 = subtext1  # type: QColor | None
        self.subtext0 = subtext0  # type: QColor | None
        self.overlay2 = overlay2  # type: QColor | None
        self.overlay1 = overlay1  # type: QColor | None
        self.overlay0 = overlay0  # type: QColor | None
        self.surface2 = surface2  # type: QColor | None
        self.surface1 = surface1  # type: QColor | None
        self.surface0 = surface0  # type: QColor | None
        self.base = base  # type: QColor | None
        self.mantle = mantle  # type: QColor | None
        self.crust = crust  # type: QColor | None

    def isDarkTheme(self):
        """
        :return: bool
        """
        return self.text.value() > self.base.value()


def getTheme(name=None):
    """
    Return the theme with `name` if found and valid.
    If no name is provided, return the current theme applied to the QApplication. This
    only works in the same Python session.
    :param name: str | unicode | QString | None
    :return: Theme | None
    """
    if name is None:
        application = QApplication.instance()  # type: QApplication
        return application.property(PROPERTY_NAME) if application else None
    fileName = '{}.json'.format(name)  # type: str
    for themesPath in _getPaths():
        path = join(themesPath, fileName)  # type: str
        if exists(path):
            break
    else:
        logger.warning('Cannot find theme {!r}.'.format(fileName))
        return None
    try:
        return _load(path)
    except TypeError:
        logger.warning('Invalid theme {!r}.'.format(path))
        return None


def getThemes():
    """
    Return all valid themes found on disk as a dictionary.
    :return: dict[str | unicode | QString, Theme]
    """
    themes = {}  # type: dict[str, Theme]
    for themesPath in _getPaths():
        if not exists(themesPath):
            continue
        for fileName in listdir(themesPath):
            name, ext = splitext(fileName)  # type: str, str
            if ext != '.json':
                continue
            path = join(themesPath, fileName)  # type: str
            try:
                themes[name] = _load(path)  # type: Theme
            except TypeError:
                logger.warning('Invalid theme {!r}.'.format(path))
                continue
    return themes


def updatePalette(palette, theme):
    """
    Set the theme for the given QPalette.
    :param palette: QPalette
    :param theme: Theme
    :return:
    """
    # Colors.
    highlightedColor = theme.primary
    highlightedTextColor = theme.mantle if highlightedColor.valueF() > 0.5 else theme.text
    h, s, v, a = theme.text.getHsvF()  # type: float, float, float, float
    brightTextColor = QColor.fromHsvF(h, s, 1 - v, a)  # type: QColor
    # Normal.
    if theme.isDarkTheme():
        palette.setColor(QPalette.Base, theme.mantle)
        palette.setColor(QPalette.AlternateBase, theme.base)
    else:
        palette.setColor(QPalette.Base, theme.crust)
        palette.setColor(QPalette.AlternateBase, theme.mantle)
    palette.setColor(QPalette.Window, theme.base)
    palette.setColor(QPalette.WindowText, theme.text)
    if hasattr(QPalette, 'PlaceholderText'):
        palette.setColor(QPalette.PlaceholderText, theme.overlay1)
    palette.setColor(QPalette.Text, theme.text)
    palette.setColor(QPalette.Button, theme.base)
    palette.setColor(QPalette.ButtonText, theme.text)
    palette.setColor(QPalette.BrightText, brightTextColor)
    palette.setColor(QPalette.ToolTipBase, theme.mantle)
    palette.setColor(QPalette.ToolTipText, theme.overlay2)
    palette.setColor(QPalette.Highlight, highlightedColor)
    palette.setColor(QPalette.HighlightedText, highlightedTextColor)
    palette.setColor(QPalette.Link, theme.secondary)
    palette.setColor(QPalette.LinkVisited, theme.secondary)
    palette.setColor(QPalette.Light, theme.crust)
    palette.setColor(QPalette.Midlight, theme.mantle)
    palette.setColor(QPalette.Mid, theme.surface0)
    palette.setColor(QPalette.Dark, theme.surface1)
    palette.setColor(QPalette.Shadow, theme.overlay0)
    # Inactive.
    palette.setColor(QPalette.Inactive, QPalette.Highlight, theme.surface1)
    palette.setColor(QPalette.Inactive, QPalette.Link, theme.surface1)
    palette.setColor(QPalette.Inactive, QPalette.LinkVisited, theme.surface1)
    # Disabled.
    palette.setColor(QPalette.Disabled, QPalette.WindowText, theme.overlay1)
    palette.setColor(QPalette.Disabled, QPalette.Base, theme.base)
    palette.setColor(QPalette.Disabled, QPalette.AlternateBase, theme.base)
    palette.setColor(QPalette.Disabled, QPalette.Text, theme.overlay1)
    if hasattr(QPalette, 'PlaceholderText'):
        palette.setColor(QPalette.Disabled, QPalette.PlaceholderText, theme.overlay1)
    palette.setColor(QPalette.Disabled, QPalette.Button, theme.base)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, theme.overlay1)
    palette.setColor(QPalette.Disabled, QPalette.BrightText, theme.mantle)
    palette.setColor(QPalette.Disabled, QPalette.Highlight, theme.surface2)
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, theme.surface0)
    palette.setColor(QPalette.Disabled, QPalette.Link, theme.surface0)
    palette.setColor(QPalette.Disabled, QPalette.LinkVisited, theme.surface0)
    try:
        # PySide2 compatibility.
        palette.setColor(QPalette.Accent, theme.secondary)
        palette.setColor(QPalette.Inactive, QPalette.Accent, theme.surface1)
        palette.setColor(QPalette.Disabled, QPalette.Accent, theme.surface2)
    except AttributeError:
        pass


def setTheme(theme, style='fusion'):
    """
    Set the theme and style for the current QApplication.
    By default, set the fusion style as it works the best with QPalette ColorRoles.
    :param theme: Theme | str | unicode | QString | None
    :param style: str | unicode | QString | None
    :return: None
    """
    # Set style
    if style:
        QApplication.setStyle(style)
    # Reset theme.
    if not theme:
        QApplication.setPalette(QPalette())
        return
    # Set theme.
    if hasattr(theme, 'encode'):
        theme = getTheme(theme)  # type: Theme | str | None
        if not theme:
            return
    palette = QPalette()  # type: QPalette
    updatePalette(palette, theme)
    QApplication.setPalette(palette)
    application = QApplication.instance()  # type: QApplication
    if application:
        application.setProperty(PROPERTY_NAME, theme)


def setWidgetTheme(widget, theme, style='fusion'):
    """
    Set the theme and style for the given QWidget.
    By default, set the fusion style as it works the best with QPalette ColorRoles.
    :param widget: QWidget
    :param theme: Theme | str | unicode | QString | None
    :param style: str | unicode | QString | None
    :return: None
    """
    # Set style.
    if style:
        widget.setStyle(QStyleFactory.create(style))
    # Reset theme.
    if not theme:
        widget.setPalette(QPalette())
        return
    # Set theme.
    if isinstance(theme, str):
        theme = getTheme(theme)  # type: Theme | str | None
        if not theme:
            return
    palette = QPalette()  # type: QPalette
    updatePalette(palette, theme)
    widget.setPalette(palette)
    widget.setProperty(PROPERTY_NAME, theme)


def _load(path):
    """
    Return the theme from `path`.
    :raises FileNotFoundError: if theme cannot be found.
    :raises TypeError: if theme has unexpected data.
    :raises JSONDecodeError: if theme is invalid JSON.
    :param path: str | unicode | QString
    :return: Theme
    """
    with open(str(path)) as f:
        data = load(f)  # type: dict[str, str]
    return Theme(**{key: QColor(value) for key, value in data.items()})


def _getPaths():
    """
    Return all paths to search for themes.
    :return: tuple[str, ...]
    """
    paths = [join(dirname(__file__), 'themes')]  # type: list[str]
    envPath = getenv(THEMES)  # type: str
    if envPath:
        paths.extend(envPath.split(pathsep))
    logger.debug(u'Color themes paths: {}'.format(paths))
    return tuple(paths)
