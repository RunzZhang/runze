import datetime
import random
import time
from PySide2 import QtCore

class main():
    def __init__(self):

        # print("Hello")
        self.startupdate()
    def startupdate(self):
        self.P=fake_P()
        self.T=fake_T()
        # print("Nice")

        # Read PPLC value on another thread
        self.PUpdateThread = QtCore.QThread()
        self.UpPPLC = update_P(self.P)
        self.UpPPLC.moveToThread(self.PUpdateThread)
        self.PUpdateThread.started.connect(self.UpPPLC.run)
        self.PUpdateThread.start()


        print("Is UpPPLC running?",self.UpPPLC.Running)
        print("Is UpPPLCThread　started?",self.PUpdateThread.started.emit())
        print("Is UpPPLCThread running?",self.PUpdateThread.isRunning())
        print("Is UpPPLCThread finished?", self.PUpdateThread.isFinished())

        # Read TPLC value on another thread
        self.TUpdateThread = QtCore.QThread()
        self.UpTPLC = update_T(self.T)
        self.UpTPLC.moveToThread(self.TUpdateThread)
        self.TUpdateThread.started.connect(self.UpTPLC.run)
        self.TUpdateThread.start()

        # print("UpTPLC is running", self.UpTPLC.Running)
        # print("TPLC is running",self.TUpdateThread.isRunning())

class update_P(QtCore.QObject):
    def __init__(self,P,parent=None):
        super().__init__(parent)
        self.P=P
        self.Running=False
        # print("GOOD PPLC?")
        # while 1:
        #     print("PPLC updating", datetime.datetime.now())
        #     self.P.read()
        #     time.sleep(2)

    @QtCore.Slot()
    def run(self):
        self.Running=True
        while self.Running:
            print("PPLC updating", datetime.datetime.now())
            self.P.read()
            time.sleep(2)

    @QtCore.Slot()
    def stop(self):
        self.Running = False


class fake_P():
    def __init__(self):
        self.PT=0
    def read(self):
        print("fake P", random.randint(0,10))

class update_T(QtCore.QObject):
    def __init__(self, T,parent=None):
        super().__init__(parent)
        self.T = T
        self.Running = False

    @QtCore.Slot()
    def run(self):
        self.Running = True
        while self.Running:
            print("TPLC updating", datetime.datetime.now())
            self.T.read()
            time.sleep(2)

    @QtCore.Slot()
    def stop(self):
        self.Running = False


class fake_T():
    def __init__(self):
        self.RTD = 0
    def read(self):
        print("fake T",random.randint(10, 20))

if __name__=="__main__":
    main=main()