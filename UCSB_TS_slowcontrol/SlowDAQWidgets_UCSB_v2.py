"""
Module SlowDAQWidgets contains the definition of all the custom widgets used in SlowDAQ

By: Mathieu Laurin														

v1.0 Initial code 29/11/19 ML
v1.1 Alarm on state widget 04/03/20 ML
"""

from PySide2 import QtCore, QtWidgets, QtGui
import time, platform
import os

# FONT = "font-family: \"Calibri\"; font-size: 14px;"
FONT = "font-family: \"Times\"; font-size: 8px;"

# FONT = " "


# BORDER_RADIUS = "border-radius: 2px;"
BORDER_RADIUS = " "

C_LIGHT_GREY = "background-color: rgb(204,204,204);"
C_MEDIUM_GREY = "background-color: rgb(167,167,167);"
C_WHITE = "color: white;"
C_BLACK = "color: black;"
C_GREEN = "background-color: rgb(0,217,0);"
C_RED = "background-color: rgb(255,25,25);"
C_BLUE = "background-color: rgb(34,48,171);"
C_ORANGE = "background-color: rgb(255,132,27);"

# if platform.system() == "Linux":
#     QtGui.QFontDatabase.addApplicationFont("/usr/share/fonts/truetype/vista/calibrib.ttf")
#     FONT = "font-family: calibrib; font-size: 8px;"
#     TITLE_STYLE = "background-color: rgb(204,204,204);  font-family: calibrib;" \
#                   " font-size: 14px; "

# TITLE_STYLE = "background-color: rgb(204,204,204); border-radius: 10px; font-family: " \
#               "\"Calibri\"; font-size: 22px; font-weight: bold;"

#this title style is for SBC slowcontrol machine
TITLE_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: " \
              "\"Times\"; font-size: 14px; font-weight: bold;"
BORDER_STYLE = "border-style: outset; border-width: 2px; border-radius: 4px;" \
               " border-color: black;"
TITLE_STYLE = "background-color: rgb(204,204,204); "
LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Calibri\"; " \
              "font-size: 12px; font-weight: bold;"
# BORDER_STYLE = " "
# FONT = " font-size: 14px;"
# TITLE_STYLE = "background-color: rgb(204,204,204);  " \
#                   " font-size: 14px; "




R=0.6 #Resolution rate


class ButtonGroup(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("ButtonGroup")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 150*R))
        self.setMinimumSize(70*R, 150*R)
        self.setSizePolicy(sizePolicy)

        self.Button0 = QtWidgets.QPushButton(self)
        self.Button0.setObjectName("Button0")
        self.Button0.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 30*R))
        self.Button0.setText("Mode0")
        self.Button0.setStyleSheet("QPushButton {" + FONT + "}")

        self.Button1 = QtWidgets.QPushButton(self)
        self.Button1.setObjectName("Button1")
        self.Button1.setGeometry(QtCore.QRect(0 * R, 35 * R, 70 * R, 30 * R))
        self.Button1.setText("Mode1")
        self.Button1.setStyleSheet("QPushButton {" + FONT + "}")

        self.Button2 = QtWidgets.QPushButton(self)
        self.Button2.setObjectName("Button2")
        self.Button2.setGeometry(QtCore.QRect(0 * R, 70 * R, 70 * R, 30 * R))
        self.Button2.setText("Mode2")
        self.Button2.setStyleSheet("QPushButton {" + FONT + "}")

        self.Button3 = QtWidgets.QPushButton(self)
        self.Button3.setObjectName("Button3")
        self.Button3.setGeometry(QtCore.QRect(0 * R, 105 * R, 70 * R, 30 * R))
        self.Button3.setText("Mode3")
        self.Button3.setStyleSheet("QPushButton {" + FONT + "}")

