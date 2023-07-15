
import os, sys, time, platform, datetime, random, pickle, cgitb, traceback


from PySide2 import QtWidgets, QtCore, QtGui

import zmq

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print("ExceptType: ", exctype, "Value: ", value, "Traceback: ", traceback)
    # sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

# class OtherThread(QtCore.QThread):
#     over = QtCore.Signal(object)
#
#
#     @QtCore.Slot(object)
#     def run(self):
#         while True:
#             self.over.emit([(1,2,3), (2,3,4)])
#             time.sleep(1)
#
#
#
# class MyApp(QtCore.QObject):
#
#     def __init__(self):
#         super(MyApp, self).__init__()
#         self.thread = OtherThread(self)
#         self.thread.over.connect(self.on_over)
#         self.thread.start()
#         # self.thread.run()
#
#     @QtCore.Slot(object)
#     def on_over(self, value):
#         print ('Thread Value', value)
#
#
# if __name__ == "__main__":
#     myapp = MyApp()

################################################################
# class UpdateDisplay(QtCore.QObject):
#     signal1 = QtCore.Signal(object)
#     def __init__(self, MW, parent=None):
#         super().__init__(parent)
#         self.MW =  MW
#         self.LOOP= True
#         self.i=0
#         self.signal1.connect(self.speak)
#
#
#
#
#     @QtCore.Slot(object)
#     def run(self):
#         while self.LOOP:
#             try:
#                 self.signal1.emit([(1,2,3), (2,3,4)])
#                 print('UpdateDisplay' , self.i)
#                 self.i += 1
#                 time.sleep(1)
#             except:
#                 (type, value, traceback) = sys.exc_info()
#                 exception_hook(type, value, traceback)
#
#     @QtCore.Slot(object)
#     def speak(self, word):
#         print(word)
#
#
# class UpdateClient(QtCore.QObject):
#     signal2 = QtCore.Signal(object)
#     def __init__(self, MW, UD, parent=None):
#         super().__init__(parent)
#         self.MW =  MW
#         self.j = 1
#
#         self.UD = UD
#
#
#     @QtCore.Slot(object)
#     def run(self):
#         while True:
#             self.signal2.emit([(1,2,3), (2,3,4)])
#             print('UpClinet', self.j)
#             self.j += 1
#             time.sleep(1)
#
#     @QtCore.Slot(object)
#     def speak(self, word):
#         print(word)
#
#
#
#
#
# class MyApp(QtCore.QObject):
#
#     def __init__(self):
#         super(MyApp, self).__init__()
#         self.StartUpdater()
#
#     def StartUpdater(self):
#         try:
#             # Open connection to both PLCs
#             # self.PLC = PLC()
#
#             # Read PLC value on another thread
#             # self.PLCUpdateThread = QtCore.QThread()
#             # self.UpPLC = UpdatePLC(self.PLC)
#             # self.UpPLC.moveToThread(self.PLCUpdateThread)
#             # self.PLCUpdateThread.started.connect(self.UpPLC.run)
#             # self.PLCUpdateThread.start()
#
#             # Update display values on another thread
#             # self.testup = UpdateDisplay(self)
#             # # self.testuc = UpdateClient(self, self.testup)
#             # self.testup.signal1.connect(self.testup.speak)
#             # self.testup.run()
#
#             self.DUpdateThread = QtCore.QThread()
#             self.DUpdateThread.start()
#             self.UpDisplay = UpdateDisplay(self)
#
#
#
#             self.UpDisplay.moveToThread(self.DUpdateThread)
#
#             for i in range(10):
#                 self.UpDisplay.signal1.emit('this')
#                 time.sleep(1)
#                 print('outloop')
#             # self.DUpdateThread.started.connect(self.UpDisplay.run)
#
#
#             # Make sure PLCs values are initialized before trying to access them with update function
#             time.sleep(2)
#
#             # self.ClientUpdateThread = QtCore.QThread()
#             # self.UpClient = UpdateClient(self, self.UpDisplay)
#             # self.UpClient.moveToThread(self.ClientUpdateThread)
#             # self.ClientUpdateThread.started.connect(self.UpClient.run)
#             # self.ClientUpdateThread.start()
#
#
#
#
#         except:
#             (type, value, traceback) = sys.exc_info()
#             exception_hook(type, value, traceback)
#
#     # Stop all updater threads
#     @QtCore.Slot()
#     def StopUpdater(self):
#         # self.UpPLC.stop()
#         # self.PLCUpdateThread.quit()
#         # self.PLCUpdateThread.wait()
#         self.UpClient.stop()
#         self.ClientUpdateThread.quit()
#         self.ClientUpdateThread.wait()
#
#         self.UpDisplay.stop()
#         self.DUpdateThread.quit()
#         self.DUpdateThread.wait()
#     # signal connections to write settings to PLC codes
#
# if __name__ == "__main__":
#     myapp = MyApp()



