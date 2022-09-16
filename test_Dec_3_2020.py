from PySide2 import QtCore, QtGui, QtWidgets


class TabWindow(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(TabWindow, self).__init__(parent)
        self.initTabs()

    def initTabs(self):
        self.test1 = self.addTab(QtWidgets.QWidget(), "Test 1")
        self.test2 = self.addTab(QtWidgets.QWidget(),"Test 2")
        self.test3 = self.addTab(QtWidgets.QWidget(),"Test 3")
        self.test4 = self.addTab(QtWidgets.QWidget(),"Test 4")

    def resizeEvent(self, event):
        self.tabBar().setFixedWidth(self.width())
        super(TabWindow, self).resizeEvent(event)


class MainApplication(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainApplication, self).__init__(parent)
        self.mainWidget = TabWindow()
        self.setCentralWidget(self.mainWidget)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_app = MainApplication()
    main_app.resize(640, 480)
    main_app.show()
    sys.exit(app.exec_())