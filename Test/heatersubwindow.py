from PySide2 import QtWidgets, QtCore, QtGui
import os, sys, time, platform
R=1
LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 6px; font-family: \"Calibri\"; " \
              "font-size: 12px; font-weight: bold;"
TITLE_STYLE = "background-color: rgb(204,204,204); border-radius: 10px; font-family: \"Calibri\";" \
              " font-size: 14px; font-weight: bold;"
BORDER_STYLE = " border-radius: 2px; border-color: black;"

class HeaterSubWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(1200*R, 600*R)
        self.setMinimumSize(1200*R, 600*R)
        self.setWindowTitle("Detailed Information")

        # self.Widget = QtWidgets.QWidget()
        # self.Widget.setGeometry(QtCore.QRect(0*R, 0*R, 1200*R, 600*R))

        self.VL = QtWidgets.QVBoxLayout(self)
        self.VL.setContentsMargins(0 * R, 0 * R, 0 * R, 0 * R)
        self.VL.setAlignment(QtCore.Qt.AlignCenter)
        self.VL.setSpacing(5 * R)
        # self.Widget.setLayout(self.VL)

        self.HL1 = QtWidgets.QHBoxLayout()
        self.HL1.setContentsMargins(0 * R, 0 * R, 0 * R, 0 * R)
        self.HL1.setAlignment(QtCore.Qt.AlignCenter)
        self.HL1.setSpacing(5 * R)

        self.HL2 = QtWidgets.QHBoxLayout()
        self.HL2.setContentsMargins(0 * R, 0 * R, 0 * R, 0 * R)
        self.HL2.setAlignment(QtCore.Qt.AlignCenter)
        self.HL2.setSpacing(5 * R)

        self.HL3 = QtWidgets.QHBoxLayout()
        self.HL3.setContentsMargins(0 * R, 0 * R, 0 * R, 0 * R)
        self.HL3.setAlignment(QtCore.Qt.AlignCenter)
        self.HL3.setSpacing(5 * R)

        self.VL.addLayout(self.HL1)
        self.VL.addLayout(self.HL2)
        self.VL.addLayout(self.HL3)

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setMinimumSize(QtCore.QSize(10 * R, 10 * R))
        self.Label.setStyleSheet("QLabel {" + TITLE_STYLE + BORDER_STYLE + "}")
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setGeometry(QtCore.QRect(0 * R, 0 * R, 40 * R, 140 * R))
        self.Label.setText("Write")
        self.HL1.addWidget(self.Label)

        self.FBSwitch = Menu(self)
        self.FBSwitch.Label.setText("FBSWITCH")
        self.HL1.addWidget(self.FBSwitch)

        self.Mode = DoubleButton(self)
        self.Mode.Label.setText("Mode")
        self.HL1.addWidget(self.Mode)

        self.HISP = SetPoint(self)
        self.HISP.Label.setText("HI SET")
        self.HL1.addWidget(self.HISP)

        self.LOSP = SetPoint(self)
        self.LOSP.Label.setText("LO SET")
        self.HL1.addWidget(self.LOSP)

        self.SP = SetPoint(self)
        self.SP.Label.setText("SetPoint")
        self.HL1.addWidget(self.SP)

        self.updatebutton = QtWidgets.QPushButton(self)
        self.updatebutton.setText("Update")
        self.updatebutton.setGeometry(QtCore.QRect(0 * R, 0 * R, 40 * R, 70 * R))
        self.HL1.addWidget(self.updatebutton)

        self.Interlock = ColorIndicator(self)
        self.Interlock.Label.setText("INTLCK")
        self.HL2.addWidget(self.Interlock)

        self.Error = ColorIndicator(self)
        self.Error.Label.setText("ERR")
        self.HL2.addWidget(self.Error)

        self.MANSP = ColorIndicator(self)
        self.MANSP.Label.setText("MAN")
        self.HL2.addWidget(self.MANSP)

        self.SAT = ColorIndicator(self)
        self.SAT.Label.setText("SAT")
        self.HL2.addWidget(self.SAT)

        self.ModeREAD = Indicator(self)
        self.ModeREAD.Label.setText("Mode")
        self.HL2.addWidget(self.ModeREAD)

        self.EN = Indicator(self)
        self.EN.Label.setText("ENABLE")
        self.HL2.addWidget(self.EN)

        self.Power = Control(self)
        self.Power.Label.setText("Power")
        self.Power.SetUnit(" %")
        self.Power.Max = 100.
        self.Power.Min = 0.
        self.Power.Step = 0.1
        self.Power.Decimals = 1
        self.HL2.addWidget(self.Power)

        self.IN = Indicator(self)
        self.IN.Label.setText("IN")
        self.HL2.addWidget(self.IN)

        self.HIGH = Indicator(self)
        self.HIGH.Label.setText("HIGH")
        self.HL2.addWidget(self.HIGH)

        self.LOW = SetPoint(self)
        self.LOW.Label.setText("LOW")
        self.HL2.addWidget(self.LOW)

        self.SETSP = Indicator(self)
        self.SETSP.Label.setText("SP")
        self.HL2.addWidget(self.SETSP)

        self.RTD1 = Indicator(self)
        self.RTD1.Label.setText("RTD1")
        self.HL3.addWidget(self.RTD1)

        self.RTD2 = Indicator(self)
        self.RTD2.Label.setText("RTD2")
        self.HL3.addWidget(self.RTD2)


if __name__ == "__main__":


    App = QtWidgets.QApplication(sys.argv)


    MW = HeaterSubWindow()

    if platform.system() == "Linux":
        MW.show()
        MW.showMinimized()
    else:
        MW.show()
    MW.activateWindow()


    sys.exit(App.exec_())