# ####################################################
# class GenericWorker(QtCore.QObject):
#     send = QtCore.Signal(object)
#     # def __init__(self, function, *args, **kwargs):
#     def __init__(self):
#         super(GenericWorker, self).__init__()
#         self.i = 0
#
#         # self.function = function
#         # self.args = args
#         # self.kwargs = kwargs
#         # self.start.connect(self.run)
#
#
#
#     # start = QtCore.Signal(str)
#
#
#     # @QtCore.Slot(str)
#     # def run(self, some_string_arg):
#     #     # self.function(*self.args, **self.kwargs)
#     #     print(some_string_arg)
#
#     def run(self):
#         for i in range(5):
#             self.i += 1
#             self.send.emit(self.i)
#             print(self.i)
#             time.sleep(1)
#
#
#
#     # self.function(*self.args, **self.kwargs)
#
#
#
#
#
# class Window(QtWidgets.QMainWindow):
#     # Snip...
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.clicksCount = 0
#         self.setupUi()
#
#     def setupUi(self):
#         self.my_thread = QtCore.QThread()
#
#
#         # This causes my_worker.run() to eventually execute in my_thread:
#         self.my_worker = GenericWorker()
#         self.my_worker.moveToThread(self.my_thread)
#         self.my_thread.started.connect(self.my_worker.run)
#         # self.my_worker.send.connect(self.report)
#         self.my_thread.start()
#         # self.my_worker.start.emit("hello")
#
#     def report(self,content):
#         print(content)
#
#
#
#
# if __name__ == "__main__":
#
#
#
#     App = QtWidgets.QApplication(sys.argv)
#
#     MW = Window()
#
#     # MW = HeaterSubWindow()
#     # recover data
#     # MW.Recover()
#     if platform.system() == "Linux":
#         MW.show()
#         MW.showMinimized()
#     else:
#         MW.show()
#     MW.activateWindow()
#     # save data
#
#     sys.exit(App.exec_())

########################################################
class GenericWorker(QtCore.QObject):
    start = QtCore.Signal(object)
    # def __init__(self):

        # super(GenericWorker, self).__init__()

    @QtCore.Slot(object)
    def run(self, some_string_arg):
        print("yes")
        # for i in range(5):
        #
        #     print(some_string_arg)



# class Window(QtWidgets.QMainWindow):
class Window(QtWidgets.QWidget):
    # Snip...
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicksCount = 0
        self.j = 0
        self.setupUi()
        # print("begin")


    def setupUi(self):
        self.my_thread = QtCore.QThread()

        # This causes self.self.my_worker.run() to eventually execute in self.my_thread:
        self.my_worker = GenericWorker()
        self.my_worker.moveToThread(self.my_thread)
        # self.my_thread.started.connect(self.my_worker.run)

        # self.my_thread.start()

        self.my_worker.start.connect(self.my_worker.run)
        # self.my_worker.start.connect(self.report)
        try:
            while True:
                self.my_worker.start.emit({1:5})
                time.sleep(2)
                print(self.j)
                self.j += 1
                if self.j == 5:
                    raise Exception('Not connected to PLC')

        except Exception as e:
            print("mail failed to send")
            print(e)


    def report(self,content):
        print("OI")
        # for i in range(5):
        #     print(content)




if __name__ == "__main__":



    App = QtWidgets.QApplication(sys.argv)

    MW = Window()

    # MW = HeaterSubWindow()
    # recover data
    # MW.Recover()
    if platform.system() == "Linux":
        MW.show()
        MW.showMinimized()
    else:
        MW.show()
    MW.activateWindow()
    # save data

    sys.exit(App.exec_())



