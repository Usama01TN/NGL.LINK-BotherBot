# coding=utf-8
"""
None
"""
from os.path import dirname
from os import environ
from sys import path

environ['QT_API'] = 'PyQt5'

if dirname(__file__) not in path:
    path.append(dirname(__file__))

try:
    from .mainwindow import MainWindow
except:
    from mainwindow import MainWindow

if __name__ == '__main__':
    from ManyQt.QtWidgets import QApplication
    from sys import argv, exit

    a = QApplication(argv)  # type: QApplication
    a.setQuitOnLastWindowClosed(True)
    w = MainWindow()  # type: MainWindow
    w.show()
    exit(a.exec_())