class PnID_Alone(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("PnID_Alone")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.setMinimumSize(70*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Background.setStyleSheet("QLabel {" + C_LIGHT_GREY + BORDER_RADIUS+ "}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("PnID_Alone")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")


class ColoredStatus(QtWidgets.QWidget):
    # Mode number should be set to 0, 1 and 2
    def __init__(self, parent=None, mode=0):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("ColoredStatus")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.setMinimumSize(70*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.Background.setStyleSheet("QLabel {" + C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Indicator")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Field = QtWidgets.QPushButton(self)
        self.Field.setObjectName("color status value")
        self.Field.setGeometry(QtCore.QRect(2.5*R, 20*R, 65*R, 15*R))


        self.Mode = mode
        if self.Mode == 0:
            # mode 0: color is green when active is false and red when active is true
            self.Field.setStyleSheet(
                "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[Active = true]{" + C_RED +
                "} QWidget[Active = false]{" + C_GREEN + "}")
            # mode 1: color is grey when active is false and red when active is true
        elif self.Mode == 1:
            self.Field.setStyleSheet(
                "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[Active = true]{" + C_RED +
                "} QWidget[Active = false]{" + C_MEDIUM_GREY + "}")
            # mode 2: color is grey when active is false and green when active is true
        elif self.Mode == 2:
            self.Field.setStyleSheet(
                "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[Active = true]{" + C_GREEN +
                "} QWidget[Active = false]{" + C_MEDIUM_GREY + "}")
        elif self.Mode == 4:
            # mode 0: color is green when active is false and red when active is true
            self.Field.setStyleSheet(
                "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[Active = true]{" + C_GREEN +
                "} QWidget[Active = false]{" + C_RED + "}")
        else:
            print("Please set a mode number to class colorstatus widget!")
        self.Field.setProperty("Active", False)
    @QtCore.Slot()
    def UpdateColor(self, active):
        # active should true or false
        if active in [True, "true", 1]:
            self.Field.setProperty("Active", True)
        elif active in [False, "false", 0]:
            self.Field.setProperty("Active", False)
        else:
            print("variable'active' must be either True or False!")
        self.Field.setStyle(self.Field.style())


class ColorIndicator(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("ColorIndicator")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.setMinimumSize(70*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_RADIUS+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Indicator")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        # unfinished part of the function, should change color when the reading changes
        self.Field = QtWidgets.QLineEdit(self)
        self.Field.setObjectName("value")
        self.Field.setGeometry(QtCore.QRect(0*R, 20*R, 70*R, 20*R))
        self.Field.setAlignment(QtCore.Qt.AlignCenter)
        self.Field.setStyleSheet(
        "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[Alarm = true]{" + C_ORANGE + "} QWidget[Alarm = false]{" + C_MEDIUM_GREY + "}")
        self.Field.setProperty("Alarm", False)

        # test part.
        self.ColorButton = QtWidgets.QPushButton(self)
        self.ColorButton.setObjectName("ColorButton")
        self.ColorButton.setGeometry(QtCore.QRect(0*R, 20*R, 65*R, 15*R))
        self.ColorButton.setStyleSheet(
            "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[ColorStyle='0']{" + C_ORANGE +
            "} QWidget[ColorStyle = '1']{" + C_RED + "} QWidget[ColorStyle = '2']{" + C_BLUE + "}")
        self.ColorNumber = 0
        self.ColorButton.clicked.connect(self.ButtonClicked)

    @QtCore.Slot()
    def ButtonClicked(self):
        self.ColorNumber += 1
        self.ColorNumber = self.ColorNumber % 3
        self.ColorButton.setProperty("ColorStyle", str(self.ColorNumber))
        self.ColorButton.setStyle(self.ColorButton.style())

    def setColorNumber(self, number):
        self.ColorNumber = number

    def UpdateColor(self):
        self.ColorButton.setProperty("ColorStyle", str(self.ColorNumber))
        self.ColorButton.setStyle(self.ColorButton.style())


# unfinished part of change button color every 2 seconds
def ColorNumberLoop(self, loopnumber=10):
    while loopnumber>1:
         self.ColorButton.setProperty("ColorStyle", str(self.ColorNumber))
         self.ColorButton.setStyle(self.ColorButton.style())
         self.ColorNumber += 1
         loopnumber -= 1
         time.sleep(2)
         self.ColorNumber = self.ColorNumber%3


class SetPoint(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("SetPoint")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.setMinimumSize(70*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("SetPoint")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Field = QtWidgets.QLineEdit(self)
        self.Field.setValidator(QtGui.QIntValidator(0*R, 1000*R, self))
        self.Field.setAlignment(QtCore.Qt.AlignCenter)
        self.Field.setObjectName("setpoint value")
        self.Field.setGeometry(QtCore.QRect(0*R, 20*R, 70*R, 20*R))
        self.Field.setStyleSheet("QLineEdit {"+BORDER_STYLE + C_BLACK + FONT+"}")
        self.Field.editingFinished.connect(self.UpdateValue)
        self.value = 0
        self.Field.setText(str(self.value))

    def SetValue(self, value):
        self.value = value
        self.Field.setText(format(value, '#.2f') + self.Unit)

    def UpdateValue(self):
        self.value = self.Field.text()


class CheckButton(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("CheckButton")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 200*R, 100*R))
        self.setMinimumSize(200*R, 100*R)
        self.setSizePolicy(sizePolicy)

        self.CheckButton = QtWidgets.QPushButton(self)
        self.CheckButton.setText("Check!")
        self.CheckButton.Alarm = False

    @QtCore.Slot()
    def CollectAlarm(self, *args):
        self.Collected = False
        for i in range(len(args)):
            # calculate collected alarm status
            self.Collected = self.Collected or args[i].Alarm
        self.CheckButton.Alarm = self.Collected


class Loadfile(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("LoadFile")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 600*R, 100*R))
        self.setMinimumSize(600*R, 1000*R)
        self.setSizePolicy(sizePolicy)

        self.VL = QtWidgets.QVBoxLayout(self)
        self.VL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.setSpacing(3)

        self.HL = QtWidgets.QHBoxLayout()
        self.HL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.addLayout(self.HL)

        self.FilePath = QtWidgets.QLineEdit(self)
        self.FilePath.setGeometry(QtCore.QRect(0*R, 0*R, 400*R, 50*R))
        self.HL.addWidget(self.FilePath)

        self.LoadPathButton = QtWidgets.QPushButton(self)
        self.LoadPathButton.clicked.connect(self.LoadPath)
        self.LoadPathButton.setText("LoadPath")
        self.LoadPathButton.setFixedSize(180*R, 50*R)
        self.HL.addWidget(self.LoadPathButton)

        self.LoadFileButton = QtWidgets.QPushButton(self)
        self.LoadFileButton.setFixedSize(180*R, 50*R)
        self.LoadFileButton.setText("ReadFile")
        self.HL.addWidget(self.LoadFileButton)

        self.FileContent = QtWidgets.QTextEdit(self)
        self.FileContent.setReadOnly(True)
        self.VL.addWidget(self.FileContent)

    def LoadPath(self):
        # set default path to read
        defaultpath = "$HOME/.config//SBC/SlowControl.ini"
        filterset = "*.ini;;*.py;;*.*"
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', dir=defaultpath, filter=filterset)
        self.FilePath.setText(name[0])

        try:
            print("Read " + str(self.FilePath.text()))
            file = open(self.FilePath.text(), 'r')

            with file:
                text = file.read()
                self.FileContent.setText(text)
        except:
            print("Error! Please type in a valid path")


class CustomSave(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("CustomSave")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 600*R, 1000*R))
        self.setMinimumSize(600*R, 1000*R)
        self.setSizePolicy(sizePolicy)

        self.VL = QtWidgets.QHBoxLayout()
        self.VL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.setSpacing(3)

        self.FilePath = QtWidgets.QLineEdit(self)
        self.FilePath.setGeometry(QtCore.QRect(0*R, 0*R, 400*R, 50*R))
        self.VL.addWidget(self.FilePath)

        self.LoadPathButton = QtWidgets.QPushButton(self)
        self.LoadPathButton.clicked.connect(self.LoadPath)
        self.LoadPathButton.setText("ChoosePath")
        self.LoadPathButton.setFixedSize(200*R, 50*R)
        self.LoadPathButton.move(400*R, 0*R)
        self.VL.addWidget(self.LoadPathButton)

        self.SaveFileButton = QtWidgets.QPushButton(self)
        self.SaveFileButton.setFixedSize(150*R, 50*R)
        self.SaveFileButton.move(400*R, 50*R)
        self.SaveFileButton.setText("SaveFile")
        self.VL.addWidget(self.SaveFileButton)

        self.Head = None
        self.Tail = None

    def LoadPath(self):
        # set default path to save
        defaultpath = "$HOME/.config//SBC/"
        filterset = "*.ini"
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', dir=defaultpath, filter=filterset)
        self.FilePath.setText(name[0])
        head_tail = os.path.split(name[0])
        # split path to a local path and the project name for future reference
        self.Head = head_tail[0]
        self.Tail = head_tail[1]


class AlarmStatusWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("AlarmStatusWidget")
        self.setGeometry(QtCore.QRect(0 * R, 0 * R, 200 * R, 100 * R))
        self.setMinimumSize(200 * R, 100 * R)
        self.setSizePolicy(sizePolicy)

        self.GL = QtWidgets.QGridLayout(self)
        self.GL.setContentsMargins(0 * R, 0 * R, 0 * R, 0 * R)
        self.GL.setSpacing(3)

        self.Label = QtWidgets.QLabel(self)
        self.Label.setMinimumSize(QtCore.QSize(10 * R, 10 * R))
        self.Label.setStyleSheet("QLabel {" +TITLE_STYLE+"}")
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setText("Label")
        self.GL.addWidget(self.Label,0,1)

        self.Indicator = Indicator(self)
        self.Indicator.Label.setText("Indicator")
        self.GL.addWidget(self.Indicator,1,0)

        self.Low_Limit = SetPoint(self)
        self.Low_Limit.Label.setText("LOW")
        self.GL.addWidget(self.Low_Limit,1,1)

        self.High_Limit = SetPoint(self)
        self.High_Limit.Label.setText("HIGH")
        self.GL.addWidget(self.High_Limit,1,2)

        # When mode is off, the alarm won't be sent out in spite of the value of the indicator value
        self.AlarmMode = QtWidgets.QCheckBox(self)
        self.AlarmMode.setText("Active")
        self.GL.addWidget(self.AlarmMode,0,3)
        self.Alarm = False

        self.updatebutton =  QtWidgets.QPushButton(self)
        self.updatebutton.setText("Update")
        self.GL.addWidget(self.updatebutton,1,3)

    @QtCore.Slot()
    def CheckAlarm(self):
        if self.AlarmMode.isChecked():
            if int(self.Low_Limit.value) > int(self.High_Limit.value):
                print("Low limit should be less than high limit!")
            else:
                if int(self.Indicator.value) < int(self.Low_Limit.value):
                    self.Indicator.SetAlarm()
                    self.Alarm = True
                    print(str(self.Label.text()) + " reading is lower than the low limit")
                elif int(self.Indicator.value) > int(self.High_Limit.value):
                    self.Indicator.SetAlarm()
                    self.Alarm = True
                    print(str(self.Label.text()) + " reading is higher than the high limit")
                else:
                    self.Indicator.ResetAlarm()
                    self.Alarm = False
        else:
            self.Indicator.ResetAlarm()
            self.Alarm = False

    @QtCore.Slot()
    def UpdateAlarm(self,Value):
        if self.AlarmMode.isChecked():
            if Value:
                self.Indicator.SetAlarm()
                self.Alarm = True
            elif not Value:
                self.Indicator.ResetAlarm()
                self.Alarm = False
            else:
                print("Alarm Info Error")

        else:
            self.Indicator.ResetAlarm()
            self.Alarm = False


# class HeaterExpand(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
#
#         self.setObjectName("HeaterExpand")
#         self.setGeometry(QtCore.QRect(0*R, 0*R, 1200*R, 200*R))
#         self.setMinimumSize(1200*R, 200*R)
#         self.setSizePolicy(sizePolicy)
#
#         self.GL = QtWidgets.QGridLayout(self)
#         self.GL.setContentsMargins(0 * R, 0 * R, 0 * R, 0 * R)
#         self.GL.setSpacing(3*R)
#
#         self.Label = QtWidgets.QLabel(self)
#         self.Label.setObjectName("Label")
#         self.Label.setMinimumSize(QtCore.QSize(10*R, 10*R))
#         # self.Label.setStyleSheet(TITLE_STYLE + BORDER_STYLE)
#         # self.Label.setAlignment(QtCore.Qt.AlignCenter)
#         self.Label.setText("Label")
#         self.GL.addWidget(self.Label,0,1)
#
#         self.SP = SetPoint(self)
#         self.SP.Label.setText("SetPoint")
#
#         self.GL.addWidget(self.SP, 1, 0)
#
#         self.MANSP = SetPoint(self)
#         self.MANSP.Label.setText("Manual SetPoint")
#         self.GL.addWidget(self.MANSP, 1, 1)
#
#         self.Power = Control(self)
#         self.Power.Label.setText("Power")
#         self.Power.SetUnit(" %")
#         self.Power.Max = 100.
#         self.Power.Min = 0.
#         self.Power.Step = 0.1
#         self.Power.Decimals = 1
#         self.GL.addWidget(self.Power, 1, 2)
#
#         self.RTD1 = Indicator(self)
#         self.RTD1.Label.setText("RTD1")
#         self.GL.addWidget(self.RTD1, 1, 3)
#
#         self.RTD2 = Indicator(self)
#         self.RTD2.Label.setText("RTD2")
#         self.GL.addWidget(self.RTD2, 1, 4)
#
#         self.Interlock = ColorIndicator(self)
#         self.Interlock.Label.setText("INTLCK")
#         self.GL.addWidget(self.Interlock, 1, 5)
#
#         self.Error = ColorIndicator(self)
#         self.Error.Label.setText("ERR")
#         self.GL.addWidget(self.Error, 1, 6)
#
#         self.HIGH = SetPoint(self)
#         self.HIGH.Label.setText("HIGH")
#         self.GL.addWidget(self.HIGH, 1, 7)
#
#         self.LOW = SetPoint(self)
#         self.LOW.Label.setText("LOW")
#         self.GL.addWidget(self.LOW, 1, 8)
#
#         self.Mode = DoubleButton(self)
#         self.Mode.Label.setText("Mode")
#         self.GL.addWidget(self.Mode,1,9)
#
#         self.FBSwitch = Menu(self)
#         self.FBSwitch.Label.setText("FBSWITCH")
#         self.GL.addWidget(self.FBSwitch,1,10)
#
#         self.LOID = Indicator(self)
#         self.LOID.Label.setText('LOW')
#         self.GL.addWidget(self.LOID, 1,11)
#
#         self.HIID = Indicator(self)
#         self.HIID.Label.setText('HIGH')
#         self.GL.addWidget(self.HIID, 1,12)
#
#         self.SETSP = Indicator(self)
#         self.SETSP.Label.setText("SP")
#         self.GL.addWidget(self.SETSP,1,13)
#
#         # self.updatebutton= QtWidgets.QPushButton(self)
#         # self.updatebutton.setText("Update")
#         # self.GL.addWidget(self.updatebutton,1,14)




class BoolIndicator(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("BoolIndicator")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.setMinimumSize(70*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_RADIUS+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Indicator")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Field = QtWidgets.QLineEdit(self)
        self.Field.setObjectName("value")
        self.Field.setGeometry(QtCore.QRect(0*R, 20*R, 70*R, 20*R))
        self.Field.setAlignment(QtCore.Qt.AlignCenter)
        self.Field.setReadOnly(True)
        self.Field.setStyleSheet(
            "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[Alarm = true]{" + C_ORANGE +
            "} QWidget[Alarm = false]{" + C_MEDIUM_GREY + "}")
        self.Field.setProperty("Alarm", False)
        self.SetValue("On")

    def SetValue(self, value):
        self.value = value
        self.Field.setText(str(value))

    def SetAlarm(self):
        self.Field.setProperty("Alarm", True)
        self.Field.setStyle(self.Field.style())

    def ResetAlarm(self):
        self.Field.setProperty("Alarm", False)
        self.Field.setStyle(self.Field.style())


class Indicator(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("Indicator")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 80*R, 40*R))
        self.setMinimumSize(80*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 80*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Indicator")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 80*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Field = QtWidgets.QLineEdit(self)
        self.Field.setObjectName("indicator value")
        self.Field.setGeometry(QtCore.QRect(0*R, 20*R, 80*R, 20*R))
        self.Field.setAlignment(QtCore.Qt.AlignCenter)
        self.Field.setReadOnly(True)
        self.Field.setStyleSheet(
            "QLineEdit{" + BORDER_STYLE + C_WHITE + FONT + "} QLineEdit[Alarm = true]{" + C_ORANGE +
            "} QLineEdit[Alarm = false]{" + C_MEDIUM_GREY + "}")
        self.Field.Property = False
        self.Field.setProperty("Alarm", False)

        self.Unit = " K"
        self.SetValue(0.)

    def SetValue(self, value):
        self.value = value
        self.Field.setText(format(value, '#.2f') + self.Unit)

    def SetAlarm(self):
        self.Field.Property = True
        self.Field.setProperty("Alarm", self.Field.Property)
        self.Field.setStyle(self.Field.style())

    def ResetAlarm(self):
        self.Field.Property = False
        self.Field.setProperty("Alarm", self.Field.Property)
        self.Field.setStyle(self.Field.style())

    def SetUnit(self, unit=" °C"):
        self.Unit = unit
        self.Field.setText(format(self.value, '#.2f') + self.Unit)

    # set alarm mode, if the mode is false, then the alarm will not be triggered despite of alarm value
    def SetAlarmMode(self, Mode):
        self.AlarmMode = Mode

class PressureIndicator(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("PressureIndicator")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 80*R, 40*R))
        self.setMinimumSize(80*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 80*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("PressureIndicator")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 80*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Field = QtWidgets.QLineEdit(self)
        self.Field.setObjectName("indicator value")
        self.Field.setGeometry(QtCore.QRect(0*R, 20*R, 80*R, 20*R))
        self.Field.setAlignment(QtCore.Qt.AlignCenter)
        self.Field.setReadOnly(True)
        self.Field.setStyleSheet(
            "QLineEdit{" + BORDER_STYLE + C_WHITE + FONT + "} QLineEdit[Alarm = true]{" + C_ORANGE +
            "} QLineEdit[Alarm = false]{" + C_MEDIUM_GREY + "}")
        self.Field.Property = False
        self.Field.setProperty("Alarm", False)

        self.Unit = " mA"
        self.SetValue(0.)

    def SetValue(self, value):
        self.value = value
        self.Field.setText(format(value, '#.2f') + self.Unit)

    def SetAlarm(self):
        self.Field.Property = True
        self.Field.setProperty("Alarm", self.Field.Property)
        self.Field.setStyle(self.Field.style())

    def ResetAlarm(self):
        self.Field.Property = False
        self.Field.setProperty("Alarm", self.Field.Property)
        self.Field.setStyle(self.Field.style())

    def SetUnit(self, unit=" °C"):
        self.Unit = unit
        self.Field.setText(format(self.value, '#.2f') + self.Unit)

    # set alarm mode, if the mode is false, then the alarm will not be triggered despite of alarm value
    def SetAlarmMode(self, Mode):
        self.AlarmMode = Mode


class LiquidLevel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("LiquidLevel")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 80*R, 40*R))
        self.setMinimumSize(80*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 80*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("LiquidLevel")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 80*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Field = QtWidgets.QLineEdit(self)
        self.Field.setObjectName("indicator value")
        self.Field.setGeometry(QtCore.QRect(0*R, 20*R, 80*R, 20*R))
        self.Field.setAlignment(QtCore.Qt.AlignCenter)
        self.Field.setReadOnly(True)
        self.Field.setStyleSheet(
            "QLineEdit{" + BORDER_STYLE + C_WHITE + FONT + "} QLineEdit[Alarm = true]{" + C_ORANGE +
            "} QLineEdit[Alarm = false]{" + C_MEDIUM_GREY + "}")
        self.Field.Property = False
        self.Field.setProperty("Alarm", False)

        self.Unit = " cm"
        self.SetValue(0.)

    def SetValue(self, value):
        self.value = value
        self.Field.setText(format(value, '#.2f') + self.Unit)

    def SetAlarm(self):
        self.Field.Property = True
        self.Field.setProperty("Alarm", self.Field.Property)
        self.Field.setStyle(self.Field.style())

    def ResetAlarm(self):
        self.Field.Property = False
        self.Field.setProperty("Alarm", self.Field.Property)
        self.Field.setStyle(self.Field.style())

    def SetUnit(self, unit=" °C"):
        self.Unit = unit
        self.Field.setText(format(self.value, '#.2f') + self.Unit)

    # set alarm mode, if the mode is false, then the alarm will not be triggered despite of alarm value
    def SetAlarmMode(self, Mode):
        self.AlarmMode = Mode

class Control(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.Signals = ChangeValueSignal()

        self.setObjectName("Control")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.setMinimumSize(70*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Control")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Button = QtWidgets.QPushButton(self)
        self.Button.setObjectName("Button")
        self.Button.setGeometry(QtCore.QRect(0*R, 20*R, 70*R, 20*R))
        self.Button.setStyleSheet("QPushButton {" +C_BLUE + C_WHITE + FONT + BORDER_RADIUS+"}")

        self.Unit = " W"
        self.SetValue(0.)

        self.Max = 10.
        self.Min = -10.
        self.Step = 0.1
        self.Decimals = 1

    def SetValue(self, value):
        self.value = value
        self.Button.setText(str(value) + self.Unit)

    def SetUnit(self, unit=" °C"):
        self.Unit = unit
        self.Button.setText(format(self.value, '#.2f') + self.Unit)

    @QtCore.Slot()
    def Changevalue(self):
        return 0
        # Dialog = QtWidgets.QInputDialog()
        # Dialog.setInputMode(QtWidgets.QInputDialog.DoubleInput)
        # Dialog.setDoubleDecimals(self.Decimals)
        # Dialog.setDoubleRange(self.Min, self.Max)
        # Dialog.setDoubleStep(self.Step)
        # Dialog.setDoublevalue(self.value)
        # Dialog.setLabelText("Please entre a new value (min = " + str(self.Min) + ", max = " + str(self.Max) + ")")
        # Dialog.setModal(True)
        # Dialog.setWindowTitle("Modify value")
        # Dialog.exec()
        # if Dialog.result():
        #     self.SetValue(Dialog.doublevalue())
        #     self.Signals.fSignal.emit(self.value)

    def Activate(self, Activate):
        if Activate:
            try:
                self.Button.clicked.connect(self.Changevalue)
            except:
                pass
        else:
            try:
                self.Button.clicked.disconnect(self.Changevalue)
            except:
                pass


class Menu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.Signals = ChangeValueSignal()

        self.setObjectName("Menu")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 140*R, 40*R))
        self.setMinimumSize(140*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 140*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Menu")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 140*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Combobox = QtWidgets.QComboBox(self)
        self.Combobox.setObjectName("Menu")
        self.Combobox.setGeometry(QtCore.QRect(0*R, 20*R, 140*R, 20*R))
        self.Combobox.addItem("0")
        self.Combobox.addItem("1")
        self.Combobox.addItem("2")
        self.Combobox.setStyleSheet("QWidget {" + FONT + "}")


class Toggle(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.Signals = ChangeValueSignal()

        self.setObjectName("Toggle")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.setMinimumSize(70*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Toggle")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Button = QtWidgets.QPushButton(self)
        self.Button.setObjectName("Button")
        self.Button.setGeometry(QtCore.QRect(0*R, 20*R, 70*R, 20*R))
        self.Button.setStyleSheet(
            "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[State = true]{" + C_GREEN
            + "} QWidget[State = false]{" + C_RED + "}")
        self.Button.setProperty("State", False)
        self.Button.clicked.connect(self.ButtonClicked)

        self.State = "On"
        self.SetToggleStateNames("On", "Off")
        self.SetState("Off")

    def SetToggleStateNames(self, On, Off):
        self.OnName = On
        self.OffName = Off

    def ToggleState(self):
        if self.State == self.OnName:
            self.Button.setText(self.OffName)
            self.Button.setProperty("State", False)
            self.Button.setStyle(self.Button.style())
            self.State = self.OffName
        else:
            self.Button.setText(self.OnName)
            self.Button.setProperty("State", True)
            self.Button.setStyle(self.Button.style())
            self.State = self.OnName

    def SetState(self, State):
        if self.State != self.OffName and State == self.OffName:
            self.ToggleState()
        elif self.State != self.OnName and State == self.OnName:
            self.ToggleState()

    @QtCore.Slot()
    def ButtonClicked(self):
        self.ToggleState()
        self.Signals.sSignal.emit(self.State)

    def Activate(self, Activate):
        if Activate:
            try:
                self.Button.clicked.connect(self.ButtonClicked)
            except:
                pass
        else:
            try:
                self.Button.clicked.disconnect(self.ButtonClicked)
            except:
                pass


class Position(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("Position")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 250*R))
        self.setMinimumSize(70*R, 250*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 250*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Position")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Field = QtWidgets.QLineEdit(self)
        self.Field.setObjectName("value")
        self.Field.setGeometry(QtCore.QRect(0*R, 20*R, 70*R, 20*R))
        self.Field.setAlignment(QtCore.Qt.AlignCenter)
        self.Field.setReadOnly(True)
        self.Field.setStyleSheet(
            "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[Alarm = true]{" + C_ORANGE
            + "} QWidget[Alarm = false]{" + C_MEDIUM_GREY + "}")
        self.Field.setProperty("Alarm", False)

        self.Max = QtWidgets.QLabel(self)
        self.Max.setObjectName("Max")
        self.Max.setGeometry(QtCore.QRect(0*R, 43, 40*R, 20*R))
        self.Max.setAlignment(QtCore.Qt.AlignRight)
        self.Max.setStyleSheet("QLabel {" +FONT+"}")

        self.Zero = QtWidgets.QLabel(self)
        self.Zero.setObjectName("Zero")
        self.Zero.setText("0\"")
        self.Zero.setAlignment(QtCore.Qt.AlignRight)
        self.Zero.setStyleSheet("QLabel {" +FONT+"}")

        self.Min = QtWidgets.QLabel(self)
        self.Min.setObjectName("Min")
        self.Min.setGeometry(QtCore.QRect(0*R, 230*R, 40*R, 20*R))
        self.Min.setAlignment(QtCore.Qt.AlignRight)
        self.Min.setStyleSheet("QLabel {" +FONT+"}")

        self.Slider = QtWidgets.QSlider(self)
        self.Slider.setObjectName("Slider")
        self.Slider.setTickPosition(QtWidgets.QSlider.TicksLeft)
        self.Slider.setGeometry(QtCore.QRect(40*R, 45*R, 25*R, 200*R))
        self.Slider.setStyleSheet("QSlider::handle:vertical{background: white; border-radius: 5px;}")
        self.Slider.setEnabled(False)

        self.SetLimits(-.88, 2.35)
        self.SetValue(0.)

    def SetValue(self, value):
        self.value = value
        self.Slider.setSliderPosition(value * 100*R)
        self.Field.setText(format(value, '#.2f') + "\"")

    def SetLimits(self, Min, Max):
        self.Slider.setMaximum(Max * 100*R)
        self.Slider.setMinimum(Min * 100*R)
        self.Max.setText(format(Max, '#.2f') + "\"")
        self.Min.setText(format(Min, '#.2f') + "\"")
        Offset = 43 - ((43 - 230) / (Max - Min)) * Max
        self.Zero.setGeometry(QtCore.QRect(0*R, Offset, 40*R, 20*R))

    def SetAlarm(self):
        self.Field.setProperty("Alarm", True)
        self.Field.setStyle(self.Field.style())

    def ResetAlarm(self):
        self.Field.setProperty("Alarm", False)
        self.Field.setStyle(self.Field.style())


class State(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("State")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 140*R, 40*R))
        self.setMinimumSize(140*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 140*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("State")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 140*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Field = QtWidgets.QLineEdit(self)
        self.Field.setObjectName("state value")
        self.Field.setGeometry(QtCore.QRect(0*R, 20*R, 140*R, 20*R))
        self.Field.setAlignment(QtCore.Qt.AlignCenter)
        self.Field.setReadOnly(True)
        self.Field.setStyleSheet(
            "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[Alarm = true]{" + C_ORANGE
            + "} QWidget[Alarm = false]{" + C_MEDIUM_GREY + "}")
        self.Field.setProperty("Alarm", False)
        self.Field.setText("Emergency")

    def SetAlarm(self):
        self.Field.setProperty("Alarm", True)
        self.Field.setStyle(self.Field.style())

    def ResetAlarm(self):
        self.Field.setProperty("Alarm", False)
        self.Field.setStyle(self.Field.style())


class DoubleButton(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.Signals = ChangeValueSignal()

        self.setObjectName("DoubleButton")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 140*R, 40*R))
        self.setMinimumSize(140*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 140*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Double button")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 140*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.LButton = QtWidgets.QPushButton(self)
        self.LButton.setObjectName("LButton")
        self.LButton.setText("On")
        self.LButton.setGeometry(QtCore.QRect(2.5*R, 20*R, 65*R, 15*R))
        self.LButton.setProperty("State", True)
        self.LButton.setStyleSheet(
            "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[State = true]{" + C_GREEN
            + "} QWidget[State = false]{" + C_RED + "}")


        self.RButton = QtWidgets.QPushButton(self)
        self.RButton.setObjectName("RButton")
        self.RButton.setText("Off")
        self.RButton.setGeometry(QtCore.QRect(72.5*R, 20*R, 65*R, 15*R))
        self.RButton.setProperty("State", False)
        self.RButton.setStyleSheet(
            "QWidget{" + BORDER_RADIUS + C_WHITE + FONT + "} QWidget[State = true]{"
            + C_GREEN + "} QWidget[State = false]{" + C_RED + "}")


        self.LState = "Active"
        self.RState = "Inactive"
        self.SetButtonStateNames("Active", "Inactive")
        self.ButtonRState()
        self.Activate(True)

    def SetButtonStateNames(self, Active, Inactive):
        self.ActiveName = Active
        self.InactiveName = Inactive

    # Neutral means that the button shouldn't show any color
    def ButtonLState(self):
        if self.LState == self.InactiveName and self.RState == self.ActiveName:
            self.LButton.setProperty("State", True)
            self.LButton.setStyle(self.LButton.style())
            self.LState = self.ActiveName
            self.RButton.setProperty("State", "Neutral")
            self.RButton.setStyle(self.RButton.style())
            self.RState = self.InactiveName
        else:
            pass

    def ButtonRState(self):
        if self.LState == self.ActiveName and self.RState == self.InactiveName:
            self.RButton.setProperty("State", False)
            self.RButton.setStyle(self.RButton.style())
            self.LState = self.InactiveName
            self.LButton.setProperty("State", "Neutral")
            self.LButton.setStyle(self.LButton.style())
            self.RState = self.ActiveName
        else:
            pass

    @QtCore.Slot()
    def ButtonLClicked(self):
        # time.sleep(1)
        self.ButtonLState()
        self.Signals.sSignal.emit(self.LButton.text())

    @QtCore.Slot()
    def ButtonRClicked(self):
        # time.sleep(1)
        self.ButtonRState()
        self.Signals.sSignal.emit(self.RButton.text())

    def Activate(self, Activate):
        if Activate:
            try:
                self.LButton.clicked.connect(self.ButtonLClicked)
                self.RButton.clicked.connect(self.ButtonRClicked)
            except:
                pass
        else:
            try:
                self.LButton.clicked.disconnect(self.ButtonLClicked)
                self.RButton.clicked.disconnect(self.ButtonRClicked)
            except:
                pass


class SingleButton(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.Signals = ChangeValueSignal()

        self.setObjectName("SingleButton")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.setMinimumSize(70*R, 40*R)
        self.setSizePolicy(sizePolicy)

        self.Background = QtWidgets.QLabel(self)
        self.Background.setObjectName("Background")
        self.Background.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 40*R))
        self.Background.setStyleSheet("QLabel {" +C_LIGHT_GREY + BORDER_STYLE+"}")

        self.Label = QtWidgets.QLabel(self)
        self.Label.setObjectName("Label")
        self.Label.setText("Button")
        self.Label.setGeometry(QtCore.QRect(0*R, 0*R, 70*R, 20*R))
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("QLabel {" +FONT+"}")

        self.Button = QtWidgets.QPushButton(self)
        self.Button.setObjectName("Button")
        self.Button.setText("Button")
        self.Button.setGeometry(QtCore.QRect(0*R, 20*R, 70*R, 20*R))
        self.Button.setStyleSheet("QPushButton {" +C_BLUE + C_WHITE + FONT + BORDER_RADIUS+"}")

    @QtCore.Slot()
    def ButtonClicked(self):
        self.Signals.sSignal.emit(self.Button.text())

    def Activate(self, Activate):
        if Activate:
            try:
                self.Button.clicked.connect(self.ButtonClicked)
            except:
                pass
        else:
            try:
                self.Button.clicked.disconnect(self.ButtonClicked)
            except:
                pass


class AlarmWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.Widget = QtWidgets.QWidget(self)
        self.Widget.setGeometry(QtCore.QRect(0*R, 0*R, 2000*R, 1000*R))

        # reset the size of the window
        self.setMinimumSize(2000*R, 1100*R)
        self.resize(2000*R, 1100*R)
        self.setWindowTitle("Alarm Window")
        self.Widget.setGeometry(QtCore.QRect(0*R, 0*R, 2000*R, 1100*R))

        self.Tab = QtWidgets.QTabWidget(self)
        self.Tab.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Tab.setStyleSheet("font-weight: bold; font-size: 20px; font-family: Times;")
        self.Tab.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.Tab.setGeometry(QtCore.QRect(0*R, 0*R, 2400*R, 1400*R))

        self.PressureTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.PressureTab, "Pressure Transducers")

        self.RTDSET12Tab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.RTDSET12Tab, "RTD SET 1&2")

        self.RTDSET34Tab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.RTDSET34Tab, "RTD SET 3&4")

        self.RTDLEFTTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.RTDLEFTTab, "HEATER RTDs and ETC")

        # Groupboxs for alarm/PT/TT

        self.GLPT = QtWidgets.QGridLayout()
        # self.GLPT = QtWidgets.QGridLayout(self)
        self.GLPT.setContentsMargins(20*R, 20*R, 20*R, 20*R)
        self.GLPT.setSpacing(20*R)
        self.GLPT.setAlignment(QtCore.Qt.AlignCenter)

        self.GroupPT = QtWidgets.QGroupBox(self.PressureTab)
        self.GroupPT.setTitle("Pressure Transducer")
        self.GroupPT.setLayout(self.GLPT)
        self.GroupPT.move(0*R, 0*R)

        self.GLRTD1 = QtWidgets.QGridLayout()
        # self.GLRTD1 = QtWidgets.QGridLayout(self)
        self.GLRTD1.setContentsMargins(20*R, 20*R, 20*R, 20*R)
        self.GLRTD1.setSpacing(20*R)
        self.GLRTD1.setAlignment(QtCore.Qt.AlignCenter)

        self.GroupRTD1 = QtWidgets.QGroupBox(self.RTDSET12Tab)
        self.GroupRTD1.setTitle("RTD SET 1")
        self.GroupRTD1.setLayout(self.GLRTD1)
        self.GroupRTD1.move(0*R, 0*R)

        self.GLRTD2 = QtWidgets.QGridLayout()
        # self.GLRTD2 = QtWidgets.QGridLayout(self)
        self.GLRTD2.setContentsMargins(20*R, 20*R, 20*R, 20*R)
        self.GLRTD2.setSpacing(20*R)
        self.GLRTD2.setAlignment(QtCore.Qt.AlignCenter)

        self.GroupRTD2 = QtWidgets.QGroupBox(self.RTDSET12Tab)
        self.GroupRTD2.setTitle("RTD SET 2")
        self.GroupRTD2.setLayout(self.GLRTD2)
        self.GroupRTD2.move(0*R, 300*R)

        self.GLRTD3 = QtWidgets.QGridLayout()
        # self.GLRTD3 = QtWidgets.QGridLayout(self)
        self.GLRTD3.setContentsMargins(20*R, 20*R, 20*R, 20*R)
        self.GLRTD3.setSpacing(20*R)
        self.GLRTD3.setAlignment(QtCore.Qt.AlignCenter)

        self.GroupRTD3 = QtWidgets.QGroupBox(self.RTDSET34Tab)
        self.GroupRTD3.setTitle("RTD SET 3")
        self.GroupRTD3.setLayout(self.GLRTD3)
        self.GroupRTD3.move(0*R, 0*R)

        self.GLRTD4 = QtWidgets.QGridLayout()
        # self.GLRTD4 = QtWidgets.QGridLayout(self)
        self.GLRTD4.setContentsMargins(20*R, 20*R, 20*R, 20*R)
        self.GLRTD4.setSpacing(20*R)
        self.GLRTD4.setAlignment(QtCore.Qt.AlignCenter)

        self.GroupRTD4 = QtWidgets.QGroupBox(self.RTDSET34Tab)
        self.GroupRTD4.setTitle("RTD SET 4")
        self.GroupRTD4.setLayout(self.GLRTD4)
        self.GroupRTD4.move(0*R, 500*R)

        self.GLRTDLEFT = QtWidgets.QGridLayout()
        # self.GLRTDLEFT = QtWidgets.QGridLayout(self)
        self.GLRTDLEFT.setContentsMargins(20*R, 20*R, 20*R, 20*R)
        self.GLRTDLEFT.setSpacing(20*R)
        self.GLRTDLEFT.setAlignment(QtCore.Qt.AlignCenter)

        self.GroupRTDLEFT = QtWidgets.QGroupBox(self.RTDLEFTTab)
        self.GroupRTDLEFT.setTitle(" LEFT RTDs ")
        self.GroupRTDLEFT.setLayout(self.GLRTDLEFT)
        self.GroupRTDLEFT.move(0*R, 0*R)


        # PT part
        self.PT1012 = AlarmStatusWidget(self.PressureTab)
        self.PT1012.Label.setText("PT1012")

        self.PT1013 = AlarmStatusWidget(self.PressureTab)
        self.PT1013.Label.setText("PT1013")

        self.PT1014 = AlarmStatusWidget(self.PressureTab)
        self.PT1014.Label.setText("PT1014")



        # make a directory for the alarm instrument and assign instrument to certain position
        # self.AlarmRTD1dir = {0: {0: self.TT2111, 1: self.TT2112, 2: self.TT2113, 3: self.TT2114, 4: self.TT2115},
        #                      1: {0: self.TT2116, 1: self.TT2117, 2: self.TT2118, 3: self.TT2119, 4: self.TT2120}}
        #
        # self.AlarmRTD1list1D = [self.TT2111, self.TT2112, self.TT2113,  self.TT2114,  self.TT2115, self.TT2116,
        #                        self.TT2117, self.TT2118, self.TT2119,  self.TT2120]
        #
        # self.AlarmRTD2dir = {0: {0: self.TT2401, 1: self.TT2402, 2: self.TT2403, 3: self.TT2404, 4: self.TT2405},
        #                      1: {0: self.TT2406, 1: self.TT2407, 2: self.TT2408, 3: self.TT2409, 4: self.TT2410},
        #                      2: {0: self.TT2411, 1: self.TT2412, 2: self.TT2413, 3: self.TT2414, 4: self.TT2415},
        #                      3: {0: self.TT2416, 1: self.TT2417, 2: self.TT2418, 3: self.TT2419, 4: self.TT2420},
        #                      4: {0: self.TT2421, 1: self.TT2422, 2: self.TT2423, 3: self.TT2424, 4: self.TT2425},
        #                      5: {0: self.TT2426, 1: self.TT2427, 2: self.TT2428, 3: self.TT2429, 4: self.TT2430},
        #                      6: {0: self.TT2431, 1: self.TT2432}}
        #
        #
        # self.AlarmRTD3dir = {0: {0: self.TT2435, 1: self.TT2436, 2: self.TT2437, 3: self.TT2438, 4: self.TT2439},
        #                      1: {0: self.TT2440, 1: self.TT2441, 2: self.TT2442, 3: self.TT2443, 4: self.TT2444},
        #                      2: {0: self.TT2445, 1: self.TT2446, 2: self.TT2447, 3: self.TT2448, 4: self.TT2449},
        #                      3: {0: self.TT2450}}
        #
        # self.AlarmRTD4dir = {0: {0: self.TT2101, 1: self.TT2102, 2: self.TT2103, 3: self.TT2104, 4: self.TT2105},
        #                      1: {0: self.TT2106, 1: self.TT2107, 2: self.TT2108, 3: self.TT2109, 4: self.TT2110}}
        #
        self.AlarmPTdir = {0: {0: self.PT1012, 1: self.PT1013, 2: self.PT1014}}
        #
        # self.AlarmRTDLEFTdir = {0: {0: self.TT4330, 1: self.TT6220, 2: self.TT6213, 3: self.TT6401, 4: self.TT6203},
        #                         1: {0: self.TT6404, 1: self.TT6207, 2: self.TT6405, 3: self.TT6211, 4: self.TT6406},
        #                         2: {0: self.TT6223, 1: self.TT6410, 2: self.TT6408, 3: self.TT6409, 4: self.TT6412},
        #                         3: {0: self.TT3402, 1: self.TT3401, 2: self.TT7401, 3: self.TT7202, 4: self.TT7403},
        #                         4: {0: self.TT6222, 1: self.TT6407, 2: self.TT6415, 3: self.TT6416, 4: self.TT6411},
        #                         5: {0: self.TT6413, 1: self.TT6414}}

        # # variables usable for building widgets
        # # i is row number, j is column number
        # # RTD1 is for temperature transducer while PT is for pressure transducer
        # # max is max row and column number
        # # last is the last widget's row and column index in gridbox
        # self.i_RTD1_max = len(self.AlarmRTD1dir)
        # self.j_RTD1_max = len(self.AlarmRTD1dir[0])

        # self.i_RTD2_max = len(self.AlarmRTD2dir)
        # self.j_RTD2_max = len(self.AlarmRTD2dir[0])
        # self.i_RTD3_max = len(self.AlarmRTD3dir)
        # self.j_RTD3_max = len(self.AlarmRTD3dir[0])
        # self.i_RTD4_max = len(self.AlarmRTD4dir)
        # self.j_RTD4_max = len(self.AlarmRTD4dir[0])
        # self.i_RTDLEFT_max = len(self.AlarmRTDLEFTdir)
        # self.j_RTDLEFT_max = len(self.AlarmRTDLEFTdir[0])

        self.i_PT_max = len(self.AlarmPTdir)
        self.j_PT_max = len(self.AlarmPTdir[0])
        # self.i_RTD1_last = len(self.AlarmRTD1dir) - 1
        # self.j_RTD1_last = len(self.AlarmRTD1dir[self.i_RTD1_last]) - 1
        # self.i_RTD2_last = len(self.AlarmRTD2dir) - 1
        # self.j_RTD2_last = len(self.AlarmRTD2dir[self.i_RTD2_last]) - 1
        # self.i_RTD3_last = len(self.AlarmRTD3dir) - 1
        # self.j_RTD3_last = len(self.AlarmRTD3dir[self.i_RTD3_last]) - 1
        # self.i_RTD4_last = len(self.AlarmRTD4dir) - 1
        # self.j_RTD4_last = len(self.AlarmRTD4dir[self.i_RTD4_last]) - 1
        # self.i_RTDLEFT_last = len(self.AlarmRTDLEFTdir) - 1
        # self.j_RTDLEFT_last = len(self.AlarmRTDLEFTdir[self.i_RTDLEFT_last]) - 1
        self.i_PT_last = len(self.AlarmPTdir) - 1
        # which is 3
        self.j_PT_last = len(self.AlarmPTdir[self.i_PT_last]) - 1
        # which is 1
        self.ResetOrder()

    @QtCore.Slot()
    def ResetOrder(self):
        # for i in range(0, self.i_RTD1_max):
        #     for j in range(0, self.j_RTD1_max):
        #         # self.GLRTD1.addWidget(eval(self.AlarmRTD1dir[i][j]), i, j)
        #         self.GLRTD1.addWidget(self.AlarmRTD1dir[i][j], i, j)
        #         # end the position generator when i= last element's row number, j= last element's column number
        #         if (i, j) == (self.i_RTD1_last, self.j_RTD1_last):
        #             break
        #     if (i, j) == (self.i_RTD1_last, self.j_RTD1_last):
        #         break
        #
        # for i in range(0, self.i_RTD2_max):
        #     for j in range(0, self.j_RTD2_max):
        #         # self.GLRTD2.addWidget(eval(self.AlarmRTD2dir[i][j]), i, j)
        #         self.GLRTD2.addWidget(self.AlarmRTD2dir[i][j], i, j)
        #         # end the position generator when i= last element's row number, j= last element's column number
        #         if (i, j) == (self.i_RTD2_last, self.j_RTD2_last):
        #             break
        #     if (i, j) == (self.i_RTD2_last, self.j_RTD2_last):
        #         break
        #
        # for i in range(0, self.i_RTD3_max):
        #     for j in range(0, self.j_RTD3_max):
        #         # self.GLRTD3.addWidget(eval(self.AlarmRTD3dir[i][j]), i, j)
        #         self.GLRTD3.addWidget(self.AlarmRTD3dir[i][j], i, j)
        #         # end the position generator when i= last element's row number, j= last element's column number
        #         if (i, j) == (self.i_RTD3_last, self.j_RTD3_last):
        #             break
        #     if (i, j) == (self.i_RTD3_last, self.j_RTD3_last):
        #         break
        #
        # for i in range(0, self.i_RTD4_max):
        #     for j in range(0, self.j_RTD4_max):
        #         # self.GLRTD4.addWidget(eval(self.AlarmRTD4dir[i][j]), i, j)
        #         self.GLRTD4.addWidget(self.AlarmRTD4dir[i][j], i, j)
        #         # end the position generator when i= last element's row number, j= last element's column number
        #         if (i, j) == (self.i_RTD4_last, self.j_RTD4_last):
        #             break
        #     if (i, j) == (self.i_RTD4_last, self.j_RTD4_last):
        #         break
        #
        # for i in range(0, self.i_RTDLEFT_max):
        #     for j in range(0, self.j_RTDLEFT_max):
        #         # self.GLRTDLEFT.addWidget(eval(self.AlarmRTDLEFTdir[i][j]), i, j)
        #         self.GLRTDLEFT.addWidget(self.AlarmRTDLEFTdir[i][j], i, j)
        #         # end the position generator when i= last element's row number, j= last element's column number
        #         if (i, j) == (self.i_RTDLEFT_last, self.j_RTDLEFT_last):
        #             break
        #     if (i, j) == (self.i_RTDLEFT_last, self.j_RTDLEFT_last):
        #         break

        for i in range(0, self.i_PT_max):
            for j in range(0, self.j_PT_max):
                # self.GLPT.addWidget(eval(self.AlarmPTdir[i][j]), i, j)
                self.GLPT.addWidget(self.AlarmPTdir[i][j], i, j)
                # end the position generator when i= last element's row number -1, j= last element's column number
                if (i, j) == (self.i_PT_last, self.j_PT_last):
                    break
            if (i, j) == (self.i_PT_last, self.j_PT_last):
                break

    @QtCore.Slot()
    def ReassignRTD1Order(self):
        # check the status of the Widget and reassign the diretory
        # establish 2 diretory, reorder TempDic to reorder the widgets
        # k,l are pointers in the TempDic, ij are pointers in TempRefDic
        # i_max, j_max are max row and column number
        # l max are max column number+1
        # i_last,j_last are last elements's diretory coordinate
        TempRefRTD1dir = self.AlarmRTD1dir
        TempRTD1dir = {0: {0: None, 1: None, 2: None, 3: None, 4: None},
                       1: {0: None, 1: None, 2: None, 3: None, 4: None}}

        # l_RTD1_max is max number of column
        l_RTD1 = 0
        k_RTD1 = 0

        # i_RTD1_max = 3
        # j_RTD1_max = 5
        # i_PT_max = 4
        # j_PT_max = 5
        # l_RTD1_max = 4
        # l_PT_max = 4
        # i_RTD1_last = 2
        # j_RTD1_last = 4
        # i_PT_last = 3
        # j_PT_last = 1
        i_RTD1_max = len(self.AlarmRTD1dir)
        # which is 3
        j_RTD1_max = len(self.AlarmRTD1dir[0])
        # which is 5

        i_RTD1_last = len(self.AlarmRTD1dir) - 1
        # which is 2
        j_RTD1_last = len(self.AlarmRTD1dir[i_RTD1_last]) - 1
        # which is 4
        # print(i_RTD1_max,j_RTD1_max,i_RTD1_last, j_RTD1_last)

        l_RTD1_max = j_RTD1_max - 1

        # RTD1 put alarm true widget to the begining of the diretory
        for i in range(0, i_RTD1_max):
            for j in range(0, j_RTD1_max):
                if TempRefRTD1dir[i][j].Alarm:
                    TempRTD1dir[k_RTD1][l_RTD1] = TempRefRTD1dir[i][j]
                    l_RTD1 = l_RTD1 + 1
                    if l_RTD1 == l_RTD1_max + 1:
                        l_RTD1 = 0
                        k_RTD1 = k_RTD1 + 1
                if (i, j) == (i_RTD1_last, j_RTD1_last):
                    break
            if (i, j) == (i_RTD1_last, j_RTD1_last):
                break
        # print("1st part")
        #
        #
        # # RTD1 put alarm false widget after that
        for i in range(0, i_RTD1_max):
            for j in range(0, j_RTD1_max):
                if not TempRefRTD1dir[i][j].Alarm:
                    TempRTD1dir[k_RTD1][l_RTD1] = TempRefRTD1dir[i][j]
                    l_RTD1 = l_RTD1 + 1
                    if l_RTD1 == l_RTD1_max + 1:
                        l_RTD1 = 0
                        k_RTD1 = k_RTD1 + 1
                if (i, j) == (i_RTD1_last, j_RTD1_last):
                    break
            if (i, j) == (i_RTD1_last, j_RTD1_last):
                break
        # print("2nd part")
        # Reassign position
        # end the position generator when i= last element's row number, j= last element's column number
        for i in range(0, i_RTD1_max):
            for j in range(0, j_RTD1_max):
                self.GLRTD1.addWidget(TempRTD1dir[i][j], i, j)
                if (i, j) == (i_RTD1_last, j_RTD1_last):
                    break
            if (i, j) == (i_RTD1_last, j_RTD1_last):
                break
        # print("3rd part")

    @QtCore.Slot()
    def ReassignRTD2Order(self):
        # check the status of the Widget and reassign the diretory
        # establish 2 diretory, reorder TempDic to reorder the widgets
        # k,l are pointers in the TempDic, ij are pointers in TempRefDic
        # i_max, j_max are max row and column number
        # l max are max column number+1
        # i_last,j_last are last elements's diretory coordinate

        TempRefRTD2dir = self.AlarmRTD2dir

        TempRTD2dir = self.AlarmRTD2dir

        # l_RTD1_max is max number of column

        l_RTD2 = 0
        k_RTD2 = 0

        # i_RTD1_max = 3
        # j_RTD1_max = 5
        # i_PT_max = 4
        # j_PT_max = 5
        # l_RTD1_max = 4
        # l_PT_max = 4
        # i_RTD1_last = 2
        # j_RTD1_last = 4
        # i_PT_last = 3
        # j_PT_last = 1

        i_RTD2_max = len(self.AlarmRTD2dir)
        j_RTD2_max = len(self.AlarmRTD2dir[0])

        i_RTD2_last = len(self.AlarmRTD2dir) - 1
        j_RTD2_last = len(self.AlarmRTD2dir[i_RTD2_last]) - 1


        l_RTD2_max = j_RTD2_max - 1

        # RTD1 put alarm true widget to the begining of the diretory

        for i in range(0, i_RTD2_max):
            for j in range(0, j_RTD2_max):
                if TempRefRTD2dir[i][j].Alarm:
                    TempRTD2dir[k_RTD2][l_RTD2] = TempRefRTD2dir[i][j]
                    l_RTD2 = l_RTD2 + 1
                    if l_RTD2 == l_RTD2_max+1:
                        l_RTD2 = 0
                        k_RTD2 = k_RTD2 + 1
                if (i, j) == (i_RTD2_last, j_RTD2_last):
                    break
            if (i, j) == (i_RTD2_last, j_RTD2_last):
                break

        # RTD2 put alarm false widget after that
        for i in range(0, i_RTD2_max):
            for j in range(0, j_RTD2_max):
                if not TempRefRTD2dir[i][j].Alarm:
                    TempRTD2dir[k_RTD2][l_RTD2] = TempRefRTD2dir[i][j]
                    l_RTD2 = l_RTD2 + 1
                    if l_RTD2 == l_RTD2_max+1:
                        l_RTD2 = 0
                        k_RTD2 = k_RTD2 + 1
                if (i, j) == (i_RTD2_last, j_RTD2_last):
                    break
            if (i, j) == (i_RTD2_last, j_RTD2_last):
                break


        # Reassign position
        # end the position generator when i= last element's row number, j= last element's column number

        for i in range(0, i_RTD2_max):
            for j in range(0, j_RTD2_max):
                self.GLRTD2.addWidget(TempRTD2dir[i][j], i, j)
                if (i, j) == (i_RTD2_last, j_RTD2_last):
                    break
            if (i, j) == (i_RTD2_last, j_RTD2_last):
                break


    @QtCore.Slot()
    def ReassignRTD3Order(self):
        # check the status of the Widget and reassign the diretory
        # establish 2 diretory, reorder TempDic to reorder the widgets
        # k,l are pointers in the TempDic, ij are pointers in TempRefDic
        # i_max, j_max are max row and column number
        # l max are max column number+1
        # i_last,j_last are last elements's diretory coordinate

        TempRefRTD3dir = self.AlarmRTD3dir

        TempRTD3dir = self.AlarmRTD3dir

        # l_RTD1_max is max number of column

        l_RTD3 = 0
        k_RTD3 = 0

        # i_RTD1_max = 3
        # j_RTD1_max = 5
        # i_PT_max = 4
        # j_PT_max = 5
        # l_RTD1_max = 4
        # l_PT_max = 4
        # i_RTD1_last = 2
        # j_RTD1_last = 4
        # i_PT_last = 3
        # j_PT_last = 1
        i_RTD3_max = len(self.AlarmRTD3dir)
        j_RTD3_max = len(self.AlarmRTD3dir[0])

        i_RTD3_last = len(self.AlarmRTD3dir) - 1
        j_RTD3_last = len(self.AlarmRTD3dir[i_RTD3_last]) - 1

        l_RTD3_max = j_RTD3_max - 1

        for i in range(0, i_RTD3_max):
            for j in range(0, j_RTD3_max):
                if TempRefRTD3dir[i][j].Alarm:
                    TempRTD3dir[k_RTD3][l_RTD3] = TempRefRTD3dir[i][j]
                    l_RTD3 = l_RTD3 + 1
                    if l_RTD3 == l_RTD3_max+1:
                        l_RTD3 = 0
                        k_RTD3 = k_RTD3 + 1
                if (i, j) == (i_RTD3_last, j_RTD3_last):
                    break
            if (i, j) == (i_RTD3_last, j_RTD3_last):
                break

        # RTD3 put alarm false widget after that
        for i in range(0, i_RTD3_max):
            for j in range(0, j_RTD3_max):
                if not TempRefRTD3dir[i][j].Alarm:
                    TempRTD3dir[k_RTD3][l_RTD3] = TempRefRTD3dir[i][j]
                    l_RTD3 = l_RTD3 + 1
                    if l_RTD3 == l_RTD3_max+1:
                        l_RTD3 = 0
                        k_RTD3 = k_RTD3 + 1
                if (i, j) == (i_RTD3_last, j_RTD3_last):
                    break
            if (i, j) == (i_RTD3_last, j_RTD3_last):
                break


        # Reassign position
        # end the position generator when i= last element's row number, j= last element's column number


        for i in range(0, i_RTD3_max):
            for j in range(0, j_RTD3_max):
                self.GLRTD3.addWidget(TempRTD3dir[i][j], i, j)
                if (i, j) == (i_RTD3_last, j_RTD3_last):
                    break
            if (i, j) == (i_RTD3_last, j_RTD3_last):
                break

    @QtCore.Slot()
    def ReassignRTD4Order(self):
        # check the status of the Widget and reassign the diretory
        # establish 2 diretory, reorder TempDic to reorder the widgets
        # k,l are pointers in the TempDic, ij are pointers in TempRefDic
        # i_max, j_max are max row and column number
        # l max are max column number+1
        # i_last,j_last are last elements's diretory coordinate

        TempRefRTD4dir = self.AlarmRTD4dir

        TempRTD4dir = self.AlarmRTD4dir

        # l_RTD1_max is max number of column

        l_RTD4 = 0
        k_RTD4 = 0

        # i_RTD1_max = 3
        # j_RTD1_max = 5
        # i_PT_max = 4
        # j_PT_max = 5
        # l_RTD1_max = 4
        # l_PT_max = 4
        # i_RTD1_last = 2
        # j_RTD1_last = 4
        # i_PT_last = 3
        # j_PT_last = 1

        i_RTD4_max = len(self.AlarmRTD4dir)
        j_RTD4_max = len(self.AlarmRTD4dir[0])

        i_RTD4_last = len(self.AlarmRTD4dir) - 1
        j_RTD4_last = len(self.AlarmRTD4dir[i_RTD4_last]) - 1

        l_RTD4_max = j_RTD4_max - 1

        for i in range(0, i_RTD4_max):
            for j in range(0, j_RTD4_max):
                if TempRefRTD4dir[i][j].Alarm:
                    TempRTD4dir[k_RTD4][l_RTD4] = TempRefRTD4dir[i][j]
                    l_RTD4 = l_RTD4 + 1
                    if l_RTD4 == l_RTD4_max+1:
                        l_RTD4 = 0
                        k_RTD4 = k_RTD4 + 1
                if (i, j) == (i_RTD4_last, j_RTD4_last):
                    break
            if (i, j) == (i_RTD4_last, j_RTD4_last):
                break

        # RTD4 put alarm false widget after that
        for i in range(0, i_RTD4_max):
            for j in range(0, j_RTD4_max):
                if not TempRefRTD4dir[i][j].Alarm:
                    TempRTD4dir[k_RTD4][l_RTD4] = TempRefRTD4dir[i][j]
                    l_RTD4 = l_RTD4 + 1
                    if l_RTD4 == l_RTD4_max+1:
                        l_RTD4 = 0
                        k_RTD4 = k_RTD4 + 1
                if (i, j) == (i_RTD4_last, j_RTD4_last):
                    break
            if (i, j) == (i_RTD4_last, j_RTD4_last):
                break


        # Reassign position
        # end the position generator when i= last element's row number, j= last element's column number

            # for i in range(0, i_RTD4_max):
            for j in range(0, j_RTD4_max):
                self.GLRTD4.addWidget(TempRTD4dir[i][j], i, j)
                if (i, j) == (i_RTD4_last, j_RTD4_last):
                    break
            if (i, j) == (i_RTD4_last, j_RTD4_last):
                break
        # end the position generator when i= last element's row number, j= last element's column number


    @QtCore.Slot()
    def ReassignRTDLEFTOrder(self):
        # check the status of the Widget and reassign the diretory
        # establish 2 diretory, reorder TempDic to reorder the widgets
        # k,l are pointers in the TempDic, ij are pointers in TempRefDic
        # i_max, j_max are max row and column number
        # l max are max column number+1
        # i_last,j_last are last elements's diretory coordinate


        TempRefRTDLEFTdir = self.AlarmRTDLEFTdir


        TempRTDLEFTdir = self.AlarmRTDLEFTdir

        # l_RTD1_max is max number of column

        l_RTDLEFT = 0
        k_RTDLEFT = 0


        # i_RTD1_max = 3
        # j_RTD1_max = 5
        # i_PT_max = 4
        # j_PT_max = 5
        # l_RTD1_max = 4
        # l_PT_max = 4
        # i_RTD1_last = 2
        # j_RTD1_last = 4
        # i_PT_last = 3
        # j_PT_last = 1

        i_RTDLEFT_max = len(self.AlarmRTDLEFTdir)
        j_RTDLEFT_max = len(self.AlarmRTDLEFTdir[0])

        i_RTDLEFT_last = len(self.AlarmRTDLEFTdir) - 1
        j_RTDLEFT_last = len(self.AlarmRTDLEFTdir[i_RTDLEFT_last]) - 1

        l_RTDLEFT_max = j_RTDLEFT_max - 1

        for i in range(0, i_RTDLEFT_max):
            for j in range(0, j_RTDLEFT_max):
                if TempRefRTDLEFTdir[i][j].Alarm:
                    TempRTDLEFTdir[k_RTDLEFT][l_RTDLEFT] = TempRefRTDLEFTdir[i][j]
                    l_RTDLEFT = l_RTDLEFT + 1
                    if l_RTDLEFT == l_RTDLEFT_max+1:
                        l_RTDLEFT = 0
                        k_RTDLEFT = k_RTDLEFT + 1
                if (i, j) == (i_RTDLEFT_last, j_RTDLEFT_last):
                    break
            if (i, j) == (i_RTDLEFT_last, j_RTDLEFT_last):
                break

        # RTDLEFT put alarm false widget after that
        for i in range(0, i_RTDLEFT_max):
            for j in range(0, j_RTDLEFT_max):
                if not TempRefRTDLEFTdir[i][j].Alarm:
                    TempRTDLEFTdir[k_RTDLEFT][l_RTDLEFT] = TempRefRTDLEFTdir[i][j]
                    l_RTDLEFT = l_RTDLEFT + 1
                    if l_RTDLEFT == l_RTDLEFT_max+1:
                        l_RTDLEFT = 0
                        k_RTDLEFT = k_RTDLEFT + 1
                if (i, j) == (i_RTDLEFT_last, j_RTDLEFT_last):
                    break
            if (i, j) == (i_RTDLEFT_last, j_RTDLEFT_last):
                break

        # Reassign position
        # end the position generator when i= last element's row number, j= last element's column number
        for i in range(0, i_RTDLEFT_max):
            for j in range(0, j_RTDLEFT_max):
                self.GLRTDLEFT.addWidget(TempRTDLEFTdir[i][j], i, j)
                if (i, j) == (i_RTDLEFT_last, j_RTDLEFT_last):
                    break
            if (i, j) == (i_RTDLEFT_last, j_RTDLEFT_last):
                break

        # end the position generator when i= last element's row number, j= last element's column number

    @QtCore.Slot()
    def ReassignPTOrder(self):
        # check the status of the Widget and reassign the diretory
        # establish 2 diretory, reorder TempDic to reorder the widgets
        # k,l are pointers in the TempDic, ij are pointers in TempRefDic
        # i_max, j_max are max row and column number
        # l max are max column number+1
        # i_last,j_last are last elements's diretory coordinate


        TempRefPTdir = self.AlarmPTdir

        TempPTdir = self.AlarmPTdir
        # l_RTD1_max is max number of column

        l_PT = 0
        k_PT = 0
        # i_RTD1_max = 3
        # j_RTD1_max = 5
        # i_PT_max = 4
        # j_PT_max = 5
        # l_RTD1_max = 4
        # l_PT_max = 4
        # i_RTD1_last = 2
        # j_RTD1_last = 4
        # i_PT_last = 3
        # j_PT_last = 1

        i_PT_max = len(self.AlarmPTdir)
        # which is 4
        j_PT_max = len(self.AlarmPTdir[0])
        # which is 5

        i_PT_last = len(self.AlarmPTdir) - 1
        # which is 3
        j_PT_last = len(self.AlarmPTdir[i_PT_last]) - 1
        # which is 1

        l_PT_max = j_PT_max - 1

        # PT
        for i in range(0, i_PT_max):
            for j in range(0, j_PT_max):
                if TempRefPTdir[i][j].Alarm:
                    TempPTdir[k_PT][l_PT] = TempRefPTdir[i][j]
                    l_PT = l_PT + 1
                    if l_PT == l_PT_max+1:
                        l_PT = 0
                        k_PT = k_PT + 1
                if (i, j) == (i_PT_last, j_PT_last):
                    break
            if (i, j) == (i_PT_last, j_PT_last):
                break

        for i in range(0, i_PT_max):
            for j in range(0, j_PT_max):
                if not TempRefPTdir[i][j].Alarm:
                    TempPTdir[k_PT][l_PT] = TempRefPTdir[i][j]
                    l_PT = l_PT + 1
                    if l_PT == l_PT_max+1:
                        l_PT = 0
                        k_PT = k_PT + 1
                    if (i, j) == (i_PT_last, j_PT_last):
                        break
                if (i, j) == (i_PT_last, j_PT_last):
                    break

        # Reassign position
        # end the position generator when i= last element's row number, j= last element's column number

        # end the position generator when i= last element's row number, j= last element's column number
        for i in range(0, i_PT_max):
            for j in range(0, j_PT_max):
                self.GLPT.addWidget(TempPTdir[i][j], i, j)
                if (i, j) == (i_PT_last, j_PT_last):
                    break
            if (i, j) == (i_PT_last, j_PT_last):
                break


class HeaterSubWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(1700*R, 600*R)
        self.setMinimumSize(1700*R, 600*R)
        self.setWindowTitle("Detailed Information")

        self.Widget = QtWidgets.QWidget(self)
        self.Widget.setGeometry(QtCore.QRect(0*R, 0*R, 1700*R, 600*R))

        # Groupboxs for alarm/PT/TT

        self.GLWR = QtWidgets.QHBoxLayout()
        self.GLWR.setContentsMargins(20 * R, 20 * R, 20 * R, 20 * R)
        self.GLWR.setSpacing(20 * R)
        self.GLWR.setAlignment(QtCore.Qt.AlignCenter)

        self.GroupWR = QtWidgets.QGroupBox(self.Widget)
        self.GroupWR.setTitle("Write")
        self.GroupWR.setLayout(self.GLWR)
        self.GroupWR.move(0 * R, 0 * R)

        self.GLRD = QtWidgets.QHBoxLayout()
        self.GLRD.setContentsMargins(20 * R, 20 * R, 20 * R, 20 * R)
        self.GLRD.setSpacing(20 * R)
        self.GLRD.setAlignment(QtCore.Qt.AlignCenter)

        self.GroupRD = QtWidgets.QGroupBox(self.Widget)
        self.GroupRD.setTitle("Read")
        self.GroupRD.setLayout(self.GLRD)
        self.GroupRD.move(0 * R, 240 * R)

        self.Label = QtWidgets.QPushButton(self.GroupWR)
        self.Label.setObjectName("Label")
        self.Label.setText("Indicator")
        self.Label.setGeometry(QtCore.QRect(0 * R, 0 * R, 40 * R, 70 * R))
        self.Label.setStyleSheet("QPushButton {" + TITLE_STYLE + "}")
        self.GLWR.addWidget(self.Label)

        self.ButtonGroup = ButtonGroup(self.GroupWR)
        self.GLWR.addWidget(self.ButtonGroup)


        self.Mode = DoubleButton(self.GroupWR)
        self.Mode.Label.setText("Mode")
        self.GLWR.addWidget(self.Mode)

        self.LOSP = SetPoint(self.GroupWR)
        self.LOSP.Label.setText("LO SET")
        self.GLWR.addWidget(self.LOSP)

        self.HISP = SetPoint(self.GroupWR)
        self.HISP.Label.setText("HI SET")
        self.GLWR.addWidget(self.HISP)


        self.SP = SetPoint(self.GroupWR)
        self.SP.Label.setText("SetPoint")
        self.GLWR.addWidget(self.SP)

        self.updatebutton = QtWidgets.QPushButton(self.GroupWR)
        self.updatebutton.setText("Update")
        self.updatebutton.setGeometry(QtCore.QRect(0 * R, 0 * R, 40 * R, 70 * R))
        self.GLWR.addWidget(self.updatebutton)

        self.Interlock = ColoredStatus(self.GroupRD, mode = 1)
        self.Interlock.Label.setText("INTLCK")
        self.GLRD.addWidget(self.Interlock)

        self.Error = ColoredStatus(self.GroupRD, mode = 1)
        self.Error.Label.setText("ERR")
        self.GLRD.addWidget(self.Error)

        self.MANSP = ColoredStatus(self.GroupRD, mode = 2)
        self.MANSP.Label.setText("MAN")
        self.GLRD.addWidget(self.MANSP)

        self.SAT = ColoredStatus(self.GroupRD, mode = 1)
        self.SAT.Label.setText("SAT")
        self.GLRD.addWidget(self.SAT)

        self.ModeREAD = Indicator(self.GroupRD)
        self.ModeREAD.Label.setText("Mode")
        self.GLRD.addWidget(self.ModeREAD)

        self.EN = ColoredStatus(self.GroupRD, mode = 4)
        self.EN.Label.setText("ENABLE")
        self.GLRD.addWidget(self.EN)

        self.Power = Control(self.GroupRD)
        self.Power.Label.setText("Power")
        self.Power.SetUnit(" %")
        self.Power.Max = 100.
        self.Power.Min = 0.
        self.Power.Step = 0.1
        self.Power.Decimals = 1
        self.GLRD.addWidget(self.Power)

        self.IN = Indicator(self.GroupRD)
        self.IN.Label.setText("IN")
        self.GLRD.addWidget(self.IN)

        self.LOW = Indicator(self.GroupRD)
        self.LOW.Label.setText("LOW")
        self.GLRD.addWidget(self.LOW)

        self.HIGH = Indicator(self.GroupRD)
        self.HIGH.Label.setText("HIGH")
        self.GLRD.addWidget(self.HIGH)


        self.SETSP = Indicator(self.GroupRD)
        self.SETSP.Label.setText("SP")
        self.GLRD.addWidget(self.SETSP)

        self.RTD1 = Indicator(self.GroupRD)
        self.RTD1.Label.setText("RTD1")
        self.GLRD.addWidget(self.RTD1)

        self.RTD2 = Indicator(self.GroupRD)
        self.RTD2.Label.setText("RTD2")
        self.GLRD.addWidget(self.RTD2)

        self.RTD3 = Indicator(self.GroupRD)
        self.RTD3.Label.setText("RTD3")
        self.GLRD.addWidget(self.RTD3)

        self.RTD4 = Indicator(self.GroupRD)
        self.RTD4.Label.setText("RTD4")
        self.GLRD.addWidget(self.RTD4)

        self.RTD5 = Indicator(self.GroupRD)
        self.RTD5.Label.setText("RTD5")
        self.GLRD.addWidget(self.RTD5)

        self.RTD6 = Indicator(self.GroupRD)
        self.RTD6.Label.setText("RTD6")
        self.GLRD.addWidget(self.RTD6)



# Define a function tab that shows the status of the widgets

class MultiStatusIndicator(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("MutiStatusIndicator")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 200*R, 100*R))
        self.setMinimumSize(200*R, 100*R)
        self.setSizePolicy(sizePolicy)

        self.VL = QtWidgets.QVBoxLayout(self)
        self.VL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.setSpacing(3)

        self.Label = QtWidgets.QLabel(self)
        self.Label.setMinimumSize(QtCore.QSize(10*R, 10*R))
        self.Label.setStyleSheet("QLabel {" +TITLE_STYLE + BORDER_STYLE+"}")
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setText("Label")
        self.VL.addWidget(self.Label)

        self.HL = QtWidgets.QHBoxLayout()
        self.HL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.addLayout(self.HL)

        self.Interlock = ColoredStatus(self, 2)
        self.Interlock.Label.setText("INTLKD")
        self.HL.addWidget(self.Interlock)

        self.Manual = ColoredStatus(self, 2)
        self.Manual.Label.setText("MAN")
        self.HL.addWidget(self.Manual)

        self.Error = ColoredStatus(self, 1)
        self.Error.Label.setText("ERR")
        self.HL.addWidget(self.Error)


# Define an alarm button
class AlarmButton(QtWidgets.QWidget):
    def __init__(self, Window, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.Signals = ChangeValueSignal()

        self.setObjectName("AlarmButton")
        self.setGeometry(QtCore.QRect(5*R, 5*R, 250*R, 80*R))
        self.setMinimumSize(250*R, 80*R)
        self.setSizePolicy(sizePolicy)

        # link the button to a new window
        self.SubWindow = Window

        self.Button = QtWidgets.QPushButton(self)
        self.Button.setObjectName("Button")
        self.Button.setText("Button")
        self.Button.setGeometry(QtCore.QRect(5*R, 5*R, 245*R, 75*R))
        self.Button.setStyleSheet(
            "QWidget{" + LABEL_STYLE + "} QWidget[Alarm = true]{ background-color: rgb(255,132,27);} "
                                       "QWidget[Alarm = false]{ background-color: rgb(204,204,204);}")

        self.Button.setProperty("Alarm", False)
        self.Button.Alarm = False
        self.Button.clicked.connect(self.ButtonClicked)
        self.Collected = False

    @QtCore.Slot()
    def ButtonClicked(self):
        self.SubWindow.show()
        # self.Signals.sSignal.emit(self.Button.text())

    @QtCore.Slot()
    def ButtonAlarmSetSignal(self):
        self.Button.setProperty("Alarm", True)
        self.Button.setStyle(self.Button.style())

    @QtCore.Slot()
    def ButtonAlarmResetSignal(self):
        self.Button.setProperty("Alarm", False)
        self.Button.setStyle(self.Button.style())


    @QtCore.Slot()
    def CollectAlarm(self, list):
        # self.Collected=False
        # for i in range(len(list)):
        #     # calculate collected alarm status
        #     self.Collected = self.Collected or list[i].Alarm
        # self.Button.Alarm = self.Collected
        if True in list:
            self.Button.Alarm = True
        else:
            self.Button.Alarm = False



# Define a function tab that shows the status of the widgets
class FunctionButton(QtWidgets.QWidget):
    def __init__(self, Window, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.Signals = ChangeValueSignal()

        self.setObjectName("FunctionButton")
        self.setGeometry(QtCore.QRect(5*R, 5*R, 250*R, 80*R))
        self.setMinimumSize(250*R, 80*R)
        self.setSizePolicy(sizePolicy)

        # link the button to a new window
        self.SubWindow = Window

        self.Button = QtWidgets.QPushButton(self)
        self.Button.setObjectName("Button")
        self.Button.setText("Button")
        self.Button.setGeometry(QtCore.QRect(5*R, 5*R, 245*R, 75*R))
        self.Button.clicked.connect(self.ButtonClicked)
        self.Button.setStyleSheet("QPushButton {" +LABEL_STYLE+"}")

    @QtCore.Slot()
    def ButtonClicked(self):
        self.SubWindow.show()
        # self.Signals.sSignal.emit(self.Button.text())


# Defines a reusable layout containing widgets

class Chiller(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.VL = QtWidgets.QVBoxLayout(self)
        self.VL.setContentsMargins(0*R, 0*R, 0*R, 0*R)

        self.Label = QtWidgets.QLabel(self)
        self.Label.setMinimumSize(QtCore.QSize(30*R, 30*R))
        self.Label.setStyleSheet("QLabel {" +TITLE_STYLE+"}")
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setText("Label")
        self.VL.addWidget(self.Label)

        self.HL = QtWidgets.QHBoxLayout()
        self.HL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.addLayout(self.HL)

        self.State = Toggle(self)
        self.State.Label.setText("State")
        self.HL.addWidget(self.State)

        self.Setpoint = Control(self)
        self.Setpoint.Label.setText("Setpoint")
        self.HL.addWidget(self.Setpoint)

        self.Temp = Indicator(self)
        self.Temp.Label.setText("Temp")
        self.HL.addWidget(self.Temp)


# Defines a reusable layout containing widgets
class Heater(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.VL = QtWidgets.QVBoxLayout(self)
        self.VL.setContentsMargins(0*R, 0*R, 0*R, 0*R)

        self.Label = QtWidgets.QPushButton(self)
        self.Label.setMinimumSize(QtCore.QSize(30*R, 30*R))
        self.Label.setStyleSheet("QPushButton {" +TITLE_STYLE+BORDER_STYLE+"}")
        self.Label.setText("Label")
        self.VL.addWidget(self.Label)

        # Add a Sub window popped out when click the name
        self.HeaterSubWindow = HeaterSubWindow(self)
        self.Label.clicked.connect(self.PushButton)

        self.HL = QtWidgets.QHBoxLayout()
        self.HL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.addLayout(self.HL)

        self.State = DoubleButton(self)
        self.State.Label.setText("State")
        self.State.LButton.setText("On")
        self.State.RButton.setText("Off")
        self.HL.addWidget(self.State)

        self.Power = Control(self)
        self.Power.Label.setText("Power")
        self.Power.SetUnit(" %")
        self.Power.Max = 100.
        self.Power.Min = 0.
        self.Power.Step = 0.1
        self.Power.Decimals = 1
        self.HL.addWidget(self.Power)

    def PushButton(self):
        self.HeaterSubWindow.show()


# Defines a reusable layout containing widgets
class AOMultiLoop(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.VL = QtWidgets.QVBoxLayout(self)
        self.VL.setContentsMargins(0*R, 0*R, 0*R, 0*R)

        self.Label = QtWidgets.QPushButton(self)
        self.Label.setMinimumSize(QtCore.QSize(30*R, 30*R))
        self.Label.setStyleSheet("QLabel {" +TITLE_STYLE + BORDER_STYLE+"}")
        self.Label.setText("Label")
        self.VL.addWidget(self.Label)

        # Add a Sub window popped out when click the name
        self.HeaterSubWindow = HeaterSubWindow(self)
        self.Label.clicked.connect(self.PushButton)

        self.HL = QtWidgets.QHBoxLayout()
        self.HL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.addLayout(self.HL)

        self.Mode = Menu(self)
        self.Mode.Label.setText("Mode")
        self.HL.addWidget(self.Mode)

        self.Power = Control(self)
        self.Power.Label.setText("Power")
        self.Power.SetUnit(" %")
        self.Power.Max = 100.
        self.Power.Min = 0.
        self.Power.Step = 0.1
        self.Power.Decimals = 1
        self.HL.addWidget(self.Power)

    def PushButton(self):
        self.HeaterSubWindow.show()


# Defines a reusable layout containing widgets
class AOMutiLoopExpand(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setObjectName("AOMutiLoop")
        self.setGeometry(QtCore.QRect(0*R, 0*R, 1050*R, 80*R))
        self.setMinimumSize(1050*R, 80*R)
        self.setSizePolicy(sizePolicy)

        self.VL = QtWidgets.QVBoxLayout(self)
        self.VL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.setSpacing(5*R)

        self.Label = QtWidgets.QLabel(self)
        self.Label.setMinimumSize(QtCore.QSize(30*R, 30*R))
        self.Label.setStyleSheet("QLabel {" +TITLE_STYLE + BORDER_STYLE+"}")
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setText("Label")
        self.VL.addWidget(self.Label)

        self.HL = QtWidgets.QHBoxLayout()
        self.HL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.addLayout(self.HL)

        self.Mode = DoubleButton(self)
        self.Mode.Label.setText("Mode")
        self.HL.addWidget(self.Mode)

        self.FBSwitch = Menu(self)
        self.FBSwitch.Label.setText("FBSWITCH")
        self.HL.addWidget(self.FBSwitch)

        self.SP = SetPoint(self)
        self.SP.Label.setText("SetPoint")
        self.HL.addWidget(self.SP)

        self.MANSP = SetPoint(self)
        self.MANSP.Label.setText("Manual SetPoint")
        self.HL.addWidget(self.MANSP)

        self.Power = Control(self)
        self.Power.Label.setText("Power")
        self.Power.SetUnit(" %")
        self.Power.Max = 100.
        self.Power.Min = 0.
        self.Power.Step = 0.1
        self.Power.Decimals = 1
        self.HL.addWidget(self.Power)

        self.RTD1 = Indicator(self)
        self.RTD1.Label.setText("RTD1")
        self.HL.addWidget(self.RTD1)

        self.RTD2 = Indicator(self)
        self.RTD2.Label.setText("RTD2")
        self.HL.addWidget(self.RTD2)

        self.Interlock = ColoredStatus(self)
        self.Interlock.Label.setText("INTLCK")
        self.HL.addWidget(self.Interlock)

        self.Error = ColoredStatus(self)
        self.Error.Label.setText("ERR")
        self.HL.addWidget(self.Error)

        self.HIGH = SetPoint(self)
        self.HIGH.Label.setText("HIGH")
        self.HL.addWidget(self.HIGH)

        self.LOW = SetPoint(self)
        self.LOW.Label.setText("LOW")
        self.HL.addWidget(self.LOW)


# Defines a reusable layout containing widget
class Valve(QtWidgets.QWidget):
    def __init__(self, parent=None, mode=0):
        super().__init__(parent)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.VL = QtWidgets.QVBoxLayout(self)
        self.VL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.setSpacing(3)

        self.Label = QtWidgets.QLabel(self)
        # self.Label.setMinimumSize(QtCore.QSize(30*R, 30*R))
        self.Label.setMinimumSize(QtCore.QSize(10*R, 10*R))
        self.Label.setStyleSheet("QLabel {" +TITLE_STYLE + BORDER_STYLE+"}")
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setText("Label")
        self.VL.addWidget(self.Label)

        self.HL = QtWidgets.QHBoxLayout()
        self.HL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.addLayout(self.HL)

        self.Set = DoubleButton(self)
        self.Set.Label.setText("Set")
        self.Set.LButton.setText("open")
        self.Set.RButton.setText("close")
        self.HL.addWidget(self.Set)

        self.ActiveState = ColoredStatus(self, mode)
        # self.ActiveState = ColorIndicator(self) for test the function
        self.ActiveState.Label.setText("Status")
        self.HL.addWidget(self.ActiveState)


# Defines a reusable layout containing widgets
class Camera(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.VL = QtWidgets.QVBoxLayout(self)
        self.VL.setContentsMargins(0*R, 0*R, 0*R, 0*R)

        self.Label = QtWidgets.QLabel(self)
        self.Label.setMinimumSize(QtCore.QSize(30*R, 30*R))
        self.Label.setStyleSheet("QLabel {" +TITLE_STYLE+"}")
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setText("Label")
        self.VL.addWidget(self.Label)

        self.HL = QtWidgets.QHBoxLayout()
        self.HL.setContentsMargins(0*R, 0*R, 0*R, 0*R)
        self.VL.addLayout(self.HL)

        self.Temp = Indicator(self)
        self.Temp.Label.setText("Temp")
        self.HL.addWidget(self.Temp)

        self.LED1 = Indicator(self)
        self.LED1.Label.setText("LED 1")
        self.HL.addWidget(self.LED1)

        self.LED2 = Indicator(self)
        self.LED2.Label.setText("LED 2")
        self.HL.addWidget(self.LED2)

        self.Humidity = Indicator(self)
        self.Humidity.Label.setText("Humidity")
        self.Humidity.Unit = " %"
        self.HL.addWidget(self.Humidity)

        self.Air = Indicator(self)
        self.Air.Label.setText("Air")
        self.HL.addWidget(self.Air)



class ChangeValueSignal(QtCore.QObject):
    fSignal = QtCore.Signal(float)
    bSignal = QtCore.Signal(bool)
    sSignal = QtCore.Signal(str)