# -*- coding: utf-8 -*-
"""
None
"""
from ManyQt.QtWidgets import QFileDialog, QMainWindow, QMessageBox
from ManyQt.QtCore import pyqtSlot, QTimer
from ManyQt.QtGui import QIcon
from ManyQt.uic import loadUi
from os.path import exists, dirname, join
from threading import Lock, Thread, Event
from traceback import print_exc
from sys import exit, path
from time import sleep

if dirname(__file__) not in path:
    path.append(dirname(__file__))

try:
    from .widgets.QtThemes import setTheme, getThemes
    from .nglwrapper import NGLWrapper
except:
    from widgets.QtThemes import setTheme, getThemes
    from nglwrapper import NGLWrapper


class MainWindow(QMainWindow):
    """
    MainWindow class.
    """
    __m_ui = None
    __m_stopEvent = None  # type: Event | None

    def __init__(self, *args, **kwargs):
        """
        :param args: any
        :param kwargs: any
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        self.__m_ui = loadUi(join(dirname(__file__), 'mainwindow.ui'))
        self.setWindowIcon(QIcon('res/logo.png' if exists('res/logo.png') else join(dirname(__file__), 'res/logo.png')))
        self.setWindowTitle(self.__m_ui.windowTitle())
        self.resize(self.__m_ui.size())
        self.setCentralWidget(self.__m_ui)
        if hasattr(self.__m_ui, 'setupUi'):
            self.__m_ui.setupUi(self)
        # Set default values.
        self.__m_ui.timeDblSpinBox.setValue(0.20)
        self.__m_ui.threadSpinBox.setValue(40)
        # Set widgets text.
        self.__m_ui.threadsNumLab.setText('0/{}'.format(self.__m_ui.threadSpinBox.value()))
        # Default variables.
        self.__m_totalSent = 0  # type: int
        self.__m_totalError = 0  # type: int
        self.__m_totalThreads = 0  # type: int
        self.__m_usersDict = {'Good': {}, 'Bad': {}}
        self.__m_lock = Lock()  # type: Lock
        self.__m_stopEvent = Event()  # type: Event # Event to signal threads to stop.
        self.__m_activeThreads = []  # type: list[Thread] # Keep track of active threads.
        # Connect widgets with events.
        self.__m_ui.loadLstBtn.clicked.connect(self.onLoadListFile)
        self.__m_ui.threadSpinBox.valueChanged.connect(self.onThreadChanged)
        self.__m_ui.usrLstLineBox.textChanged.connect(self.onLoadList)
        self.__m_ui.startBtn.clicked.connect(self.onStart)
        self.__m_ui.cancelBtn.clicked.connect(exit)
        self.__m_logTimer = QTimer()  # type: QTimer
        self.__m_logTimer.timeout.connect(self.updateLogs)
        # Set default style.
        setTheme('catppuccin_macchiato', style='fusion')

    @pyqtSlot(int)
    def onThreadChanged(self, value):
        """
        :param value: int
        :return:
        """
        # Extract the current active threads count from the label.
        self.__m_ui.threadsNumLab.setText('{}/{}'.format(self.__m_ui.threadsNumLab.text().split('/')[0], value))

    def nglBother(self, vicName, msg='You have been hacked!', timeout=0):
        """
        :param vicName: str | unicode | QString
        :param msg: str | unicode | QString
        :param timeout: int
        :return: None
        """
        if msg == '':
            print(self.tr('Empty message box!, please enter any message!'))
            return
        if vicName in self.__m_usersDict['Bad']:
            print(self.tr('User already marked as invalid: {}').format(vicName))
            return
        try:
            session = NGLWrapper(vicName, timeout)  # type: NGLWrapper
            if not session.isValidUser():
                with self.__m_lock:
                    print(self.tr('Could not find user: {}').format(vicName))
                    self.__m_usersDict['Bad'][vicName] = self.__m_usersDict['Bad'].get(
                        vicName, 0) + 1  # type: int
                    self.__m_totalError += 1  # type: int
            else:
                session.sendQuestion(msg)
                with self.__m_lock:
                    print(self.tr('Message sent to: {}').format(vicName))
                    self.__m_usersDict['Good'][vicName] = self.__m_usersDict['Good'].get(vicName, 0) + 1  # type: int
                    self.__m_totalSent += 1  # type: int
        except Exception as e:
            with self.__m_lock:
                print(self.tr('Connection error: {}').format(str(e)))
                self.__m_totalError += 1  # type: int
        finally:
            del session  # <-- Explicitly release session resources.

    def bothNow(self, vicName, msg, msgNums, sndTime, timeout=0):
        """
        :param vicName: str | unicode | QString
        :param msg: str | unicode | QString
        :param msgNums: int
        :param sndTime: float | int
        :param timeout: int
        :return: None
        """
        if not self.__m_stopEvent:
            return
        with self.__m_lock:
            self.__m_totalThreads += 1  # type: int
        try:
            if self.__m_ui.msgNumChBox.isChecked():
                for x in range(msgNums):
                    # Check if we should stop.
                    if self.__m_stopEvent.is_set() or self.__m_ui.startBtn.text().lower() == self.tr(u'start'):
                        break
                    self.nglBother(vicName, msg, timeout)
                    sleep(sndTime)
                    if self.__m_stopEvent.is_set() or self.__m_ui.startBtn.text().lower() == self.tr(u'start'):
                        break
            else:
                # For continuous sending, use a while loop with stop condition.
                while not self.__m_stopEvent.is_set() and self.__m_ui.startBtn.text().lower() == self.tr(u'stop'):
                    users = vicName.strip().split('\n')  # type: list[str]
                    for usr in users:
                        if self.__m_stopEvent.is_set() or self.__m_ui.startBtn.text().lower() == self.tr(u'start'):
                            break
                        if usr.strip():  # Skip empty lines.
                            self.nglBother(usr.strip(), msg, timeout)
                        sleep(sndTime)
                    sleep(sndTime)
        except Exception as e:
            print(self.tr('Error in thread: {}').format(e))
            print_exc()
        finally:
            with self.__m_lock:
                self.__m_totalThreads -= 1  # type: int

    # @pyqtSlot()
    def beginBother(self):
        """
        :return: None
        """
        if not self.__m_ui or not self.__m_stopEvent:
            return
        self.__m_activeThreads = []  # type: list[Thread] # Clear the list of active threads.
        try:
            if self.__m_ui.msgNumChBox.isChecked():
                # Send a specific number of messages to each user.
                for usr in self.__m_ui.lstEditBox.toPlainText().strip().split('\n'):
                    if not usr.strip():  # Skip empty lines.
                        continue
                    # Wait if we've reached the thread limit.
                    # Replace the while-wait block:
                    while self.__m_totalThreads >= self.__m_ui.threadSpinBox.value() and \
                            not self.__m_stopEvent.is_set():
                        sleep(0.1)
                        # Prune finished threads to free memory.
                        self.__m_activeThreads = [t for t in self.__m_activeThreads if t.is_alive()]  # type: list[Thread]
                    if self.__m_stopEvent.is_set():
                        break
                    botThr = Thread(target=self.bothNow, args=(
                        usr.strip(),
                        self.__m_ui.msgEditBox.toPlainText(),
                        self.__m_ui.msgNumSpinBox.value(),
                        self.__m_ui.timeDblSpinBox.value(),
                        self.__m_ui.timeOutSpinBox.value() if self.__m_ui.timeOutSpinBox.isEnabled() else 0))
                    botThr.daemon = True
                    botThr.start()
                    self.__m_activeThreads.append(botThr)
            else:
                # Create multiple threads for continuous sending.
                for thr in range(self.__m_ui.threadSpinBox.value()):
                    if self.__m_stopEvent.is_set():
                        break
                    botThr = Thread(target=self.bothNow, args=(
                        self.__m_ui.lstEditBox.toPlainText(),
                        self.__m_ui.msgEditBox.toPlainText(), None,
                        self.__m_ui.timeDblSpinBox.value(),
                        self.__m_ui.timeOutSpinBox.value() if self.__m_ui.timeOutSpinBox.isEnabled() else 0))
                    botThr.daemon = True
                    botThr.start()
                    self.__m_activeThreads.append(botThr)
            # NEW (waits until each thread actually finishes):
            for thread in self.__m_activeThreads:
                while thread.is_alive():
                    thread.join(timeout=0.5)
                    if self.__m_stopEvent.is_set():
                        break
        except Exception as e:
            print(self.tr('Error in beginBother: {}').format(e))
        finally:
            for thread in self.__m_activeThreads:
                while thread.is_alive():
                    thread.join(timeout=0.5)
                    if self.__m_stopEvent.is_set():
                        break
            if hasattr(self.__m_activeThreads, 'clear'):
                self.__m_activeThreads.clear()
            else:
                self.__m_activeThreads = []  # type: list[Thread]
            self.__m_ui.startBtn.setText(self.tr(u'Start'))
            self.__m_ui.startBtn.setEnabled(True)
            self.__m_stopEvent.clear()
            self.__m_logTimer.stop()

    @pyqtSlot()
    def onLoadListFile(self):
        """
        :return:
        """
        localPathFile = QFileDialog.getOpenFileName(self, self.tr('Load text file'), '', self.tr('Any text File (*)'))
        if isinstance(localPathFile, tuple):
            localPathFile = localPathFile[0]
        if localPathFile != '':
            if exists(localPathFile):
                self.__m_ui.usrLstLineBox.setText(localPathFile)

    @pyqtSlot('QString')
    @pyqtSlot(str)
    def onLoadList(self, t):
        """
        :param t: str | unicode | QString
        :return:
        """
        if exists(self.__m_ui.usrLstLineBox.text()):
            try:
                with open(self.__m_ui.usrLstLineBox.text(), 'r', encoding='utf-8') as f:
                    self.__m_ui.lstEditBox.setText(f.read())
            except Exception as e:
                print(self.tr('Error loading file: {}').format(e))

    @pyqtSlot()
    def onLogTextEvent(self):
        """
        :return: None
        """
        if not self.__m_stopEvent:
            return
        try:
            while not self.__m_stopEvent.is_set() and (
                    self.__m_ui.startBtn.text().lower() == self.tr(u'stop') or self.__m_totalThreads > 0):
                sleep(0.50)
        except Exception as e:
            print(self.tr('Error in log thread: {}').format(e))

    def generateLogText(self):
        """
        Generate the log text from current user dictionaries
        :return: str | unicode | QString
        """
        textLog = 'Total valid users: {}\n'.format(len(self.__m_usersDict['Good']))  # type: str
        for x in self.__m_usersDict['Good']:
            textLog += x + ': {}\n'.format(self.__m_usersDict['Good'][x])  # type: str
        textLog += '---------------------------\nTotal invalid users: {}\n'.format(len(self.__m_usersDict['Bad']))
        for x in self.__m_usersDict['Bad']:
            textLog += x + ': {}\n'.format(self.__m_usersDict['Bad'][x])  # type: str
        return textLog

    # @pyqtSlot()
    def onStart(self):
        """
        :return: None
        """
        if not self.__m_ui:
            return
        if self.__m_ui.msgEditBox.toPlainText() == '':
            errMessage = QMessageBox()  # type: QMessageBox
            errMessage.setWindowTitle(self.tr('Error'))
            errMessage.setText(self.tr('Empty message box!, please enter any message!'))
            errMessage.exec_()
            return
        if self.__m_ui.startBtn.text().lower() == self.tr(u'start'):
            # Reset everything for a new run.
            self.__m_stopEvent.clear()  # Clear any existing stop event.
            self.__m_totalSent = 0  # type: int
            self.__m_totalError = 0  # type: int
            self.__m_totalThreads = 0  # type: int
            self.__m_usersDict = {'Good': {}, 'Bad': {}}
            self.__m_ui.startBtn.setText(self.tr(u'Stop'))
            # Start log thread.
            logThr = Thread(target=self.onLogTextEvent)  # type: Thread
            logThr.daemon = True
            logThr.start()
            # Start main processing thread.
            begThr = Thread(target=self.beginBother)  # type: Thread
            begThr.daemon = True
            begThr.start()
            self.__m_logTimer.start(1000)
        else:
            # Stop the process.
            self.__m_ui.startBtn.setText(self.tr('Starting stop...'))
            self.__m_ui.startBtn.setEnabled(False)
            self.__m_stopEvent.set()  # Signal all threads to stop.
            # The button will be re-enabled in beginBother when all threads are done.

    @pyqtSlot()
    def updateLogs(self):
        """
        :return:
        """
        if self.__m_ui:
            self.__m_ui.logEditBox.setText(self.generateLogText())
            self.__m_ui.totalErrorNumLab.setText(str(self.__m_totalError))
            self.__m_ui.totalNumLab.setText(str(self.__m_totalSent))
            self.__m_ui.threadsNumLab.setText('{}/{}'.format(self.__m_totalThreads, self.__m_ui.threadSpinBox.value()))
