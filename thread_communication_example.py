from PySide2.QtCore import QObject, QThread, Signal
import time, sys, platform
from PySide2 import QtWidgets, QtCore
# Snip...
# https://realpython.com/python-pyqt-qthread/

# The Window class do two things:
# 1. the upper button: "click me" contains the functions defined in Window class itself.
# 2. the lower button "long running task" depends on another class Worker's functions. Also it is included in another
# new thread
#
# The main thread can run with the Qthread at the same time, i.e. after click lower button you can still click upper
# button and see
# the number increase
# It is better to use signal to communicate between the threads and that is how "finished" and "progress" come in.
# And we use connected function to link
# the signals to functions


# Step 1: Create a worker class
class Worker(QObject):
    finished = Signal()
    progress = Signal(int)

    def run(self):
        """Long-running task."""
        for i in range(20):
            time.sleep(1)
            self.progress.emit(i + 1)
            print(i)
        self.finished.emit()


class Window(QtWidgets.QMainWindow):
    # Snip...
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicksCount = 0
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Freezing GUI")
        self.resize(300, 150)
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        # Create and connect widgets
        self.clicksLabel = QtWidgets.QLabel("Counting: 0 clicks", self)
        self.clicksLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
        self.stepLabel =QtWidgets. QLabel("Long-Running Step: 0")
        self.stepLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
        self.countBtn = QtWidgets.QPushButton("Click me!", self)
        self.countBtn.clicked.connect(self.countClicks)
        self.longRunningBtn = QtWidgets.QPushButton("Long-Running Task!", self)
        self.longRunningBtn.clicked.connect(self.runLongTask)
        # Set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.clicksLabel)
        layout.addWidget(self.countBtn)
        layout.addStretch()
        layout.addWidget(self.stepLabel)
        layout.addWidget(self.longRunningBtn)
        self.centralWidget.setLayout(layout)

    def countClicks(self):
        self.clicksCount += 1
        self.clicksLabel.setText(f"Counting: {self.clicksCount} clicks")

    def reportProgress(self, n):
        self.stepLabel.setText(f"Long-Running Step: {n}")


    def runLongTask(self):
        """Long-running task in 5 steps."""
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.longRunningBtn.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.longRunningBtn.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.stepLabel.setText("Long-Running Step: 0")
        )


if __name__ == "__main__":

    App = QtWidgets.QApplication(sys.argv)
    MW = Window()

    if platform.system() == "Linux":
        MW.show()
        MW.showMinimized()
    else:
        MW.show()
    MW.activateWindow()

    sys.exit(App.exec_())