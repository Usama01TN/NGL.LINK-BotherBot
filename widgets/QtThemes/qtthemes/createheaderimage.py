# -*- coding: utf-8 -*-
"""
None
"""
from ManyQt.QtWidgets import QGraphicsScene, QGraphicsView, QApplication, QGraphicsDropShadowEffect, QGraphicsPixmapItem
from ManyQt.QtCore import QPointF, Qt, QRect, QRectF, QPoint, pyqtSlot, pyqtProperty
from ManyQt.QtGui import QPainterPath, QPainter, QPixmap, QColor, QImage
from os.path import realpath, join


class MaskedPixmapItem(QGraphicsPixmapItem):
    """
    MaskedPixmapItem class.
    """

    def __init__(self, *args, **kwargs):
        """
        :param pixmap: QPixmap | QImage
        :param args: args
        :param kwargs: kwargs
        """
        pixmap = kwargs.pop('pixmap', None)  # type: QPixmap | None
        subArgs = (x for x in args if not isinstance(x, (QPixmap, QImage)))
        super(MaskedPixmapItem, self).__init__(*subArgs, **kwargs)
        for arg in args:
            if isinstance(arg, (QPixmap, QImage)):
                pixmap = arg  # type: QPixmap
        self.setPixmap(pixmap)
        self.__m_pixmap = pixmap  # type: QPixmap
        self.__m_offset = 0  # type: int
        self.__m_shear = 100  # type: int
        self.__m_orientation = Qt.Orientation.Horizontal

    def paint(self, painter, option, widget=None):
        """
        :param painter: QPainter
        :param option: QStyleOptionGraphicsItem
        :param widget: QWidget | None
        :return:
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipPath(self._shearPath())
        super(MaskedPixmapItem, self).paint(painter, option, widget)

    def _shearPath(self):
        """
        :return: QPainterPath
        """
        rect = self.__m_pixmap.rect()  # type: QRect
        path = QPainterPath()  # type: QPainterPath
        if self.__m_orientation == Qt.Orientation.Horizontal:
            path.moveTo(QPointF(self.__m_offset, 0))
            path.lineTo(QPointF(self.__m_offset - self.__m_shear, rect.height()))
            path.lineTo(QPointF(rect.width(), rect.height()))
            path.lineTo(QPointF(rect.width(), 0))
        else:
            path.moveTo(QPointF(0, self.__m_offset))
            path.lineTo(QPointF(rect.width(), self.__m_offset - self.__m_shear))
            path.lineTo(QPointF(rect.width(), rect.height()))
            path.lineTo(QPointF(0, rect.height()))
        path.closeSubpath()
        return path

    @pyqtSlot(int)
    def setPixmapOffset(self, offset):
        """
        :param offset: int
        :return:
        """
        if self.__m_offset != offset:
            self.__m_offset = offset  # type: int
            self.update()

    def getPixmapOffset(self):
        """
        :return: int
        """
        return self.__m_offset

    @pyqtSlot(int)
    def setShear(self, shear):
        """
        :param shear: int
        :return:
        """
        if self.__m_shear != shear:
            self.__m_shear = shear  # type: int
            self.update()

    def getShear(self):
        """
        :return: int
        """
        return self.__m_shear

    @pyqtSlot(Qt.Orientation)
    @pyqtSlot(int)
    def setOrientation(self, orientation):
        """
        :param orientation: Qt.Orientation | int
        :return:
        """
        if isinstance(orientation, Qt.Orientation):
            orientation = Qt.Orientation(orientation)  # type: Qt.Orientation
        if self.__m_orientation != orientation:
            self.__m_orientation = orientation  # type: Qt.Orientation
            self.update()

    def getOrientation(self):
        """
        :return: Qt.Orientation
        """
        return self.__m_orientation

    pixmapOffset = pyqtProperty(int, fget=getPixmapOffset, fset=setPixmapOffset)  # type: pyqtProperty
    shear = pyqtProperty(int, fget=getShear, fset=setShear)  # type: pyqtProperty
    orientation = pyqtProperty(Qt.Orientation, fget=getOrientation, fset=setOrientation)  # type: pyqtProperty


def createHeaderImage(paths, outputPath, shadowRadius=32, shadowOffset=QPoint(0, 4)):
    """
    :param paths: list[str | unicode | QString] | QStringList
    :param outputPath: str | unicode | QString
    :param shadowRadius: int
    :param shadowOffset: QPoint
    :return:
    """
    if not paths:
        raise ValueError(u'paths cannot be empty')
    _ = QApplication([])  # type: QApplication
    # Graphics View.
    view = QGraphicsView()  # type: QGraphicsView
    view.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Graphics Scene.
    rect = QPixmap(paths[0]).rect()  # type: QPixmap
    scene = QGraphicsScene()  # type: QGraphicsScene
    sceneRect = QRect(
        int((-shadowRadius + shadowOffset.x()) / 2.0),
        int((-shadowRadius + shadowOffset.y()) / 2.0),
        rect.width() + shadowRadius,
        rect.height() + shadowRadius,
    )  # type: QRect
    scene.setSceneRect(sceneRect)
    view.setScene(scene)
    # Drop Shadow.
    dropShadow = QGraphicsDropShadowEffect()  # type: QGraphicsDropShadowEffect
    dropShadow.setOffset(shadowOffset)
    dropShadow.setBlurRadius(shadowRadius)
    dropShadow.setColor(QColor(0, 0, 0, 128))
    # Masked Images.
    for i, path in enumerate(paths):
        pixmap = QPixmap(path)  # type: QPixmap
        if i == 0:
            item = QGraphicsPixmapItem(pixmap)  # type: QGraphicsPixmapItem
            item.setGraphicsEffect(dropShadow)
        else:
            item = MaskedPixmapItem(pixmap)  # type: MaskedPixmapItem
            shear = 300  # type: int
            item.setPixmapOffset(int((pixmap.rect().width() + shear) / len(paths) * i))
            item.setShear(shear)
        scene.addItem(item)
    # Save Scene to image.
    image = QImage(sceneRect.width(), sceneRect.height(), QImage.Format.Format_ARGB32)  # type: QImage
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)  # type: QPainter
    scene.render(painter, target=QRectF(image.rect()), source=sceneRect)
    painter.end()
    image.save(outputPath)


def createThemeHeaderImage():
    """
    :return:
    """
    assetsDir = realpath('./assets')  # type: str
    paths = []  # type: list[str]
    for theme in (u'catppuccin_latte', u'one_dark_two', u'monokai', u'catppuccin_frappe', u'atom_one', u'nord'):
        paths.append(join(assetsDir, '{}.png'.format(theme)))
    createHeaderImage(paths, join(assetsDir, 'header.png'))


if __name__ == '__main__':
    createThemeHeaderImage()
