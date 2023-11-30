"""
This is the main SlowDAQ code used to read/setproperties of the TPLC and PPLC

By: Mathieu Laurin

v0.1.0 Initial code 29/11/19 ML
v0.1.1 Read and write implemented 08/12/19 ML
v0.1.2 Alarm implemented 07/01/20 ML
v0.1.3 PLC online detection, poll PLCs only when values are updated, fix Centos window size bug 04/03/20 ML
"""

import os, sys, time, platform, datetime, random, pickle, cgitb, traceback, signal, copy

from PySide2 import QtWidgets, QtCore, QtGui

# from SlowDAQ_SBC_v2 import *
# from PLC import *
from PICOPW import VerifyPW
from SlowDAQWidgets_UCSB_v3 import *
import zmq
import slowcontrol_env_cons as sec

VERSION = "v2.1.3"
# if platform.system() == "Linux":
#     QtGui.QFontDatabase.addApplicationFont("/usr/share/fonts/truetype/vista/calibrib.ttf")
#     SMALL_LABEL_STYLE = "background-color: rgb(204,204,204);  font-family: calibrib;" \
#                         " font-size: 10px;" \
#                         " font-weight: bold;"
#     LABEL_STYLE = "background-color: rgb(204,204,204);  font-family: calibrib; " \
#                   "font-size: 12px; "
#     TITLE_STYLE = "background-color: rgb(204,204,204);  font-family: calibrib;" \
#                   " font-size: 14px; "


# Settings adapted to sbc slowcontrol machine
SMALL_LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Calibri\";" \
                    " font-size: 10px;" \
                    " font-weight: bold;"
LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Calibri\"; " \
              "font-size: 12px; font-weight: bold;"
TITLE_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Calibri\";" \
              " font-size: 14px; font-weight: bold;"

BORDER_STYLE = " border-radius: 2px; border-color: black;"

ADMIN_TIMER = 30000
PLOTTING_SCALE = 0.66
ADMIN_PASSWORD = "60b6a2988e4ee1ad831ad567ad938adcc8e294825460bbcab26c1948b935bdf133e9e2c98ad4eafc622f4" \
                 "f5845cf006961abcc0a4007e3ac87d26c8981b792259f3f4db207dc14dbff315071c2f419122f1367668" \
                 "31c12bff0da3a2314ca2266"

R = 0.6  # Resolution settings

sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    print("ExceptType: ", exctype, "Value: ", value, "Traceback: ", traceback)
    # sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = exception_hook


def sendKillSignal(etype, value, tb):
    print('KILL ALL')
    traceback.print_exception(etype, value, tb)
    os.kill(os.getpid(), signal.SIGKILL)


original_init = QtCore.QThread.__init__


def patched_init(self, *args, **kwargs):
    print("thread init'ed")
    original_init(self, *args, **kwargs)
    original_run = self.run

    def patched_run(*args, **kwargs):
        try:
            original_run(*args, **kwargs)
        except:
            sys.excepthook(*sys.exc_info())

    self.run = patched_run


QtCore.QThread.__init__ = patched_init


def install():
    sys._excepthook = sys.excepthook
    sys.excepthook = sendKillSignal
    QtCore.QThread.__init__ = patched_init


def TwoD_into_OneD(Twod_array):
    Oned_array = []
    i_max = len(Twod_array)
    j_max = len(Twod_array[0])
    i_last = len(Twod_array) - 1
    j_last = len(Twod_array[i_last]) - 1
    for i in range(0, i_max):
        for j in range(0, j_max):
            Oned_array.append(Twod_array[i][j])
            if (i, j) == (i_last, j_last):
                break
        if (i, j) == (i_last, j_last):
            break
    return Oned_array


# Main class
# This is designed for linux system
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Get background image path
        if '__file__' in globals():
            self.Path = os.path.dirname(os.path.realpath(__file__))
        else:
            self.Path = os.getcwd()
        self.ImagePath = os.path.join(self.Path, "image")
        # print(self.ImagePath)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.resize(2400 * R, 1400 * R)  # Open at center using resized
        self.setMinimumSize(2400 * R, 1400 * R)
        self.setWindowTitle("SlowDAQ " + VERSION)
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.ImagePath, "ucsb_phy.jpg")))

        # Tabs, backgrounds & labels

        self.Tab = QtWidgets.QTabWidget(self)
        self.Tab.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Tab.setStyleSheet("font-weight: bold; font-size: 20px; font-family: Times;")
        self.Tab.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.Tab.setGeometry(QtCore.QRect(0 * R, 0 * R, 2400 * R, 1400 * R))

        self.ThermosyphonTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.ThermosyphonTab, "Thermosyphon Main Panel")

        self.ThermosyphonTab.Background = QtWidgets.QLabel(self.ThermosyphonTab)
        self.ThermosyphonTab.Background.setScaledContents(True)
        self.ThermosyphonTab.Background.setStyleSheet('background-color:black;')
        pixmap_thermalsyphon = QtGui.QPixmap(os.path.join(self.ImagePath, "henry_ts_panel.png"))
        pixmap_thermalsyphon = pixmap_thermalsyphon.scaledToWidth(2400 * R)
        self.ThermosyphonTab.Background.setPixmap(QtGui.QPixmap(pixmap_thermalsyphon))
        self.ThermosyphonTab.Background.move(0 * R, 0 * R)
        self.ThermosyphonTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.GasTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.GasTab, "Gas Panel")

        self.GasTab.Background = QtWidgets.QLabel(self.GasTab)
        self.GasTab.Background.setScaledContents(True)
        self.GasTab.Background.setStyleSheet('background-color:black;')
        pixmap_gas = QtGui.QPixmap(os.path.join(self.ImagePath, "henry_gas_panel.png"))
        pixmap_gas = pixmap_gas.scaledToWidth(2400 * R)
        self.GasTab.Background.setPixmap(QtGui.QPixmap(pixmap_gas))
        self.GasTab.Background.move(0 * R, 0 * R)
        self.GasTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.TubeTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.TubeTab, "Inner Tube")

        self.TubeTab.Background = QtWidgets.QLabel(self.TubeTab)
        self.TubeTab.Background.setScaledContents(True)
        self.TubeTab.Background.setStyleSheet('background-color:black;')
        pixmap_tube = QtGui.QPixmap(os.path.join(self.ImagePath, "henry_tube.png"))
        pixmap_tube = pixmap_tube.scaledToWidth(2400 * R)
        self.TubeTab.Background.setPixmap(QtGui.QPixmap(pixmap_tube))
        self.TubeTab.Background.move(0 * R, 0 * R)
        self.TubeTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.DatanSignalTab = QtWidgets.QWidget(self.Tab)
        self.Tab.addTab(self.DatanSignalTab, "Data and Signal Panel")

        self.DatanSignalTab.Background = QtWidgets.QLabel(self.DatanSignalTab)
        self.DatanSignalTab.Background.setScaledContents(True)
        self.DatanSignalTab.Background.setStyleSheet('background-color:black;')
        pixmap_DatanSignal = QtGui.QPixmap(os.path.join(self.ImagePath, "Default_Background"))
        pixmap_DatanSignal = pixmap_DatanSignal.scaledToWidth(2400 * R)
        self.DatanSignalTab.Background.setPixmap(QtGui.QPixmap(pixmap_DatanSignal))
        self.DatanSignalTab.Background.move(0 * R, 0 * R)
        self.DatanSignalTab.Background.setAlignment(QtCore.Qt.AlignCenter)
        self.DatanSignalTab.Background.setObjectName("DatanSignalBkg")

        # Data saving and recovery
        # Data setting form is ended with .ini and directory is https://doc.qt.io/archives/qtforpython-5.12/PySide2/QtCore/QSettings.html depending on the System
        self.settings = QtCore.QSettings("$HOME/.config//SBC/SlowControl.ini", QtCore.QSettings.IniFormat)

        # Temperature tab buttons

        self.LoginP = SingleButton(self.ThermosyphonTab)
        self.LoginP.move(2150 * R, 100 * R)
        self.LoginP.Label.setText("Login")
        self.LoginP.Button.setText("Guest")

        self.LoginT = SingleButton(self.ThermosyphonTab)
        self.LoginT.move(2250 * R, 100 * R)
        self.LoginT.Label.setText("Login")
        self.LoginT.Button.setText("Guest")

        # Data and Signal Tab
        self.ReadSettings = Loadfile(self.DatanSignalTab)
        self.ReadSettings.move(50 * R, 50 * R)


        self.SaveSettings = CustomSave(self.DatanSignalTab)
        self.SaveSettings.move(700 * R, 50 * R)
        # self.SaveSettings.SaveFileButton.clicked.connect(
        #     lambda x: self.Save(directory=self.SaveSettings.Head, project=self.SaveSettings.Tail))

        # Alarm button
        self.AlarmWindow = AlarmWin()
        self.AlarmButton = AlarmButton(self.AlarmWindow, self)
        self.AlarmButton.SubWindow.resize(1000 * R, 500 * R)
        # self.AlarmButton.StatusWindow.AlarmWindow()

        self.AlarmButton.move(2200 * R, 65 * R)
        # self.AlarmButton.Button.setText("Alarm Button")

        # Thermosyphon Widgets
        self.PV1001 = Valve_v2(self.ThermosyphonTab)
        self.PV1001.Label.setText("PV1001")
        self.PV1001.move(1035 * R, 165 * R)

        self.PV1002 = Valve_v2(self.ThermosyphonTab)
        self.PV1002.Label.setText("PV1002")
        self.PV1002.move(1950 * R, 940 * R)

        self.PV1003 = Valve_v2(self.ThermosyphonTab)
        self.PV1003.Label.setText("PV1003")
        self.PV1003.move(1950 * R, 1150 * R)

        self.PV1004 = Valve_v2(self.ThermosyphonTab)
        self.PV1004.Label.setText("PV1004")
        self.PV1004.move(1700 * R, 1100 * R)

        self.PV1005 = Valve_v2(self.ThermosyphonTab)
        self.PV1005.Label.setText("PV1005")
        self.PV1005.move(1450 * R, 585 * R)

        self.PV1006 = Valve_v2(self.ThermosyphonTab)
        self.PV1006.Label.setText("PV1006")
        self.PV1006.move(1065 * R, 940 * R)

        self.PV1007 = Valve_v2(self.ThermosyphonTab)
        self.PV1007.Label.setText("PV1007")
        self.PV1007.move(1065 * R, 1150 * R)

        self.MFC1008 = LOOPPID_v2(self.ThermosyphonTab)
        self.MFC1008.move(1795 * R, 700 * R)
        self.MFC1008.Label.setText("MFC1008")
        self.MFC1008.LOOPPIDWindow.setWindowTitle("MFC1008")
        self.MFC1008.LOOPPIDWindow.Label.setText("MFC1008")

        self.PT1000 = PressureIndicator(self.ThermosyphonTab)
        self.PT1000.Label.setText("PT1000")
        self.PT1000.move(145 * R, 30 * R)
        self.PT1000.SetUnit(" bar")

        self.PT1001 = PressureIndicator(self.ThermosyphonTab)
        self.PT1001.Label.setText("PT1001")
        self.PT1001.move(155 * R, 975 * R)
        self.PT1001.SetUnit(" bar")

        self.PT1002 = PressureIndicator(self.ThermosyphonTab)
        self.PT1002.Label.setText("PT1002")
        self.PT1002.move(160 * R, 1160 * R)
        self.PT1002.SetUnit(" bar")

        # Gas Panel Widgets

        # self.PNV001 = Valve(self.GasTab)
        # self.PNV001.Label.setText("PNV001")
        # self.PNV001.move(470 * R, 750 * R)

        self.BGA01 = PressureIndicator(self.GasTab)
        self.BGA01.Label.setText("BGA01")
        self.BGA01.move(1350 * R, 350 * R)
        self.BGA01.SetUnit(" %")

        self.BGA02 = PressureIndicator(self.GasTab)
        self.BGA02.Label.setText("BGA02")
        self.BGA02.move(1700 * R, 350 * R)
        self.BGA02.SetUnit(" %")

        self.PT001 = PressureIndicator(self.GasTab)
        self.PT001.Label.setText("PT001")
        self.PT001.move(190 * R, 560 * R)
        self.PT001.SetUnit(" bar")

        self.PT002 = PressureIndicator(self.GasTab)
        self.PT002.Label.setText("PT002")
        self.PT002.move(1073 * R, 445 * R)
        self.PT002.SetUnit(" bar")

        self.PT003 = PressureIndicator(self.GasTab)
        self.PT003.Label.setText("PT003")
        self.PT003.move(1091 * R, 740 * R)
        self.PT003.SetUnit(" bar")

        self.PT004 = PressureIndicator(self.GasTab)
        self.PT004.Label.setText("PT004")
        self.PT004.move(1455 * R, 440 * R)
        self.PT004.SetUnit(" bar")

        """
        self.IDPV1 = PnID_Alone(self.GasTab)
        self.IDPV1.Label.setText("PV1")
        self.IDPV1.move(1360 * R, 800 * R)

        self.IDPV2 = PnID_Alone(self.GasTab)
        self.IDPV2.Label.setText("PV2")
        self.IDPV2.move(1420 * R, 800 * R)

        self.IDPV3 = PnID_Alone(self.GasTab)
        self.IDPV3.Label.setText("PV3")
        self.IDPV3.move(1500 * R, 800 * R)

        self.IDPV4 = PnID_Alone(self.GasTab)
        self.IDPV4.Label.setText("PV4")
        self.IDPV4.move(1580 * R, 800 * R)

        self.IDPV5 = PnID_Alone(self.GasTab)
        self.IDPV5.Label.setText("PV5")
        self.IDPV5.move(1660 * R, 800 * R)

        self.IDPV6 = PnID_Alone(self.GasTab)
        self.IDPV6.Label.setText("PV6")
        self.IDPV6.move(1740 * R, 800 * R)

        self.IDPV7 = PnID_Alone(self.GasTab)
        self.IDPV7.Label.setText("PV7")
        self.IDPV7.move(1820 * R, 800 * R)

        self.IDPV8 = PnID_Alone(self.GasTab)
        self.IDPV8.Label.setText("PV8")
        self.IDPV8.move(1900 * R, 800 * R)

        self.IDPV9 = PnID_Alone(self.GasTab)
        self.IDPV9.Label.setText("PV9")
        self.IDPV9.move(1980 * R, 800 * R)

        self.IDPV10 = PnID_Alone(self.GasTab)
        self.IDPV10.Label.setText("PV10")
        self.IDPV10.move(2060 * R, 800 * R)

        self.IDPV11 = PnID_Alone(self.GasTab)
        self.IDPV11.Label.setText("PV11")
        self.IDPV11.move(2140 * R, 800 * R)
        """

        self.PV1 = Valve_v2(self.GasTab)
        self.PV1.Label.setText("PV1")
        self.PV1.move(895 * R, 960 * R)

        self.PV2 = Valve_v2(self.GasTab)
        self.PV2.Label.setText("PV2")
        self.PV2.move(1840 * R, 415 * R)

        self.PV3 = Valve_v2(self.GasTab)
        self.PV3.Label.setText("PV3")
        self.PV3.move(2200 * R, 492 * R)

        self.PV4 = Valve_v2(self.GasTab)
        self.PV4.Label.setText("PV4")
        self.PV4.move(1840 * R, 569 * R)

        self.PV5 = Valve_v2(self.GasTab)
        self.PV5.Label.setText("PV5")
        self.PV5.move(2200 * R, 646 * R)

        self.PV6 = Valve_v2(self.GasTab)
        self.PV6.Label.setText("PV6")
        self.PV6.move(1840 * R, 723 * R)

        self.PV7 = Valve_v2(self.GasTab)
        self.PV7.Label.setText("PV7")
        self.PV7.move(2200 * R, 800 * R)

        self.PV8 = Valve_v2(self.GasTab)
        self.PV8.Label.setText("PV8")
        self.PV8.move(1840 * R, 877 * R)

        self.PV9 = Valve_v2(self.GasTab)
        self.PV9.Label.setText("PV9")
        self.PV9.move(2200 * R, 954 * R)

        self.PV10 = Valve_v2(self.GasTab)
        self.PV10.Label.setText("PV10")
        self.PV10.move(1840 * R, 1031 * R)

        self.PV11 = Valve_v2(self.GasTab)
        self.PV11.Label.setText("PV11")
        self.PV11.move(2200 * R, 1108 * R)

        self.PV12 = Valve_v2(self.GasTab)
        self.PV12.Label.setText("PV12")
        self.PV12.move(1840 * R, 1185 * R)

        self.MFC1 = LOOPPID_v2(self.GasTab)
        self.MFC1.move(1160 * R, 525 * R)
        self.MFC1.Label.setText("MFC1")
        self.MFC1.LOOPPIDWindow.setWindowTitle("MFC1")
        self.MFC1.LOOPPIDWindow.Label.setText("MFC1")

        self.MFC2 = LOOPPID_v2(self.GasTab)
        self.MFC2.move(1525 * R, 525 * R)
        self.MFC2.Label.setText("MFC2")
        self.MFC2.LOOPPIDWindow.setWindowTitle("MFC2")
        self.MFC2.LOOPPIDWindow.Label.setText("MFC2")

        # inner tube widgets
        self.RTD1 = Indicator(self.TubeTab)
        self.RTD1.Label.setText("RTD1")
        self.RTD1.move(145 * R, 30 * R)

        self.RTD2 = Indicator(self.TubeTab)
        self.RTD2.Label.setText("RTD2")
        self.RTD2.move(145 * R, 30 * R)

        self.RTD3 = Indicator(self.TubeTab)
        self.RTD3.Label.setText("RTD3")
        self.RTD3.move(145 * R, 30 * R)

        self.RTD4 = Indicator(self.TubeTab)
        self.RTD4.Label.setText("RTD4")
        self.RTD4.move(145 * R, 30 * R)

        self.RTD5 = Indicator(self.TubeTab)
        self.RTD5.Label.setText("RTD5")
        self.RTD5.move(145 * R, 30 * R)

        self.RTD6 = Indicator(self.TubeTab)
        self.RTD6.Label.setText("RTD6")
        self.RTD6.move(145 * R, 30 * R)


        self.RTD7 = Indicator(self.TubeTab)
        self.RTD7.Label.setText("RTD7")
        self.RTD7.move(145 * R, 30 * R)

        self.RTD8 = Indicator(self.TubeTab)
        self.RTD8.Label.setText("RTD8")
        self.RTD8.move(145 * R, 100 * R)

        self.RTD9 = Indicator(self.TubeTab)
        self.RTD9.Label.setText("RTD9")
        self.RTD9.move(145 * R, 170 * R)

        self.RTD10 = Indicator(self.TubeTab)
        self.RTD10.Label.setText("RTD10")
        self.RTD10.move(145 * R, 240 * R)

        self.RTD11 = Indicator(self.TubeTab)
        self.RTD11.Label.setText("RTD11")
        self.RTD11.move(145 * R, 310 * R)

        self.RTD12 = Indicator(self.TubeTab)
        self.RTD12.Label.setText("RTD12")
        self.RTD12.move(145 * R, 380 * R)

        self.LiqLev = Indicator(self.TubeTab)
        self.LiqLev.Label.setText("Liq Lev")
        self.LiqLev.move(145 * R, 450 * R)
        self.LiqLev.SetUnit(" cm")

        self.HTR1001 = LOOPPID_v2(self.TubeTab)
        self.HTR1001.move(295 * R, 30 * R)
        self.HTR1001.Label.setText("Heater1")
        self.HTR1001.LOOPPIDWindow.setWindowTitle("Heater1")
        self.HTR1001.LOOPPIDWindow.Label.setText("Heater1")

        self.HTR1002 = LOOPPID_v2(self.TubeTab)
        self.HTR1002.move(295 * R, 130 * R)
        self.HTR1002.Label.setText("Heater2")
        self.HTR1002.LOOPPIDWindow.setWindowTitle("Heater2")
        self.HTR1002.LOOPPIDWindow.Label.setText("Heater2")

        self.HTR1003 = LOOPPID_v2(self.TubeTab)
        self.HTR1003.move(295 * R, 230 * R)
        self.HTR1003.Label.setText("Heater3")
        self.HTR1003.LOOPPIDWindow.setWindowTitle("Heater3")
        self.HTR1003.LOOPPIDWindow.Label.setText("Heater3")

        self.HTR1004 = LOOPPID_v2(self.TubeTab)
        self.HTR1004.move(295 * R, 330 * R)
        self.HTR1004.Label.setText("Heater4")
        self.HTR1004.LOOPPIDWindow.setWindowTitle("Heater4")
        self.HTR1004.LOOPPIDWindow.Label.setText("Heater4")

        self.H5 = LOOPPID_v2(self.TubeTab)
        self.H5.move(295 * R, 430 * R)
        self.H5.Label.setText("Heater5")
        self.H5.LOOPPIDWindow.setWindowTitle("Heater5")
        self.H5.LOOPPIDWindow.Label.setText("Heater5")

        self.IDHTR1001 = PnID_Alone(self.TubeTab)
        self.IDHTR1001.Label.setText("Heater 1")
        self.IDHTR1001.move(800 * R, 100 * R)

        self.IDHTR1002 = PnID_Alone(self.TubeTab)
        self.IDHTR1002.Label.setText("Heater 2")
        self.IDHTR1002.move(800 * R, 160 * R)

        self.IDHTR1003 = PnID_Alone(self.TubeTab)
        self.IDHTR1003.Label.setText("Heater 3")
        self.IDHTR1003.move(1200 * R, 600 * R)

        self.IDHTR1004 = PnID_Alone(self.TubeTab)
        self.IDHTR1004.Label.setText("Heater 4")
        self.IDHTR1004.move(1342 * R, 705 * R)

        self.IDH5 = PnID_Alone(self.TubeTab)
        self.IDH5.Label.setText("Heater 5")
        self.IDH5.move(1317 * R, 1020 * R)

        self.IDRTD7 = PnID_Alone(self.TubeTab)
        self.IDRTD7.Label.setText("RTD7")
        self.IDRTD7.move(1150 * R, 940 * R)

        self.IDRTD8 = PnID_Alone(self.TubeTab)
        self.IDRTD8.Label.setText("RTD8")
        self.IDRTD8.move(1515 * R, 940 * R)

        self.IDRTD9 = PnID_Alone(self.TubeTab)
        self.IDRTD9.Label.setText("RTD9")
        self.IDRTD9.move(1342 * R, 725 * R)

        self.IDRTD10 = PnID_Alone(self.TubeTab)
        self.IDRTD10.Label.setText("RTD10")
        self.IDRTD10.move(1342 * R, 685 * R)

        self.IDRTD11 = PnID_Alone(self.TubeTab)
        self.IDRTD11.Label.setText("RTD11")
        self.IDRTD11.move(800 * R, 130 * R)

        # self.IDRTD6 = PnID_Alone(self.TubeTab)
        # self.IDRTD6.Label.setText("RTD 6")
        # self.IDRTD6.move(145 * R, 490 * R)

        # commands stack
        self.address = sec.merge_dic(sec.TT_AD1_ADDRESS, sec.TT_AD2_ADDRESS, sec.PT_ADDRESS, sec.LEFT_REAL_ADDRESS,
                                     sec.VALVE_ADDRESS, sec.LOOPPID_ADR_BASE, sec.PROCEDURE_ADDRESS,
                                     sec.INTLK_A_ADDRESS,sec.LL_ADDRESS, sec.HTRTD_ADDRESS)
        self.commands = {}

        self.signal_connection()

        self.command_buffer_waiting = 1
        # self.statustransition={}

        self.Valve_buffer = copy.copy(sec.VALVE_OUT)
        self.CHECKED = False

        self.LOOPPID_EN_buffer = copy.copy(sec.LOOPPID_EN)


        self.RTDAlarmMatrix = [self.AlarmButton.SubWindow.RTD7, self.AlarmButton.SubWindow.RTD8,
                                 self.AlarmButton.SubWindow.RTD9, self.AlarmButton.SubWindow.RTD10,
                                 self.AlarmButton.SubWindow.RTD11, self.AlarmButton.SubWindow.RTD12]
        #
        self.HTROUTAlarmMatrix = [self.AlarmButton.SubWindow.HTR1001, self.AlarmButton.SubWindow.HTR1002,
                                 self.AlarmButton.SubWindow.HTR1003, self.AlarmButton.SubWindow.HTR1004]

        self.HTRRTDAlarmMatrix = [self.AlarmButton.SubWindow.RTD1, self.AlarmButton.SubWindow.RTD2,
                                  self.AlarmButton.SubWindow.RTD3, self.AlarmButton.SubWindow.RTD4,
                                  self.AlarmButton.SubWindow.RTD5,
                                  self.AlarmButton.SubWindow.RTD6
                                  ]


        self.PTAlarmMatrix = [self.AlarmButton.SubWindow.PT1000, self.AlarmButton.SubWindow.PT1001,
                              self.AlarmButton.SubWindow.PT1002, self.AlarmButton.SubWindow.PT001, self.AlarmButton.SubWindow.PT002,
                              self.AlarmButton.SubWindow.PT003, self.AlarmButton.SubWindow.PT004]

        self.LEFTVariableMatrix = [self.AlarmButton.SubWindow.LL]
        #
        # self.DinAlarmMatrix = [self.AlarmButton.SubWindow.LS3338, self.AlarmButton.SubWindow.LS3339,
        #                        self.AlarmButton.SubWindow.ES3347, self.AlarmButton.SubWindow.PUMP3305_CON,
        #                        self.AlarmButton.SubWindow.PUMP3305_OL, self.AlarmButton.SubWindow.PS2352,
        #                        self.AlarmButton.SubWindow.PS1361, self.AlarmButton.SubWindow.PS8302]
        #HTR1202,
        #                            self.AlarmButton.SubWindow.HTR2203, self.AlarmButton.SubWindow.HTR6202,
        #                            self.AlarmButton.SubWindow.HTR6206, self.AlarmButton.SubWindow.HTR6210,
        #                            self.AlarmButton.SubWindow.HTR6223, self.AlarmButton.SubWindow.HTR6224,
        #                            self.AlarmButton.SubWindow.HTR6219, self.AlarmButton.SubWindow.HTR6221,
        #                            self.AlarmButton.SubWindow.HTR6214]

        self.AlarmMatrix = [self.AlarmButton.SubWindow.RTD7, self.AlarmButton.SubWindow.RTD8,
                                 self.AlarmButton.SubWindow.RTD9, self.AlarmButton.SubWindow.RTD10,
                                 self.AlarmButton.SubWindow.RTD11, self.AlarmButton.SubWindow.RTD12,self.AlarmButton.SubWindow.PT1000, self.AlarmButton.SubWindow.PT1001,
                              self.AlarmButton.SubWindow.PT1002, self.AlarmButton.SubWindow.PT001, self.AlarmButton.SubWindow.PT002,
                              self.AlarmButton.SubWindow.PT003, self.AlarmButton.SubWindow.PT004,self.AlarmButton.SubWindow.LL,self.AlarmButton.SubWindow.HTR1001, self.AlarmButton.SubWindow.HTR1002,
                                 self.AlarmButton.SubWindow.HTR1003, self.AlarmButton.SubWindow.HTR1004,self.AlarmButton.SubWindow.RTD1, self.AlarmButton.SubWindow.RTD2,
                                  self.AlarmButton.SubWindow.RTD3, 
                                  self.AlarmButton.SubWindow.RTD4, self.AlarmButton.SubWindow.RTD5,
                                  self.AlarmButton.SubWindow.RTD6]

        # Set user to guest by default
        self.User = "Guest"
        self.UserTimer = QtCore.QTimer(self)
        self.UserTimer.setSingleShot(True)
        self.UserTimer.timeout.connect(self.Timeout)
        self.ActivateControls(False)

        # Initialize PLC live counters

        self.PLCLiveCounter = 0

        # Link signals to slots (toggle type)
        # self.SV4327.Button.clicked.connect(self.SV4327.ButtonClicked)
        # self.SV4327.Signals.sSignal.connect(self.SetSVMode)
        # self.SV4328.Signals.sSignal.connect(self.SetSVMode)
        # self.SV4329.Signals.sSignal.connect(self.SetSVMode)
        # self.SV4331.Signals.sSignal.connect(self.SetSVMode)
        # self.SV4332.Signals.sSignal.connect(self.SetSVMode)
        # self.SV3307.Signals.sSignal.connect(self.SetSVMode)
        # self.SV3310.Signals.sSignal.connect(self.SetSVMode)
        # self.HFSV3312.Signals.sSignal.connect(self.SetSVMode)
        # self.SV3322.Signals.sSignal.connect(self.SetSVMode)
        # self.HFSV3323.Signals.sSignal.connect(self.SetSVMode)
        # self.SV3325.Signals.sSignal.connect(self.SetSVMode)

        # self.SV3329.Signals.sSignal.connect(self.SetSVMode)
        # self.HFSV3331.Signals.sSignal.connect(self.SetSVMode)
        self.LoginT.Button.clicked.connect(self.ChangeUser)
        self.LoginP.Button.clicked.connect(self.ChangeUser)

        App.aboutToQuit.connect(self.StopUpdater)
        # Start display updater;
        self.StartUpdater()

        self.signal_connection()

    # send_command_signal_MW = QtCore.Signal(object)
    send_command_signal_MW = QtCore.Signal()

    def StartUpdater(self):

        install()

        self.ClientUpdateThread = QtCore.QThread()
        self.UpClient = UpdateClient()
        self.UpClient.moveToThread(self.ClientUpdateThread)
        self.ClientUpdateThread.started.connect(self.UpClient.run)

        # signal receive the signal and send command to client
        self.UpClient.client_command_fectch.connect(self.sendcommands)
        # self.send_command_signal_MW.connect(self.UpClient.commands)
        self.send_command_signal_MW.connect(lambda: self.UpClient.commands(self.commands))

        # signal clear the self.command

        self.UpClient.client_clear_commands.connect(self.clearcommands)
        # transport read client data into GUI, this makes sure that only when new directory comes, main thread will update the display

        self.UpClient.client_data_transport.connect(lambda: self.updatedisplay(self.UpClient.receive_dic))
        self.ClientUpdateThread.start()

    # Stop all updater threads
    @QtCore.Slot()
    def StopUpdater(self):
        # self.UpPLC.stop()
        # self.PLCUpdateThread.quit()
        # self.PLCUpdateThread.wait()
        self.UpClient.stop()
        self.ClientUpdateThread.quit()
        self.ClientUpdateThread.wait()

        self.UpDisplay.stop()
        self.DUpdateThread.quit()
        self.DUpdateThread.wait()

    # signal connections to write settings to PLC codes

    def signal_connection(self):

        # Data signal saving and writing
        self.SaveSettings.SaveFileButton.clicked.connect(
            lambda: self.SaveSettings.SavecsvConfig(self.UpClient.receive_dic))
        # self.ReadSettings.LoadFileButton.clicked.connect(lambda : self.updatedisplay(self.ReadSettings.loaded_dict))
        self.ReadSettings.LoadFileButton.clicked.connect(lambda: self.man_set(self.ReadSettings.default_dict))
        self.ReadSettings.LoadFileButton.clicked.connect(lambda: self.man_activated(self.ReadSettings.default_dict))

        self.PV1001.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1001.Label.text()))
        self.PV1001.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1001.Label.text()))
        self.PV1002.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1002.Label.text()))
        self.PV1002.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1002.Label.text()))
        self.PV1003.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1003.Label.text()))
        self.PV1003.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1003.Label.text()))
        self.PV1004.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1004.Label.text()))
        self.PV1004.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1004.Label.text()))
        self.PV1005.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1005.Label.text()))
        self.PV1005.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1005.Label.text()))
        self.PV1006.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1006.Label.text()))
        self.PV1006.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1006.Label.text()))
        self.PV1007.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1007.Label.text()))
        self.PV1007.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1007.Label.text()))

        self.PV1.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1.Label.text()))
        self.PV1.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1.Label.text()))
        self.PV2.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV2.Label.text()))
        self.PV2.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV2.Label.text()))
        self.PV3.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV3.Label.text()))
        self.PV3.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV3.Label.text()))
        self.PV4.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV4.Label.text()))
        self.PV4.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV4.Label.text()))
        self.PV5.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV5.Label.text()))
        self.PV5.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV5.Label.text()))
        self.PV6.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV6.Label.text()))
        self.PV6.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV6.Label.text()))
        self.PV7.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV7.Label.text()))
        self.PV7.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV7.Label.text()))
        self.PV8.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV8.Label.text()))
        self.PV8.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV8.Label.text()))
        self.PV9.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV9.Label.text()))
        self.PV9.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV9.Label.text()))
        self.PV10.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV10.Label.text()))
        self.PV10.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV10.Label.text()))
        self.PV11.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV11.Label.text()))
        self.PV11.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV11.Label.text()))
        self.PV12.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV12.Label.text()))
        self.PV12.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV12.Label.text()))
        # PT settings

        self.AlarmButton.SubWindow.PT1000.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1000.Label.text(),
                                       Act=self.AlarmButton.SubWindow.PT1000.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.PT1000.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.PT1000.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT1001.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1001.Label.text(),
                                       Act=self.AlarmButton.SubWindow.PT1001.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.PT1001.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.PT1001.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT1002.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1002.Label.text(),
                                       Act=self.AlarmButton.SubWindow.PT1002.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.PT1002.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.PT1002.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT001.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT001.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT001.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT001.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT001.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT002.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT002.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT002.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT002.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT002.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT003.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT003.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT003.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT003.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT003.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT004.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT004.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT004.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT004.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT004.High_Set.Field.text()))

        self.AlarmButton.SubWindow.RTD7.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD7.Label.text(),
                                     Act=self.AlarmButton.SubWindow.RTD7.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.RTD7.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.RTD7.High_Set.Field.text()))

        self.AlarmButton.SubWindow.RTD8.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD8.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD8.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD8.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD8.High_Set.Field.text()))

        self.AlarmButton.SubWindow.RTD9.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD9.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD9.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD9.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD9.High_Set.Field.text()))

        self.AlarmButton.SubWindow.RTD10.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD10.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD10.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD10.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD10.High_Set.Field.text()))

        self.AlarmButton.SubWindow.RTD11.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD11.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD11.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD11.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD11.High_Set.Field.text()))

        self.AlarmButton.SubWindow.RTD12.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD12.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD12.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD12.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD12.High_Set.Field.text()))


        self.AlarmButton.SubWindow.HTR1001.updatebutton.clicked.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1001.Label.text(),
                                       Act=self.AlarmButton.SubWindow.HTR1001.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.HTR1001.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.HTR1001.High_Set.Field.text()))

        self.AlarmButton.SubWindow.HTR1002.updatebutton.clicked.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1002.Label.text(),
                                       Act=self.AlarmButton.SubWindow.HTR1002.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.HTR1002.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.HTR1002.High_Set.Field.text()))
        self.AlarmButton.SubWindow.HTR1003.updatebutton.clicked.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1003.Label.text(),
                                       Act=self.AlarmButton.SubWindow.HTR1003.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.HTR1003.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.HTR1003.High_Set.Field.text()))

        self.AlarmButton.SubWindow.HTR1004.updatebutton.clicked.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1004.Label.text(),
                                       Act=self.AlarmButton.SubWindow.HTR1004.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.HTR1004.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.HTR1004.High_Set.Field.text()))

        self.AlarmButton.SubWindow.RTD1.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD1.Label.text(),
                                          Act=self.AlarmButton.SubWindow.RTD1.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.RTD1.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.RTD1.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD2.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD2.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD2.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD2.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD2.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD3.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD3.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD3.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD3.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD3.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD4.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD4.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD4.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD4.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD4.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD5.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD5.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD5.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD5.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD5.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD6.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD6.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD6.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD6.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD6.High_Set.Field.text()))



        self.AlarmButton.SubWindow.LL.updatebutton.clicked.connect(
            lambda: self.LLBoxUpdate(pid=self.AlarmButton.SubWindow.LL.Label.text(),
                                       Act=self.AlarmButton.SubWindow.LL.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.LL.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.LL.High_Set.Field.text()))

        # check box state change
        self.AlarmButton.SubWindow.PT1000.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1000.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT1000.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT1000.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT1000.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.PT1001.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1001.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT1001.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT1001.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT1001.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.PT1002.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1002.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT1002.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT1002.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT1002.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.PT001.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT001.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT001.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT001.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT001.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.PT002.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT002.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT002.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT002.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT002.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.PT003.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT003.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT003.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT003.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT003.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.PT004.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT004.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT004.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT004.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT004.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.RTD7.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD7.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD7.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD7.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD7.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.RTD8.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD8.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD8.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD8.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD8.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.RTD9.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD9.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD9.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD9.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD9.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.RTD10.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD10.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD10.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD10.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD10.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.RTD11.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD11.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD11.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD11.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD11.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.RTD12.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD12.Label.text(),
                                       Act=self.AlarmButton.SubWindow.RTD12.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.RTD12.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.RTD12.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.HTR1001.AlarmMode.stateChanged.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1001.Label.text(),
                                       Act=self.AlarmButton.SubWindow.HTR1001.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.HTR1001.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.HTR1001.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.HTR1002.AlarmMode.stateChanged.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1002.Label.text(),
                                       Act=self.AlarmButton.SubWindow.HTR1002.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.HTR1002.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.HTR1002.High_Set.Field.text(),update = False))
        self.AlarmButton.SubWindow.HTR1003.AlarmMode.stateChanged.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1003.Label.text(),
                                       Act=self.AlarmButton.SubWindow.HTR1003.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.HTR1003.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.HTR1003.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.HTR1004.AlarmMode.stateChanged.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1004.Label.text(),
                                       Act=self.AlarmButton.SubWindow.HTR1004.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.HTR1004.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.HTR1004.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.RTD1.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD1.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD1.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD1.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD1.High_Set.Field.text(),update = False))
        self.AlarmButton.SubWindow.RTD2.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD2.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD2.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD2.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD2.High_Set.Field.text(),update = False))
        self.AlarmButton.SubWindow.RTD3.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD3.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD3.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD3.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD3.High_Set.Field.text(),update = False))
        self.AlarmButton.SubWindow.RTD4.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD4.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD4.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD4.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD4.High_Set.Field.text(),update = False))
        self.AlarmButton.SubWindow.RTD5.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD5.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD5.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD5.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD5.High_Set.Field.text(),update = False))
        self.AlarmButton.SubWindow.RTD6.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD6.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD6.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD6.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD6.High_Set.Field.text(),update = False))

        self.AlarmButton.SubWindow.LL.AlarmMode.stateChanged.connect(
            lambda: self.LLBoxUpdate(pid=self.AlarmButton.SubWindow.LL.Label.text(),
                                       Act=self.AlarmButton.SubWindow.LL.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.LL.Low_Set.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.LL.High_Set.Field.text(),update = False))


    @QtCore.Slot()
    def LButtonClicked(self, pid):
        try:
            # if there is alread a command to send to tcp server, wait the new command until last one has been sent
            # if not self.commands[pid]:
            #     time.sleep(self.command_buffer_waiting)
            # in case cannot find the pid's address
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def RButtonClicked(self, pid):

        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "CLOSE",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked", datetime.datetime.now())
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def FLAGLButtonClicked(self, pid):
        try:
            # if there is alread a command to send to tcp server, wait the new command until last one has been sent
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            # in case cannot find the pid's address
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "FLAG", "operation": "OPEN", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def FLAGRButtonClicked(self, pid):

        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "FLAG", "operation": "CLOSE",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def SwitchLButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "switch", "operation": "ON", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def SwitchRButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "switch", "operation": "OFF",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_A_LButtonClicked(self, pid):
        try:

            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_A", "operation": "ON", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_A_RButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_A", "operation": "OFF",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_A_RESET(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_A", "operation": "RESET",
                                  "value": 1}
            print(self.commands)
            print(pid, "RESET")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_A_update(self, pid, value):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_A", "operation": "update",
                                  "value": float(value)}
            print(self.commands)
            print(pid, "update")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_D_LButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_D", "operation": "ON", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_D_RButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_D", "operation": "OFF",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_D_RESET(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_D", "operation": "RESET",
                                  "value": 1}
            print(self.commands)
            print(pid, "RESET")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTLButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_power", "operation": "OPEN",
                                  "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTRButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_power", "operation": "CLOSE",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTSet(self, pid, value):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if value in [0, 1, 2, 3]:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT", "operation": "SETMODE",
                                      "value": value}
            else:
                print("value should be 0, 1, 2, 3")
            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTSETPOINTSet(self, pid, value1, value2):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if value1 == 1:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT",
                                      "operation": "SET1", "value": value2}
            elif value1 == 2:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT",
                                      "operation": "SET2", "value": value2}
            elif value1 == 3:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT",
                                      "operation": "SET3", "value": value2}
            else:
                print("MODE number should be in 1-3")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTGroupButtonClicked(self, pid, setN):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if setN == 0:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_setmode",
                                      "operation": "SET0", "value": True}
            elif setN == 1:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_setmode",
                                      "operation": "SET1", "value": True}
            elif setN == 2:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_setmode",
                                      "operation": "SET2", "value": True}
            elif setN == 3:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_setmode",
                                      "operation": "SET3", "value": True}
            else:
                print("not a valid address")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTupdate(self, pid, modeN, setpoint):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if modeN == 'MODE0':
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_para",
                                      "operation": "SET0", "value": {"SETPOINT": setpoint}}
            elif modeN == 'MODE1':
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_para",
                                      "operation": "SET1", "value": {"SETPOINT": setpoint}}
            elif modeN == 'MODE2':
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_para",
                                      "operation": "SET2", "value": {"SETPOINT": setpoint}}
            elif modeN == 'MODE3':
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_para",
                                      "operation": "SET3", "value": {"SETPOINT": setpoint}}
            else:
                print("MODE number should be in MODE0-3 and is a string")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTRupdate(self, pid, modeN, setpoint, HI, LO):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if modeN == 'MODE0':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET0", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            elif modeN == 'MODE1':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET1", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            elif modeN == 'MODE2':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET2", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            elif modeN == 'MODE3':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET3", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            else:
                print("MODE number should be in MODE0-3 and is a string")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTLButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "heater_power", "operation": "EN",
                                  "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTRButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "heater_power", "operation": "DISEN",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTSwitchSet(self, pid, value):
        try:

            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if value in [0, 1, 2, 3]:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater", "operation": "SETMODE",
                                      "value": value}
            else:
                print("value should be 0, 1, 2, 3")
            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTHISet(self, pid, value):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                  "operation": "HI_LIM", "value": value}

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTLOSet(self, pid, value):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                  "operation": "LO_LIM", "value": value}

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTSETPOINTSet(self, pid, value1, value2):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if value1 == 0:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                      "operation": "SET0", "value": value2}
            elif value1 == 1:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                      "operation": "SET1", "value": value2}
            elif value1 == 2:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                      "operation": "SET2", "value": value2}
            elif value1 == 3:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                      "operation": "SET3", "value": value2}
            else:
                print("MODE number should be in 0-3")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTRGroupButtonClicked(self, pid, setN):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if setN == 0:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_setmode",
                                      "operation": "SET0", "value": True}
            elif setN == 1:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_setmode",
                                      "operation": "SET1", "value": True}
            elif setN == 2:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_setmode",
                                      "operation": "SET2", "value": True}
            elif setN == 3:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_setmode",
                                      "operation": "SET3", "value": True}
            else:
                print("not a valid address")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTRupdate(self, pid, modeN, setpoint, HI, LO):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if modeN == 'MODE0':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET0", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            elif modeN == 'MODE1':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET1", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            elif modeN == 'MODE2':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET2", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            elif modeN == 'MODE3':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET3", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            else:
                print("MODE number should be in MODE0-3 and is a string")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def BOTTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def AD1TTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "AD1", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def AD2TTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "AD2", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTRTTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "LS", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                   "LowLimit": float(
                                                                                                       LowLimit),
                                                                                                   "HighLimit": float(
                                                                                                       HighLimit),
                                                                                                   "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)


    @QtCore.Slot()
    def FPTTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "FP", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def PTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "PT", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LEFTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "LEFT", "operation": {"Act": Act,
                                                                                                    "LowLimit": float(
                                                                                                        LowLimit),
                                                                                                    "HighLimit": float(
                                                                                                        HighLimit),
                                                                                                    "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LLBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "LL", "address": address, "type": "LL", "operation": {"Act": Act,
                                                                                                    "LowLimit": float(
                                                                                                        LowLimit),
                                                                                                    "HighLimit": float(
                                                                                                        HighLimit),
                                                                                                    "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def DinBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "Din", "operation": {"Act": Act,
                                                                                                   "LowLimit": float(
                                                                                                       LowLimit),
                                                                                                   "HighLimit": float(
                                                                                                       HighLimit),
                                                                                                   "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOPPIDBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "LS", "address": address, "type": "LOOPPID_alarm", "operation": {"Act": Act,
                                                                                                             "LowLimit": float(
                                                                                                                 LowLimit),
                                                                                                             "HighLimit": float(
                                                                                                                 HighLimit),
                                                                                                             "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def ProcedureClick(self, pid, start, stop, abort):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "Procedure",
                                  "operation": {"Start": start, "Stop": stop, "Abort": abort}}
            print(pid, start, stop, abort, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def Procedure_TS_update(self, pid, RST, SEL, ADDREM_MASS, MAXTIME, update):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "Procedure_TS",
                                  "operation": {"RST_FF": RST, "SEL": SEL, "ADDREM_MASS": ADDREM_MASS,
                                                "MAXTIME": MAXTIME, "update": update}}
            print(pid, RST, SEL, ADDREM_MASS, MAXTIME, update, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def Procedure_PC_update(self, pid, start, stop, abort, ABORT_FF, FASTCOMP_FF, PCYCLE_SLOWCOMP_FF, PCYCLE_CYLEQ_FF,
                            PCYCLE_ACCHARGE_FF, PCYCLE_CYLBLEED_FF, PSET, MAXEXPTIME, MAXEQTIME, MAXEQPDIFF, MAXACCTIME,
                            MAXACCDPDT, MAXBLEEDTIME, MAXBLEEDDPDT, update):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "Procedure_PC",
                                  "operation": {"ABORT_FF": ABORT_FF, "FASTCOMP_FF": FASTCOMP_FF,
                                                "PCYCLE_SLOWCOMP_FF": PCYCLE_SLOWCOMP_FF,
                                                "PCYCLE_CYLEQ_FF": PCYCLE_CYLEQ_FF,
                                                "PCYCLE_ACCHARGE_FF": PCYCLE_ACCHARGE_FF,
                                                "PCYCLE_CYLBLEED_FF": PCYCLE_CYLBLEED_FF,
                                                "PSET": PSET, "MAXEXPTIME": MAXEXPTIME, "MAXEQTIME": MAXEQTIME,
                                                "MAXEQPDIFF": MAXEQPDIFF,
                                                "MAXACCTIME": MAXACCTIME, "MAXACCDPDT": MAXACCDPDT,
                                                "MAXBLEEDTIME": MAXBLEEDTIME, "MAXBLEEDDPDT": MAXBLEEDDPDT,
                                                "update": update}}
            print(pid, start, stop, abort, "ARE OK?")
        except Exception as e:
            print(e)

    # Ask if staying in admin mode after timeout
    @QtCore.Slot()
    def Timeout(self):
        if QtWidgets.QMessageBox.question(self, "Login", "Stay logged in?") == QtWidgets.QMessageBox.StandardButton.Yes:
            self.UserTimer.start(ADMIN_TIMER)
        else:
            self.ChangeUser()

    # Change user and lock/unlock controls
    @QtCore.Slot()
    def ChangeUser(self):
        if self.User == "Guest":
            Dialog = QtWidgets.QInputDialog()
            Dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
            Dialog.setLabelText("Please entre password")
            Dialog.setModal(True)
            Dialog.setWindowTitle("Login")
            Dialog.exec()
            if Dialog.result():
                if VerifyPW(ADMIN_PASSWORD, Dialog.textValue()):
                    self.User = "Admin"
                    self.LoginT.Button.setText("Admin")
                    self.LoginP.Button.setText("Admin")
                    self.LoginW.Button.setText("Admin")

                    self.ActivateControls(True)

                    self.UserTimer.start(ADMIN_TIMER)
        else:
            self.User = "Guest"
            self.LoginT.Button.setText("Guest")
            self.LoginP.Button.setText("Guest")
            self.LoginW.Button.setText("Guest")

            self.ActivateControls(False)

    @QtCore.Slot()
    def sendcommands(self):
        self.send_command_signal_MW.emit()
        print(self.commands)
        # print("signal received")

    @QtCore.Slot()
    def clearcommands(self):
        self.commands = {}

    def FindDistinctTrue(self, v0, v1, v2, v3):
        if v0 == True:
            if True in [v1, v2, v3]:
                print("Multiple True values")
                return "False"
            else:
                return "MODE0"
        elif v1 == True:
            if True in [v2, v3]:
                print("Multiple True values")
                return "False"
            else:
                return "MODE1"
        elif v2 == True:
            if True in [v3]:
                print("Multiple True values")
                return "False"
            else:
                return "MODE2"
        else:
            if v3:
                return "MODE3"
            else:
                print("No True Value")
                return "False"

    def FetchSetPoint(self, v0, v1, v2, v3, w0, w1, w2, w3):
        # v0-3 must corresponds to w0-3 in order
        if v0 == True:
            if True in [v1, v2, v3]:
                print("Multiple True values")
                return "False"
            else:
                return w0
        elif v1 == True:
            if True in [v2, v3]:
                print("Multiple True values")
                return "False"
            else:
                return w1
        elif v2 == True:
            if True in [v3]:
                print("Multiple True values")
                return "False"
            else:
                return w2
        else:
            if v3:
                return w3
            else:
                print("No True Value")
                return "False"

    @QtCore.Slot(object)
    def man_set(self, dic_c):
        self.commands['MAN_SET'] = dic_c
        # check the checkboxes

    @QtCore.Slot(object)
    def man_activated(self, dic_c):
        print("Acitve", dic_c["Active"])
        # for element in self.BORTDAlarmMatrix:
        #     element.AlarmMode.setChecked(bool(dic_c["Active"]["TT"]["BO"][element.Label.text()]))
        #
        # # FP TTs
        # # update alarmwindow widgets' <alarm> value
        #
        for element in self.RTDAlarmMatrix:
            # print(element.Label.text())
            if element.Label.text() in dic_c["Active"]["TT"]["AD1"]:
                element.AlarmMode.setChecked(bool(dic_c["Active"]["TT"]["AD1"][element.Label.text()]))
            elif element.Label.text() in dic_c["Active"]["TT"]["AD2"]:
                element.AlarmMode.setChecked(bool(dic_c["Active"]["TT"]["AD2"][element.Label.text()]))
        for element in self.HTROUTAlarmMatrix:
            # print(element.Label.text())

            element.AlarmMode.setChecked(bool(dic_c["Active"]["LOOPPID"][element.Label.text()]))
        for element in self.HTRRTDAlarmMatrix:

            element.AlarmMode.setChecked(bool(dic_c["Active"]["TT"]["LS"][element.Label.text()]))

        # for element in self.HTROUTAlarmMatrix:
        #     element.AlarmMode.setChecked(bool(dic_c["Active"]["LOOPPID"][element.Label.text()]))

        for element in self.PTAlarmMatrix:
            element.AlarmMode.setChecked(bool(dic_c["Active"]["PT"][element.Label.text()]))

        for element in self.LEFTVariableMatrix:
            element.AlarmMode.setChecked(bool(dic_c["Active"]["LL"][element.Label.text()]))

        # for element in self.LEFTVariableMatrix:
        #     element.AlarmMode.setChecked(bool(dic_c["Active"]["LEFT_REAL"][element.Label.text()]))
        #
        # for element in self.DinAlarmMatrix:
        #     element.AlarmMode.setChecked(bool(dic_c["Active"]["Din"][element.Label.text()]))
        #
        # for element in self.LOOPPIDAlarmMatrix:
        #     element.AlarmMode.setChecked(bool(dic_c["Active"]["LOOPPID"][element.Label.text()]))

        # if dic_c["Active"]["TT"]["FP"]["fa"]:
        #     self.AlarmWindow.PT2316.AlarmMode.setChecked(True)
        # elif not dic_c["Active"]["TT"]["FP"]["fa"]:
        #     self.AlarmWindow.PT2316.AlarmMode.setChecked(False)
        # else:
        #     pass

    @QtCore.Slot(object)
    def updatedisplay(self, received_dic_c):
        print("Display updating", datetime.datetime.now())
        # print('Display update result for HFSV3331:', received_dic_c["data"]["Valve"]["OUT"]["HFSV3331"])

        # print(received_dic_c["data"]["Procedure"])
        if received_dic_c["Active"]["INI_CHECK"] == True and self.CHECKED == False:
            self.man_activated(received_dic_c)
            self.CHECKED = True
        # initialization for all check box
        self.AlarmButton.SubWindow.PT1000.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT1000"])
        self.AlarmButton.SubWindow.PT1000.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT1000"])

        self.AlarmButton.SubWindow.PT1001.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT1001"])
        self.AlarmButton.SubWindow.PT1001.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT1001"])

        self.AlarmButton.SubWindow.PT1002.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT1002"])
        self.AlarmButton.SubWindow.PT1002.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT1002"])

        self.AlarmButton.SubWindow.PT001.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT001"])
        self.AlarmButton.SubWindow.PT001.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT001"])

        self.AlarmButton.SubWindow.PT002.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT002"])
        self.AlarmButton.SubWindow.PT002.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT002"])

        self.AlarmButton.SubWindow.PT003.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT003"])
        self.AlarmButton.SubWindow.PT003.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT003"])

        self.AlarmButton.SubWindow.PT004.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT004"])
        self.AlarmButton.SubWindow.PT004.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT004"])

        self.AlarmButton.SubWindow.RTD7.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD7"])
        self.AlarmButton.SubWindow.RTD7.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD7"])

        self.AlarmButton.SubWindow.RTD8.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD8"])
        self.AlarmButton.SubWindow.RTD8.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD8"])

        self.AlarmButton.SubWindow.RTD9.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD9"])
        self.AlarmButton.SubWindow.RTD9.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD9"])

        self.AlarmButton.SubWindow.RTD10.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD10"])
        self.AlarmButton.SubWindow.RTD10.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD10"])

        self.AlarmButton.SubWindow.RTD11.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD11"])
        self.AlarmButton.SubWindow.RTD11.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD11"])

        self.AlarmButton.SubWindow.RTD12.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD12"])
        self.AlarmButton.SubWindow.RTD12.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD12"])

        # self.AlarmButton.SubWindow.TT1007.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["TT1007"])
        # self.AlarmButton.SubWindow.TT1007.Indicator.SetValue(
        #     received_dic_c["data"]["TT"]["AD1"]["value"]["TT1007"])
        #
        # self.AlarmButton.SubWindow.TT1008.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["TT1008"])
        # self.AlarmButton.SubWindow.TT1008.Indicator.SetValue(
        #     received_dic_c["data"]["TT"]["AD1"]["value"]["TT1008"])
        #
        # self.AlarmButton.SubWindow.TT1009.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD2"]["TT1009"])
        # self.AlarmButton.SubWindow.TT1009.Indicator.SetValue(
        #     received_dic_c["data"]["TT"]["AD2"]["value"]["TT1009"])

        self.AlarmButton.SubWindow.HTR1001.UpdateAlarm(received_dic_c["Alarm"]["LOOPPID"]["HTR1001"])
        self.AlarmButton.SubWindow.HTR1001.Indicator.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1001"])

        self.AlarmButton.SubWindow.HTR1002.UpdateAlarm(received_dic_c["Alarm"]["LOOPPID"]["HTR1002"])
        self.AlarmButton.SubWindow.HTR1002.Indicator.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1002"])

        self.AlarmButton.SubWindow.HTR1003.UpdateAlarm(received_dic_c["Alarm"]["LOOPPID"]["HTR1003"])
        self.AlarmButton.SubWindow.HTR1003.Indicator.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1003"])

        self.AlarmButton.SubWindow.HTR1004.UpdateAlarm(received_dic_c["Alarm"]["LOOPPID"]["HTR1004"])
        self.AlarmButton.SubWindow.HTR1004.Indicator.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1004"])

        self.AlarmButton.SubWindow.RTD1.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD1"])
        self.AlarmButton.SubWindow.RTD1.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD1"])

        self.AlarmButton.SubWindow.RTD2.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD2"])
        self.AlarmButton.SubWindow.RTD2.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD2"])

        self.AlarmButton.SubWindow.RTD3.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD3"])
        self.AlarmButton.SubWindow.RTD3.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD3"])

        self.AlarmButton.SubWindow.RTD4.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD4"])
        self.AlarmButton.SubWindow.RTD4.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD4"])

        self.AlarmButton.SubWindow.RTD5.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD5"])
        self.AlarmButton.SubWindow.RTD5.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD5"])

        self.AlarmButton.SubWindow.RTD6.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD6"])
        self.AlarmButton.SubWindow.RTD6.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD6"])


        self.AlarmButton.SubWindow.LL.UpdateAlarm(received_dic_c["Alarm"]["LL"]["LL"])
        self.AlarmButton.SubWindow.LL.Indicator.SetValue(
            received_dic_c["data"]["LL"]["value"]["LL"])


        # self.display_update.emit(dic)

        # self.PV1001.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV1001"])
        # self.PV1002.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV1002"])
        # self.PV1003.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV1003"])
        # self.PV1004.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV1004"])
        # self.PV1005.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV1005"])
        # self.PV1006.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV1006"])
        # self.PV1007.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV1007"])
        #
        # self.PV1.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV1"])
        # self.PV2.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV2"])
        # self.PV3.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV3"])
        # self.PV4.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV4"])
        # self.PV5.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV5"])
        # self.PV6.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV6"])
        # self.PV7.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV7"])
        # self.PV8.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV8"])
        # self.PV9.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV9"])
        # self.PV10.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV10"])
        # self.PV11.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV11"])
        # self.PV12.Set.Activate(received_dic_c["data"]["Valve"]["MAN"]["PV12"])

        # refreshing the valve status from PLC every 30s



        self.PT1000.SetValue(received_dic_c["data"]["PT"]["value"]["PT1000"])
        self.PT1001.SetValue(received_dic_c["data"]["PT"]["value"]["PT1001"])
        self.PT1002.SetValue(received_dic_c["data"]["PT"]["value"]["PT1002"])

        self.PT001.SetValue(received_dic_c["data"]["PT"]["value"]["PT001"])

        self.PT002.SetValue(received_dic_c["data"]["PT"]["value"]["PT002"])

        self.PT003.SetValue(received_dic_c["data"]["PT"]["value"]["PT003"])
        self.PT004.SetValue(received_dic_c["data"]["PT"]["value"]["PT004"])

        self.RTD7.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD7"])
        self.RTD8.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD8"])
        self.RTD9.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD9"])
        self.RTD10.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD10"])
        self.RTD11.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD11"])
        self.RTD12.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD12"])

        self.PT001.SetValue(received_dic_c["data"]["PT"]["value"]["PT001"])
        self.PT002.SetValue(received_dic_c["data"]["PT"]["value"]["PT002"])
        self.PT003.SetValue(received_dic_c["data"]["PT"]["value"]["PT003"])
        self.PT004.SetValue(received_dic_c["data"]["PT"]["value"]["PT004"])

        self.BGA01.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["BGA01"])
        self.BGA02.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["BGA02"])



        # self.TT2118.SetValue(self.PLC.RTD[0])

        if received_dic_c["MainAlarm"]:
            self.AlarmButton.ButtonAlarmSetSignal()
        else:
            self.AlarmButton.ButtonAlarmResetSignal()
        # # # generally checkbutton.clicked -> move to updatedisplay

        for element in self.PTAlarmMatrix:
            # print(element.Label.text())
            element.UpdateAlarm(
                received_dic_c["Alarm"]["PT"][element.Label.text()])
            element.Indicator.SetValue(
                received_dic_c["data"]["PT"]["value"][element.Label.text()])
            element.Low_Read.SetValue(
                received_dic_c["data"]["PT"]["low"][element.Label.text()])
            element.High_Read.SetValue(
                received_dic_c["data"]["PT"]["high"][element.Label.text()])


        for element in self.RTDAlarmMatrix:
            if element.Label.text() in received_dic_c["Active"]["TT"]["AD1"]:
                element.UpdateAlarm(
                    received_dic_c["Alarm"]["TT"]["AD1"][element.Label.text()])
                element.Indicator.SetValue(
                    received_dic_c["data"]["TT"]["AD1"]["value"][element.Label.text()])
                element.Low_Read.SetValue(
                    received_dic_c["data"]["TT"]["AD1"]["low"][element.Label.text()])
                element.High_Read.SetValue(
                    received_dic_c["data"]["TT"]["AD1"]["high"][element.Label.text()])
            elif element.Label.text() in received_dic_c["Active"]["TT"]["AD2"]:
                element.UpdateAlarm(
                    received_dic_c["Alarm"]["TT"]["AD2"][element.Label.text()])
                element.Indicator.SetValue(
                    received_dic_c["data"]["TT"]["AD2"]["value"][element.Label.text()])
                element.Low_Read.SetValue(
                    received_dic_c["data"]["TT"]["AD2"]["low"][element.Label.text()])
                element.High_Read.SetValue(
                    received_dic_c["data"]["TT"]["AD2"]["high"][element.Label.text()])
            # print(element.Label.text())

        for element in self.HTRRTDAlarmMatrix:
            # print(element.Label.text())
            element.UpdateAlarm(
                received_dic_c["Alarm"]["TT"]["LS"][element.Label.text()])
            element.Indicator.SetValue(
                received_dic_c["data"]["TT"]["LS"]["value"][element.Label.text()])
            element.Low_Read.SetValue(
                received_dic_c["data"]["TT"]["LS"]["low"][element.Label.text()])
            element.High_Read.SetValue(
                received_dic_c["data"]["TT"]["LS"]["high"][element.Label.text()])

        for element in self.HTROUTAlarmMatrix:
            # print(element.Label.text())
            element.UpdateAlarm(
                received_dic_c["Alarm"]["LOOPPID"][element.Label.text()])
            element.Indicator.SetValue(
                received_dic_c["data"]["LOOPPID"]["OUT"][element.Label.text()])
            element.Low_Read.SetValue(
                received_dic_c["data"]["LOOPPID"]["Alarm_LowLimit"][element.Label.text()])
            element.High_Read.SetValue(
                received_dic_c["data"]["LOOPPID"]["Alarm_HighLimit"][element.Label.text()])

        for element in self.LEFTVariableMatrix:
            # print(element.Label.text())
            element.UpdateAlarm(
                received_dic_c["Alarm"]["LL"][element.Label.text()])
            element.Indicator.SetValue(
                received_dic_c["data"]["LL"]["value"][element.Label.text()])
            element.Low_Read.SetValue(
                received_dic_c["data"]["LL"]["low"][element.Label.text()])
            element.High_Read.SetValue(
                received_dic_c["data"]["LL"]["high"][element.Label.text()])



        AlarmMatrix = []
        for element in self.AlarmMatrix:
            AlarmMatrix.append(element.Alarm)
        self.update_alarmwindow(AlarmMatrix)


        self.PV1001.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1001"])
        self.PV1002.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1002"])
        self.PV1003.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1003"])
        self.PV1004.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1004"])
        self.PV1005.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1005"])
        self.PV1006.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1006"])
        self.PV1007.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1007"])
        self.PV1.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1"])
        self.PV2.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV2"])
        self.PV3.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV3"])
        self.PV4.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV4"])
        self.PV5.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV5"])
        self.PV6.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV6"])
        self.PV7.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV7"])
        self.PV8.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV8"])
        self.PV9.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV9"])
        self.PV10.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV10"])
        self.PV11.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV11"])
        self.PV12.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV12"])


        # show whether the widgets status are normal: manully controlled and no error signal

        if received_dic_c["data"]["Valve"]["MAN"]["PV1001"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1001"]:

            self.PV1001.ActiveState.UpdateColor(True)
        else:
            self.PV1001.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1002"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1002"]:

            self.PV1002.ActiveState.UpdateColor(True)
        else:
            self.PV1002.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1003"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1003"]:

            self.PV1003.ActiveState.UpdateColor(True)
        else:
            self.PV1003.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1004"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1004"]:

            self.PV1004.ActiveState.UpdateColor(True)
        else:
            self.PV1004.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1005"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1005"]:

            self.PV1005.ActiveState.UpdateColor(True)
        else:
            self.PV1005.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1006"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1006"]:

            self.PV1006.ActiveState.UpdateColor(True)
        else:
            self.PV1006.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1006"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1006"]:

            self.PV1006.ActiveState.UpdateColor(True)
        else:
            self.PV1006.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1007"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1007"]:

            self.PV1007.ActiveState.UpdateColor(True)
        else:
            self.PV1007.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1"]:

            self.PV1.ActiveState.UpdateColor(True)
        else:
            self.PV1.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV2"] and not received_dic_c["data"]["Valve"]["ERR"]["PV2"]:

            self.PV2.ActiveState.UpdateColor(True)
        else:
            self.PV2.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV3"] and not received_dic_c["data"]["Valve"]["ERR"]["PV3"]:

            self.PV3.ActiveState.UpdateColor(True)
        else:
            self.PV3.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV4"] and not received_dic_c["data"]["Valve"]["ERR"]["PV4"]:

            self.PV4.ActiveState.UpdateColor(True)
        else:
            self.PV4.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV5"] and not received_dic_c["data"]["Valve"]["ERR"]["PV5"]:

            self.PV5.ActiveState.UpdateColor(True)
        else:
            self.PV5.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV6"] and not received_dic_c["data"]["Valve"]["ERR"]["PV6"]:

            self.PV6.ActiveState.UpdateColor(True)
        else:
            self.PV6.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV7"] and not received_dic_c["data"]["Valve"]["ERR"]["PV7"]:

            self.PV7.ActiveState.UpdateColor(True)
        else:
            self.PV7.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV8"] and not received_dic_c["data"]["Valve"]["ERR"]["PV8"]:

            self.PV8.ActiveState.UpdateColor(True)
        else:
            self.PV8.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV9"] and not received_dic_c["data"]["Valve"]["ERR"]["PV9"]:

            self.PV9.ActiveState.UpdateColor(True)
        else:
            self.PV9.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV10"] and not received_dic_c["data"]["Valve"]["ERR"]["PV10"]:

            self.PV10.ActiveState.UpdateColor(True)
        else:
            self.PV10.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV11"] and not received_dic_c["data"]["Valve"]["ERR"]["PV11"]:

            self.PV11.ActiveState.UpdateColor(True)
        else:
            self.PV11.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV12"] and not received_dic_c["data"]["Valve"]["ERR"]["PV12"]:

            self.PV12.ActiveState.UpdateColor(True)
        else:
            self.PV12.ActiveState.UpdateColor(False)


        print("PV1001 busy",received_dic_c["data"]["Valve"]["Busy"]["PV1001"] )
        if received_dic_c["data"]["Valve"]["Busy"]["PV1001"] == True:
            self.PV1001.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1001.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1002"] == True:
            self.PV1002.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1002.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1003"] == True:
            self.PV1003.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1003.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1004"] == True:
            self.PV1004.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1004.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1005"] == True:
            self.PV1005.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1005.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1006"] == True:
            self.PV1006.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1006.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1007"] == True:
            self.PV1007.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1007.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1"] == True:
            self.PV1.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV2"] == True:
            self.PV2.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV2.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV3"] == True:
            self.PV3.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV3.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV4"] == True:
            self.PV4.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV4.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV5"] == True:
            self.PV5.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV5.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV6"] == True:
            self.PV6.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV6.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV7"] == True:
            self.PV7.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV7.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV8"] == True:
            self.PV8.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV8.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV9"] == True:
            self.PV9.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV9.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV10"] == True:
            self.PV10.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV10.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV11"] == True:
            self.PV11.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV11.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV12"] == True:
            self.PV12.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV12.ButtonTransitionState(False)



        # # FLAG
        # if received_dic_c["data"]["FLAG"]["INTLKD"]["MAN_TS"]:
        #
        #     self.MAN_TS.INTLK.UpdateColor(True)
        # else:
        #     self.MAN_TS.INTLK.UpdateColor(False)

        # if received_dic_c["data"]["FLAG"]["value"]["MAN_TS"] != self.FLAG_buffer["MAN_TS"]:
        #     self.MAN_TS.Set.ButtonTransitionState(False)
        #     self.FLAG_buffer["MAN_TS"] = received_dic_c["data"]["FLAG"]["value"]["MAN_TS"]
        # else:
        #     pass
        # if received_dic_c["data"]["FLAG"]["Busy"]["MAN_TS"] == True:
        #     self.MAN_TS.Set.ButtonTransitionState(False)
        #
        # elif received_dic_c["data"]["FLAG"]["Busy"]["MAN_TS"] == False:
        #     self.MAN_TS.Set.ButtonTransitionState(False)
        # else:
        #     pass
        #
        # if received_dic_c["data"]["FLAG"]["INTLKD"]["MAN_HYD"]:
        #
        #     self.MAN_HYD.INTLK.UpdateColor(True)
        # else:
        #     self.MAN_HYD.INTLK.UpdateColor(False)

        # if received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"] != self.FLAG_buffer["MAN_HYD"]:
        #     self.MAN_HYD.Set.ButtonTransitionState(False)
        #     self.FLAG_buffer["MAN_HYD"] = received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"]
        # else:
        #     pass
        # if received_dic_c["data"]["FLAG"]["Busy"]["MAN_HYD"] == True:
        #     self.MAN_HYD.Set.ButtonTransitionState(False)
        #
        # elif received_dic_c["data"]["FLAG"]["Busy"]["MAN_HYD"] == False:
        #     self.MAN_HYD.Set.ButtonTransitionState(False)
        # else:
        #     pass


        if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1001"]:
            self.HTR1001.ButtonTransitionState(True)
            self.HTR1001.LOOPPIDWindow.ButtonTransitionState(True)
        elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1001"]:
            self.HTR1001.ButtonTransitionState(False)
            self.HTR1001.LOOPPIDWindow.ButtonTransitionState(False)
        else:
            pass

        if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1002"]:
            self.HTR1002.ButtonTransitionState(True)
            self.HTR1002.LOOPPIDWindow.ButtonTransitionState(True)
        elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1002"]:
            self.HTR1002.ButtonTransitionState(False)
            self.HTR1002.LOOPPIDWindow.ButtonTransitionState(False)
        else:
            pass

        if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1003"]:
            self.HTR1003.ButtonTransitionState(True)
            self.HTR1003.LOOPPIDWindow.ButtonTransitionState(True)
        elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1003"]:
            self.HTR1003.ButtonTransitionState(False)
            self.HTR1003.LOOPPIDWindow.ButtonTransitionState(False)
        else:
            pass

        if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1004"]:
            self.HTR1004.ButtonTransitionState(True)
            self.HTR1004.LOOPPIDWindow.ButtonTransitionState(True)
        elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1004"]:
            self.HTR1004.ButtonTransitionState(False)
            self.HTR1004.LOOPPIDWindow.ButtonTransitionState(False)
        else:
            pass

            # timeline
            # 1.click button and button locked -> 2.same status signal sent(try to set button status back)-> 3.PLC received the command and change the status
            # -> 4.changed status signal sent, the status is unlocked
            # how to distinguish 2 and 4 in different senarios: state change
            # busy -> whether it is locked

        if not received_dic_c["data"]["Valve"]["MAN"]["PV1"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV1"]:
                self.PV1.Set.ButtonLClicked()
            else:
                self.PV1.Set.ButtonRClicked()
            self.Valve_buffer["PV1"] = received_dic_c["data"]["Valve"]["OUT"]["PV1"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV1"]:
            # if manually, we need to know whether the button is locked
            # if locked (grey), then only update value after the buffer != current value
            if received_dic_c["data"]["Valve"]["Busy"]["PV1"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1"]:
                    self.PV1.Set.ButtonLClicked()
                else:
                    self.PV1.Set.ButtonRClicked()
                self.Valve_buffer["PV1"] = received_dic_c["data"]["Valve"]["OUT"]["PV1"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV1"]:

                if received_dic_c["data"]["Valve"]["OUT"]["PV1"] != self.Valve_buffer["PV1"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1"]:
                        self.PV1.Set.ButtonLClicked()
                    else:
                        self.PV1.Set.ButtonRClicked()
                    self.Valve_buffer["PV1"] = received_dic_c["data"]["Valve"]["OUT"]["PV1"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV2"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV2"]:
                self.PV2.Set.ButtonLClicked()
            else:
                self.PV2.Set.ButtonRClicked()
            self.Valve_buffer["PV2"] = received_dic_c["data"]["Valve"]["OUT"]["PV2"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV2"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV2"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV2"]:
                    self.PV2.Set.ButtonLClicked()
                else:
                    self.PV2.Set.ButtonRClicked()
                self.Valve_buffer["PV2"] = received_dic_c["data"]["Valve"]["OUT"]["PV2"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV2"]:
                #     print("PV2", received_dic_c["data"]["Valve"]["OUT"]["PV2"] != self.Valve_buffer["PV2"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV2"])
                #     print("Buffer", self.Valve_buffer["PV2"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV2"] != self.Valve_buffer["PV2"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV2"]:
                        self.PV2.Set.ButtonLClicked()
                    else:
                        self.PV2.Set.ButtonRClicked()
                    self.Valve_buffer["PV2"] = received_dic_c["data"]["Valve"]["OUT"]["PV2"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV3"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV3"]:
                self.PV3.Set.ButtonLClicked()
            else:
                self.PV3.Set.ButtonRClicked()
            self.Valve_buffer["PV3"] = received_dic_c["data"]["Valve"]["OUT"]["PV3"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV3"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV3"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV3"]:
                    self.PV3.Set.ButtonLClicked()
                else:
                    self.PV3.Set.ButtonRClicked()
                self.Valve_buffer["PV3"] = received_dic_c["data"]["Valve"]["OUT"]["PV3"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV3"]:
                #     print("PV3", received_dic_c["data"]["Valve"]["OUT"]["PV3"] != self.Valve_buffer["PV3"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV3"])
                #     print("Buffer", self.Valve_buffer["PV3"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV3"] != self.Valve_buffer["PV3"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV3"]:
                        self.PV3.Set.ButtonLClicked()
                    else:
                        self.PV3.Set.ButtonRClicked()
                    self.Valve_buffer["PV3"] = received_dic_c["data"]["Valve"]["OUT"]["PV3"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV4"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV4"]:
                self.PV4.Set.ButtonLClicked()
            else:
                self.PV4.Set.ButtonRClicked()
            self.Valve_buffer["PV4"] = received_dic_c["data"]["Valve"]["OUT"]["PV4"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV4"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV4"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV4"]:
                    self.PV4.Set.ButtonLClicked()
                else:
                    self.PV4.Set.ButtonRClicked()
                self.Valve_buffer["PV4"] = received_dic_c["data"]["Valve"]["OUT"]["PV4"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV4"]:
                #     print("PV4", received_dic_c["data"]["Valve"]["OUT"]["PV4"] != self.Valve_buffer["PV4"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV4"])
                #     print("Buffer", self.Valve_buffer["PV4"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV4"] != self.Valve_buffer["PV4"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV4"]:
                        self.PV4.Set.ButtonLClicked()
                    else:
                        self.PV4.Set.ButtonRClicked()
                    self.Valve_buffer["PV4"] = received_dic_c["data"]["Valve"]["OUT"]["PV4"]
                else:
                    pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV5"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV5"]:
                    self.PV5.Set.ButtonLClicked()
                else:
                    self.PV5.Set.ButtonRClicked()
                self.Valve_buffer["PV5"] = received_dic_c["data"]["Valve"]["OUT"]["PV5"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV5"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV5"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV5"]:
                        self.PV5.Set.ButtonLClicked()
                    else:
                        self.PV5.Set.ButtonRClicked()
                    self.Valve_buffer["PV5"] = received_dic_c["data"]["Valve"]["OUT"]["PV5"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV5"]:
                    #     print("PV5", received_dic_c["data"]["Valve"]["OUT"]["PV5"] != self.Valve_buffer["PV5"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV5"])
                    #     print("Buffer", self.Valve_buffer["PV5"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV5"] != self.Valve_buffer["PV5"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV5"]:
                            self.PV5.Set.ButtonLClicked()
                        else:
                            self.PV5.Set.ButtonRClicked()
                        self.Valve_buffer["PV5"] = received_dic_c["data"]["Valve"]["OUT"]["PV5"]
                    else:
                        pass
            if not received_dic_c["data"]["Valve"]["MAN"]["PV6"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV6"]:
                    self.PV6.Set.ButtonLClicked()
                else:
                    self.PV6.Set.ButtonRClicked()
                self.Valve_buffer["PV6"] = received_dic_c["data"]["Valve"]["OUT"]["PV6"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV6"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV6"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV6"]:
                        self.PV6.Set.ButtonLClicked()
                    else:
                        self.PV6.Set.ButtonRClicked()
                    self.Valve_buffer["PV6"] = received_dic_c["data"]["Valve"]["OUT"]["PV6"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV6"]:
                    #     print("PV6", received_dic_c["data"]["Valve"]["OUT"]["PV6"] != self.Valve_buffer["PV6"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV6"])
                    #     print("Buffer", self.Valve_buffer["PV6"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV6"] != self.Valve_buffer["PV6"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV6"]:
                            self.PV6.Set.ButtonLClicked()
                        else:
                            self.PV6.Set.ButtonRClicked()
                        self.Valve_buffer["PV6"] = received_dic_c["data"]["Valve"]["OUT"]["PV6"]
                    else:
                        pass
            if not received_dic_c["data"]["Valve"]["MAN"]["PV7"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV7"]:
                    self.PV7.Set.ButtonLClicked()
                else:
                    self.PV7.Set.ButtonRClicked()
                self.Valve_buffer["PV7"] = received_dic_c["data"]["Valve"]["OUT"]["PV7"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV7"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV7"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV7"]:
                        self.PV7.Set.ButtonLClicked()
                    else:
                        self.PV7.Set.ButtonRClicked()
                    self.Valve_buffer["PV7"] = received_dic_c["data"]["Valve"]["OUT"]["PV7"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV7"]:
                    #     print("PV7", received_dic_c["data"]["Valve"]["OUT"]["PV7"] != self.Valve_buffer["PV7"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV7"])
                    #     print("Buffer", self.Valve_buffer["PV7"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV7"] != self.Valve_buffer["PV7"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV7"]:
                            self.PV7.Set.ButtonLClicked()
                        else:
                            self.PV7.Set.ButtonRClicked()
                        self.Valve_buffer["PV7"] = received_dic_c["data"]["Valve"]["OUT"]["PV7"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV8"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV8"]:
                    self.PV8.Set.ButtonLClicked()
                else:
                    self.PV8.Set.ButtonRClicked()
                self.Valve_buffer["PV8"] = received_dic_c["data"]["Valve"]["OUT"]["PV8"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV8"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV8"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV8"]:
                        self.PV8.Set.ButtonLClicked()
                    else:
                        self.PV8.Set.ButtonRClicked()
                    self.Valve_buffer["PV8"] = received_dic_c["data"]["Valve"]["OUT"]["PV8"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV8"]:
                    #     print("PV8", received_dic_c["data"]["Valve"]["OUT"]["PV8"] != self.Valve_buffer["PV8"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV8"])
                    #     print("Buffer", self.Valve_buffer["PV8"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV8"] != self.Valve_buffer["PV8"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV8"]:
                            self.PV8.Set.ButtonLClicked()
                        else:
                            self.PV8.Set.ButtonRClicked()
                        self.Valve_buffer["PV8"] = received_dic_c["data"]["Valve"]["OUT"]["PV8"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV9"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV9"]:
                    self.PV9.Set.ButtonLClicked()
                else:
                    self.PV9.Set.ButtonRClicked()
                self.Valve_buffer["PV9"] = received_dic_c["data"]["Valve"]["OUT"]["PV9"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV9"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV9"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV9"]:
                        self.PV9.Set.ButtonLClicked()
                    else:
                        self.PV9.Set.ButtonRClicked()
                    self.Valve_buffer["PV9"] = received_dic_c["data"]["Valve"]["OUT"]["PV9"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV9"]:
                    #     print("PV9", received_dic_c["data"]["Valve"]["OUT"]["PV9"] != self.Valve_buffer["PV9"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV9"])
                    #     print("Buffer", self.Valve_buffer["PV9"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV9"] != self.Valve_buffer["PV9"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV9"]:
                            self.PV9.Set.ButtonLClicked()
                        else:
                            self.PV9.Set.ButtonRClicked()
                        self.Valve_buffer["PV9"] = received_dic_c["data"]["Valve"]["OUT"]["PV9"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV10"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV10"]:
                    self.PV10.Set.ButtonLClicked()
                else:
                    self.PV10.Set.ButtonRClicked()
                self.Valve_buffer["PV10"] = received_dic_c["data"]["Valve"]["OUT"]["PV10"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV10"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV10"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV10"]:
                        self.PV10.Set.ButtonLClicked()
                    else:
                        self.PV10.Set.ButtonRClicked()
                    self.Valve_buffer["PV10"] = received_dic_c["data"]["Valve"]["OUT"]["PV10"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV10"]:
                    #     print("PV10", received_dic_c["data"]["Valve"]["OUT"]["PV10"] != self.Valve_buffer["PV10"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV10"])
                    #     print("Buffer", self.Valve_buffer["PV10"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV10"] != self.Valve_buffer["PV10"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV10"]:
                            self.PV10.Set.ButtonLClicked()
                        else:
                            self.PV10.Set.ButtonRClicked()
                        self.Valve_buffer["PV10"] = received_dic_c["data"]["Valve"]["OUT"]["PV10"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV11"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV11"]:
                    self.PV11.Set.ButtonLClicked()
                else:
                    self.PV11.Set.ButtonRClicked()
                self.Valve_buffer["PV11"] = received_dic_c["data"]["Valve"]["OUT"]["PV11"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV11"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV11"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV11"]:
                        self.PV11.Set.ButtonLClicked()
                    else:
                        self.PV11.Set.ButtonRClicked()
                    self.Valve_buffer["PV11"] = received_dic_c["data"]["Valve"]["OUT"]["PV11"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV11"]:
                    #     print("PV11", received_dic_c["data"]["Valve"]["OUT"]["PV11"] != self.Valve_buffer["PV11"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV11"])
                    #     print("Buffer", self.Valve_buffer["PV11"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV11"] != self.Valve_buffer["PV11"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV11"]:
                            self.PV11.Set.ButtonLClicked()
                        else:
                            self.PV11.Set.ButtonRClicked()
                        self.Valve_buffer["PV11"] = received_dic_c["data"]["Valve"]["OUT"]["PV11"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV12"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV12"]:
                    self.PV12.Set.ButtonLClicked()
                else:
                    self.PV12.Set.ButtonRClicked()
                self.Valve_buffer["PV12"] = received_dic_c["data"]["Valve"]["OUT"]["PV12"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV12"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV12"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV12"]:
                        self.PV12.Set.ButtonLClicked()
                    else:
                        self.PV12.Set.ButtonRClicked()
                    self.Valve_buffer["PV12"] = received_dic_c["data"]["Valve"]["OUT"]["PV12"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV12"]:
                    #     print("PV12", received_dic_c["data"]["Valve"]["OUT"]["PV12"] != self.Valve_buffer["PV12"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV12"])
                    #     print("Buffer", self.Valve_buffer["PV12"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV12"] != self.Valve_buffer["PV12"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV12"]:
                            self.PV12.Set.ButtonLClicked()
                        else:
                            self.PV12.Set.ButtonRClicked()
                        self.Valve_buffer["PV12"] = received_dic_c["data"]["Valve"]["OUT"]["PV12"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV1000"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1000"]:
                    self.PV1000.Set.ButtonLClicked()
                else:
                    self.PV1000.Set.ButtonRClicked()
                self.Valve_buffer["PV1000"] = received_dic_c["data"]["Valve"]["OUT"]["PV1000"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV1000"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV1000"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1000"]:
                        self.PV1000.Set.ButtonLClicked()
                    else:
                        self.PV1000.Set.ButtonRClicked()
                    self.Valve_buffer["PV1000"] = received_dic_c["data"]["Valve"]["OUT"]["PV1000"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV1000"]:
                    #     print("PV1000", received_dic_c["data"]["Valve"]["OUT"]["PV1000"] != self.Valve_buffer["PV1000"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1000"])
                    #     print("Buffer", self.Valve_buffer["PV1000"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1000"] != self.Valve_buffer["PV1000"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV1000"]:
                            self.PV1000.Set.ButtonLClicked()
                        else:
                            self.PV1000.Set.ButtonRClicked()
                        self.Valve_buffer["PV1000"] = received_dic_c["data"]["Valve"]["OUT"]["PV1000"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV1001"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1001"]:
                    self.PV1001.Set.ButtonLClicked()
                else:
                    self.PV1001.Set.ButtonRClicked()
                self.Valve_buffer["PV1001"] = received_dic_c["data"]["Valve"]["OUT"]["PV1001"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV1001"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV1001"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1001"]:
                        self.PV1001.Set.ButtonLClicked()
                    else:
                        self.PV1001.Set.ButtonRClicked()
                    self.Valve_buffer["PV1001"] = received_dic_c["data"]["Valve"]["OUT"]["PV1001"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV1001"]:
                    #     print("PV1001", received_dic_c["data"]["Valve"]["OUT"]["PV1001"] != self.Valve_buffer["PV1001"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1001"])
                    #     print("Buffer", self.Valve_buffer["PV1001"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1001"] != self.Valve_buffer["PV1001"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV1001"]:
                            self.PV1001.Set.ButtonLClicked()
                        else:
                            self.PV1001.Set.ButtonRClicked()
                        self.Valve_buffer["PV1001"] = received_dic_c["data"]["Valve"]["OUT"]["PV1001"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV1002"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1002"]:
                    self.PV1002.Set.ButtonLClicked()
                else:
                    self.PV1002.Set.ButtonRClicked()
                self.Valve_buffer["PV1002"] = received_dic_c["data"]["Valve"]["OUT"]["PV1002"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV1002"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV1002"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1002"]:
                        self.PV1002.Set.ButtonLClicked()
                    else:
                        self.PV1002.Set.ButtonRClicked()
                    self.Valve_buffer["PV1002"] = received_dic_c["data"]["Valve"]["OUT"]["PV1002"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV1002"]:
                    #     print("PV1002", received_dic_c["data"]["Valve"]["OUT"]["PV1002"] != self.Valve_buffer["PV1002"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1002"])
                    #     print("Buffer", self.Valve_buffer["PV1002"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1002"] != self.Valve_buffer["PV1002"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV1002"]:
                            self.PV1002.Set.ButtonLClicked()
                        else:
                            self.PV1002.Set.ButtonRClicked()
                        self.Valve_buffer["PV1002"] = received_dic_c["data"]["Valve"]["OUT"]["PV1002"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV1003"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1003"]:
                    self.PV1003.Set.ButtonLClicked()
                else:
                    self.PV1003.Set.ButtonRClicked()
                self.Valve_buffer["PV1003"] = received_dic_c["data"]["Valve"]["OUT"]["PV1003"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV1003"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV1003"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1003"]:
                        self.PV1003.Set.ButtonLClicked()
                    else:
                        self.PV1003.Set.ButtonRClicked()
                    self.Valve_buffer["PV1003"] = received_dic_c["data"]["Valve"]["OUT"]["PV1003"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV1003"]:
                    #     print("PV1003", received_dic_c["data"]["Valve"]["OUT"]["PV1003"] != self.Valve_buffer["PV1003"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1003"])
                    #     print("Buffer", self.Valve_buffer["PV1003"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1003"] != self.Valve_buffer["PV1003"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV1003"]:
                            self.PV1003.Set.ButtonLClicked()
                        else:
                            self.PV1003.Set.ButtonRClicked()
                        self.Valve_buffer["PV1003"] = received_dic_c["data"]["Valve"]["OUT"]["PV1003"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV1004"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1004"]:
                    self.PV1004.Set.ButtonLClicked()
                else:
                    self.PV1004.Set.ButtonRClicked()
                self.Valve_buffer["PV1004"] = received_dic_c["data"]["Valve"]["OUT"]["PV1004"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV1004"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV1004"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1004"]:
                        self.PV1004.Set.ButtonLClicked()
                    else:
                        self.PV1004.Set.ButtonRClicked()
                    self.Valve_buffer["PV1004"] = received_dic_c["data"]["Valve"]["OUT"]["PV1004"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV1004"]:
                    #     print("PV1004", received_dic_c["data"]["Valve"]["OUT"]["PV1004"] != self.Valve_buffer["PV1004"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1004"])
                    #     print("Buffer", self.Valve_buffer["PV1004"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1004"] != self.Valve_buffer["PV1004"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV1004"]:
                            self.PV1004.Set.ButtonLClicked()
                        else:
                            self.PV1004.Set.ButtonRClicked()
                        self.Valve_buffer["PV1004"] = received_dic_c["data"]["Valve"]["OUT"]["PV1004"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV1005"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1005"]:
                    self.PV1005.Set.ButtonLClicked()
                else:
                    self.PV1005.Set.ButtonRClicked()
                self.Valve_buffer["PV1005"] = received_dic_c["data"]["Valve"]["OUT"]["PV1005"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV1005"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV1005"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1005"]:
                        self.PV1005.Set.ButtonLClicked()
                    else:
                        self.PV1005.Set.ButtonRClicked()
                    self.Valve_buffer["PV1005"] = received_dic_c["data"]["Valve"]["OUT"]["PV1005"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV1005"]:
                    #     print("PV1005", received_dic_c["data"]["Valve"]["OUT"]["PV1005"] != self.Valve_buffer["PV1005"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1005"])
                    #     print("Buffer", self.Valve_buffer["PV1005"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1005"] != self.Valve_buffer["PV1005"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV1005"]:
                            self.PV1005.Set.ButtonLClicked()
                        else:
                            self.PV1005.Set.ButtonRClicked()
                        self.Valve_buffer["PV1005"] = received_dic_c["data"]["Valve"]["OUT"]["PV1005"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV1006"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1006"]:
                    self.PV1006.Set.ButtonLClicked()
                else:
                    self.PV1006.Set.ButtonRClicked()
                self.Valve_buffer["PV1006"] = received_dic_c["data"]["Valve"]["OUT"]["PV1006"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV1006"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV1006"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1006"]:
                        self.PV1006.Set.ButtonLClicked()
                    else:
                        self.PV1006.Set.ButtonRClicked()
                    self.Valve_buffer["PV1006"] = received_dic_c["data"]["Valve"]["OUT"]["PV1006"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV1006"]:
                    #     print("PV1006", received_dic_c["data"]["Valve"]["OUT"]["PV1006"] != self.Valve_buffer["PV1006"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1006"])
                    #     print("Buffer", self.Valve_buffer["PV1006"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1006"] != self.Valve_buffer["PV1006"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV1006"]:
                            self.PV1006.Set.ButtonLClicked()
                        else:
                            self.PV1006.Set.ButtonRClicked()
                        self.Valve_buffer["PV1006"] = received_dic_c["data"]["Valve"]["OUT"]["PV1006"]
                    else:
                        pass

            if not received_dic_c["data"]["Valve"]["MAN"]["PV1007"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1007"]:
                    self.PV1007.Set.ButtonLClicked()
                else:
                    self.PV1007.Set.ButtonRClicked()
                self.Valve_buffer["PV1007"] = received_dic_c["data"]["Valve"]["OUT"]["PV1007"]
            elif received_dic_c["data"]["Valve"]["MAN"]["PV1007"]:
                if received_dic_c["data"]["Valve"]["Busy"]["PV1007"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1007"]:
                        self.PV1007.Set.ButtonLClicked()
                    else:
                        self.PV1007.Set.ButtonRClicked()
                    self.Valve_buffer["PV1007"] = received_dic_c["data"]["Valve"]["OUT"]["PV1007"]
                elif not received_dic_c["data"]["Valve"]["Busy"]["PV1007"]:
                    #     print("PV1007", received_dic_c["data"]["Valve"]["OUT"]["PV1007"] != self.Valve_buffer["PV1007"])
                    #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1007"])
                    #     print("Buffer", self.Valve_buffer["PV1007"])
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1007"] != self.Valve_buffer["PV1007"]:
                        if received_dic_c["data"]["Valve"]["OUT"]["PV1007"]:
                            self.PV1007.Set.ButtonLClicked()
                        else:
                            self.PV1007.Set.ButtonRClicked()
                        self.Valve_buffer["PV1007"] = received_dic_c["data"]["Valve"]["OUT"]["PV1007"]
                    else:
                        pass


        # Valve icons

        # if received_dic_c["data"]["Valve"]["OUT"]["PV1"]:
        #     self.PV1_icon.Turnon()
        # else:
        #     self.PV1_icon.Turnoff()
        #
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV2"]:
        #     self.PV2_icon.Turnon()
        # else:
        #     self.PV2_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV3"]:
        #     self.PV3_icon.Turnon()
        # else:
        #     self.PV3_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV4"]:
        #     self.PV4_icon.Turnon()
        # else:
        #     self.PV4_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV5"]:
        #     self.PV5_icon.Turnon()
        # else:
        #     self.PV5_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV6"]:
        #     self.PV6_icon.Turnon()
        # else:
        #     self.PV6_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV7"]:
        #     self.PV7_icon.Turnon()
        # else:
        #     self.PV7_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV8"]:
        #     self.PV8_icon.Turnon()
        # else:
        #     self.PV8_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV9"]:
        #     self.PV9_icon.Turnon()
        # else:
        #     self.PV9_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV10"]:
        #     self.PV10_icon.Turnon()
        # else:
        #     self.PV10_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV11"]:
        #     self.PV11_icon.Turnon()
        # else:
        #     self.PV11_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV12"]:
        #     self.PV12_icon.Turnon()
        # else:
        #     self.PV12_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV1000"]:
        #     self.PV1000_icon.Turnon()
        # else:
        #     self.PV1000_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV1001"]:
        #     self.PV1001_icon.Turnon()
        # else:
        #     self.PV1001_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV1002"]:
        #     self.PV1002_icon.Turnon()
        # else:
        #     self.PV1002_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV1003"]:
        #     self.PV1003_icon.Turnon()
        # else:
        #     self.PV1003_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV1004"]:
        #     self.PV1004_icon.Turnon()
        # else:
        #     self.PV1004_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV1005"]:
        #     self.PV1005_icon.Turnon()
        # else:
        #     self.PV1005_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV1006"]:
        #     self.PV1006_icon.Turnon()
        # else:
        #     self.PV1006_icon.Turnoff()
        #
        # if received_dic_c["data"]["Valve"]["OUT"]["PV1007"]:
        #     self.PV1007_icon.Turnon()
        # else:
        #     self.PV1007_icon.Turnoff()

        #      FLAGs
        # if received_dic_c["data"]["FLAG"]["Busy"]["MAN_TS"]:
        #     if received_dic_c["data"]["FLAG"]["value"]["MAN_TS"]:
        #         self.MAN_TS.Set.ButtonLClicked()
        #     else:
        #         self.MAN_TS.Set.ButtonRClicked()
        # elif not received_dic_c["data"]["FLAG"]["Busy"]["MAN_TS"]:
        #     if received_dic_c["data"]["FLAG"]["value"]["MAN_TS"] != self.FLAG_buffer["MAN_TS"]:
        #         if received_dic_c["data"]["FLAG"]["value"]["MAN_TS"]:
        #             self.MAN_TS.Set.ButtonLClicked()
        #         else:
        #             self.MAN_TS.Set.ButtonRClicked()
        #         self.FLAG_buffer["MAN_TS"] = received_dic_c["data"]["FLAG"]["value"]["MAN_TS"]
        #     else:
        #         pass
        # print("display",received_dic_c["data"]["FLAG"]["value"]["MAN_TS"],datetime.datetime.now())

        # if not received_dic_c["data"]["FLAG"]["MAN"]["MAN_HYD"]:
        #     if received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"]:
        #         self.MAN_HYD.Set.ButtonLClicked()
        #     else:
        #         self.MAN_HYD.Set.ButtonRClicked()
        # elif received_dic_c["data"]["FLAG"]["MAN"]["MAN_HYD"]:
        #     if received_dic_c["data"]["FLAG"]["Busy"]["MAN_HYD"]:
        #         if received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"]:
        #             self.MAN_HYD.Set.ButtonLClicked()
        #         else:
        #             self.MAN_HYD.Set.ButtonRClicked()
        #     elif not received_dic_c["data"]["FLAG"]["Busy"]["MAN_HYD"]:
        #         if received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"] != self.FLAG_buffer["MAN_HYD"]:
        #             if received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"]:
        #                 self.MAN_HYD.Set.ButtonLClicked()
        #             else:
        #                 self.MAN_HYD.Set.ButtonRClicked()
        #             self.FLAG__buffer["MAN_HYD"] = received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"]
        #         else:
        #             pass
        #
        # if received_dic_c["data"]["FLAG"]["Busy"]["MAN_HYD"]:
        #     if received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"]:
        #         self.MAN_HYD.Set.ButtonLClicked()
        #     else:
        #         self.MAN_HYD.Set.ButtonRClicked()
        # elif not received_dic_c["data"]["FLAG"]["Busy"]["MAN_HYD"]:
        #     if received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"] != self.FLAG_buffer["MAN_HYD"]:
        #         if received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"]:
        #             self.MAN_HYD.Set.ButtonLClicked()
        #         else:
        #             self.MAN_HYD.Set.ButtonRClicked()
        #         self.FLAG_buffer["MAN_HYD"] = received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"]
        #     else:
        #         pass

        # if received_dic_c["data"]["FLAG"]["value"]["MAN_HYD"]:
        #     self.MAN_HYD.Set.ButtonLClicked()
        # else:
        #     self.MAN_HYD.Set.ButtonRClicked()


        # set LOOPPID double button status ON/OFF also the status in the subwindow

        if not received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1001"]:
            if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]:
                self.HTR1001.LOOPPIDWindow.Mode.ButtonLClicked()
                self.HTR1001.State.ButtonLClicked()
            else:
                self.HTR1001.LOOPPIDWindow.Mode.ButtonRClicked()
                self.HTR1001.State.ButtonRClicked()
            self.LOOPPID_EN_buffer["HTR1001"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]
        elif received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1001"]:
            if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1001"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]:
                    self.HTR1001.LOOPPIDWindow.Mode.ButtonLClicked()
                    self.HTR1001.State.ButtonLClicked()
                else:
                    self.HTR1001.LOOPPIDWindow.Mode.ButtonRClicked()
                    self.HTR1001.State.ButtonRClicked()
                self.LOOPPID_EN_buffer["HTR1001"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]
            elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1001"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"] != self.LOOPPID_EN_buffer["HTR1001"]:
                    if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]:
                        self.HTR1001.LOOPPIDWindow.Mode.ButtonLClicked()
                        self.HTR1001.State.ButtonLClicked()
                    else:
                        self.HTR1001.LOOPPIDWindow.Mode.ButtonRClicked()
                        self.HTR1001.State.ButtonRClicked()
                    self.LOOPPID_EN_buffer["HTR1001"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]
                else:
                    pass

        self.HTR1001.ColorLabel(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"])
        self.HTR1001.Power.ColorButton(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.RTD1.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1001"][0])
        self.HTR1001.LOOPPIDWindow.RTD2.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1001"][1])

        if not received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1002"]:
            if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]:
                self.HTR1002.LOOPPIDWindow.Mode.ButtonLClicked()
                self.HTR1002.State.ButtonLClicked()
            else:
                self.HTR1002.LOOPPIDWindow.Mode.ButtonRClicked()
                self.HTR1002.State.ButtonRClicked()
            self.LOOPPID_EN_buffer["HTR1002"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]
        elif received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1002"]:
            if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1002"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]:
                    self.HTR1002.LOOPPIDWindow.Mode.ButtonLClicked()
                    self.HTR1002.State.ButtonLClicked()
                else:
                    self.HTR1002.LOOPPIDWindow.Mode.ButtonRClicked()
                    self.HTR1002.State.ButtonRClicked()
                self.LOOPPID_EN_buffer["HTR1002"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]
            elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1002"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"] != self.LOOPPID_EN_buffer["HTR1002"]:
                    if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]:
                        self.HTR1002.LOOPPIDWindow.Mode.ButtonLClicked()
                        self.HTR1002.State.ButtonLClicked()
                    else:
                        self.HTR1002.LOOPPIDWindow.Mode.ButtonRClicked()
                        self.HTR1002.State.ButtonRClicked()
                    self.LOOPPID_EN_buffer["HTR1002"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]
                else:
                    pass

        self.HTR1002.ColorLabel(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"])
        self.HTR1002.Power.ColorButton(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.RTD1.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1002"][0])
        self.HTR1002.LOOPPIDWindow.RTD2.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1002"][1])


        if not received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1003"]:
            if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]:
                self.HTR1003.LOOPPIDWindow.Mode.ButtonLClicked()
                self.HTR1003.State.ButtonLClicked()
            else:
                self.HTR1003.LOOPPIDWindow.Mode.ButtonRClicked()
                self.HTR1003.State.ButtonRClicked()
            self.LOOPPID_EN_buffer["HTR1003"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]
        elif received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1003"]:
            if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1003"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]:
                    self.HTR1003.LOOPPIDWindow.Mode.ButtonLClicked()
                    self.HTR1003.State.ButtonLClicked()
                else:
                    self.HTR1003.LOOPPIDWindow.Mode.ButtonRClicked()
                    self.HTR1003.State.ButtonRClicked()
                self.LOOPPID_EN_buffer["HTR1003"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]
            elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1003"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"] != self.LOOPPID_EN_buffer["HTR1003"]:
                    if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]:
                        self.HTR1003.LOOPPIDWindow.Mode.ButtonLClicked()
                        self.HTR1003.State.ButtonLClicked()
                    else:
                        self.HTR1003.LOOPPIDWindow.Mode.ButtonRClicked()
                        self.HTR1003.State.ButtonRClicked()
                    self.LOOPPID_EN_buffer["HTR1003"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]
                else:
                    pass

        self.HTR1003.ColorLabel(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"])
        self.HTR1003.Power.ColorButton(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.RTD1.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1003"][0])
        self.HTR1003.LOOPPIDWindow.RTD2.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1003"][1])



        if not received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1004"]:
            if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]:
                self.HTR1004.LOOPPIDWindow.Mode.ButtonLClicked()
                self.HTR1004.State.ButtonLClicked()
            else:
                self.HTR1004.LOOPPIDWindow.Mode.ButtonRClicked()
                self.HTR1004.State.ButtonRClicked()
            self.LOOPPID_EN_buffer["HTR1004"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]
        elif received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1004"]:
            if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1004"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]:
                    self.HTR1004.LOOPPIDWindow.Mode.ButtonLClicked()
                    self.HTR1004.State.ButtonLClicked()
                else:
                    self.HTR1004.LOOPPIDWindow.Mode.ButtonRClicked()
                    self.HTR1004.State.ButtonRClicked()
                self.LOOPPID_EN_buffer["HTR1004"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]
            elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1004"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"] != self.LOOPPID_EN_buffer["HTR1004"]:
                    if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]:
                        self.HTR1004.LOOPPIDWindow.Mode.ButtonLClicked()
                        self.HTR1004.State.ButtonLClicked()
                    else:
                        self.HTR1004.LOOPPIDWindow.Mode.ButtonRClicked()
                        self.HTR1004.State.ButtonRClicked()
                    self.LOOPPID_EN_buffer["HTR1004"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]
                else:
                    pass

        self.HTR1004.ColorLabel(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"])
        self.HTR1004.Power.ColorButton(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.RTD1.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1004"][0])
        self.HTR1004.LOOPPIDWindow.RTD2.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1004"][1])







        # set indicators value

        self.PT001.SetValue(received_dic_c["data"]["PT"]["value"]["PT001"])
        self.PT002.SetValue(received_dic_c["data"]["PT"]["value"]["PT002"])
        self.PT003.SetValue(received_dic_c["data"]["PT"]["value"]["PT003"])
        self.PT004.SetValue(received_dic_c["data"]["PT"]["value"]["PT004"])
        self.PT1000.SetValue(received_dic_c["data"]["PT"]["value"]["PT1000"])
        self.PT1001.SetValue(received_dic_c["data"]["PT"]["value"]["PT1001"])
        self.PT1002.SetValue(received_dic_c["data"]["PT"]["value"]["PT1002"])
        self.RTD7.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD7"])
        self.RTD8.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD8"])
        self.RTD9.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD9"])
        self.RTD10.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD10"])
        self.RTD11.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD11"])
        self.RTD12.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD12"])
        # self.TT1007.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["TT1007"])
        # self.TT1008.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["TT1008"])
        # self.TT1009.SetValue(received_dic_c["data"]["TT"]["AD2"]["value"]["TT1009"])
        self.LiqLev.SetValue(received_dic_c["data"]["LL"]["value"]["LL"])





        self.HTR1001.LOOPPIDWindow.Interlock.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["INTLKD"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.Error.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["ERR"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.MANSP.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1001"])
        if True in [received_dic_c["data"]["LOOPPID"]["SATHI"]["HTR1001"],
                    received_dic_c["data"]["LOOPPID"]["SATLO"]["HTR1001"]]:

            self.HTR1001.LOOPPIDWindow.SAT.UpdateColor(True)
        else:
            self.HTR1001.LOOPPIDWindow.SAT.UpdateColor(False)
        self.HTR1001.LOOPPIDWindow.ModeREAD.Field.setText(

            self.FindDistinctTrue(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1001"],
                                  received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1001"],
                                  received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1001"],
                                  received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1001"]))
        self.HTR1001.LOOPPIDWindow.EN.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.HIGH.SetValue(
            received_dic_c["data"]["LOOPPID"]["HI_LIM"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.LOW.SetValue(
            received_dic_c["data"]["LOOPPID"]["LO_LIM"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.SETSP.SetValue(
            self.FetchSetPoint(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["SET0"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["SET1"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["SET2"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["SET3"]["HTR1001"]))
        self.HTR1001.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1001"])

        self.HTR1002.LOOPPIDWindow.Interlock.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["INTLKD"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.Error.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["ERR"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.MANSP.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1002"])
        if True in [received_dic_c["data"]["LOOPPID"]["SATHI"]["HTR1002"],
                    received_dic_c["data"]["LOOPPID"]["SATLO"]["HTR1002"]]:

            self.HTR1002.LOOPPIDWindow.SAT.UpdateColor(True)
        else:
            self.HTR1002.LOOPPIDWindow.SAT.UpdateColor(False)
        self.HTR1002.LOOPPIDWindow.ModeREAD.Field.setText(

            self.FindDistinctTrue(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1002"],
                                  received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1002"],
                                  received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1002"],
                                  received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1002"]))
        self.HTR1002.LOOPPIDWindow.EN.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.HIGH.SetValue(
            received_dic_c["data"]["LOOPPID"]["HI_LIM"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.LOW.SetValue(
            received_dic_c["data"]["LOOPPID"]["LO_LIM"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.SETSP.SetValue(
            self.FetchSetPoint(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["SET0"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["SET1"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["SET2"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["SET3"]["HTR1002"]))
        self.HTR1002.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1002"])

        self.HTR1003.LOOPPIDWindow.Interlock.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["INTLKD"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.Error.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["ERR"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.MANSP.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1003"])
        if True in [received_dic_c["data"]["LOOPPID"]["SATHI"]["HTR1003"],
                    received_dic_c["data"]["LOOPPID"]["SATLO"]["HTR1003"]]:

            self.HTR1003.LOOPPIDWindow.SAT.UpdateColor(True)
        else:
            self.HTR1003.LOOPPIDWindow.SAT.UpdateColor(False)
        self.HTR1003.LOOPPIDWindow.ModeREAD.Field.setText(

            self.FindDistinctTrue(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1003"],
                                  received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1003"],
                                  received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1003"],
                                  received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1003"]))
        self.HTR1003.LOOPPIDWindow.EN.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.HIGH.SetValue(
            received_dic_c["data"]["LOOPPID"]["HI_LIM"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.LOW.SetValue(
            received_dic_c["data"]["LOOPPID"]["LO_LIM"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.SETSP.SetValue(
            self.FetchSetPoint(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["SET0"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["SET1"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["SET2"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["SET3"]["HTR1003"]))
        self.HTR1003.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1003"])



        self.HTR1004.LOOPPIDWindow.Interlock.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["INTLKD"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.Error.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["ERR"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.MANSP.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1004"])
        if True in [received_dic_c["data"]["LOOPPID"]["SATHI"]["HTR1004"],
                    received_dic_c["data"]["LOOPPID"]["SATLO"]["HTR1004"]]:

            self.HTR1004.LOOPPIDWindow.SAT.UpdateColor(True)
        else:
            self.HTR1004.LOOPPIDWindow.SAT.UpdateColor(False)
        self.HTR1004.LOOPPIDWindow.ModeREAD.Field.setText(

            self.FindDistinctTrue(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1004"],
                                  received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1004"],
                                  received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1004"],
                                  received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1004"]))
        self.HTR1004.LOOPPIDWindow.EN.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.HIGH.SetValue(
            received_dic_c["data"]["LOOPPID"]["HI_LIM"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.LOW.SetValue(
            received_dic_c["data"]["LOOPPID"]["LO_LIM"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.SETSP.SetValue(
            self.FetchSetPoint(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["SET0"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["SET1"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["SET2"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["SET3"]["HTR1004"]))
        self.HTR1004.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1004"])

        self.MFC1.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["FCV1001"])
        self.MFC1.LOOPPIDWindow.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["FCV1001"])

        self.MFC2.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["FCV1002"])
        self.MFC2.LOOPPIDWindow.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["FCV1002"])

        # self.MFC1008.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["FCV1001"])
        # self.MFC1008.LOOPPIDWindow.OUT.SetValue(received_dic_c["data"]["LEFT_REAL"]["FCV1001"])

    @QtCore.Slot(object)
    def update_alarmwindow(self, list):
        # if len(dic)>0:
        #     print(dic)
        print(list[0])
        if True in list:
            print('list', True)
        else:
            print('list', False)

        self.AlarmButton.CollectAlarm(list)
        # print("Alarm Status=", self.AlarmButton.Button.Alarm)
        if self.AlarmButton.Button.Alarm:
            self.AlarmButton.ButtonAlarmSetSignal()
            self.AlarmButton.SubWindow.ReassignRTD1Order()
            self.AlarmButton.SubWindow.ReassignRTD2Order()
            self.AlarmButton.SubWindow.ReassignRTD3Order()
            # self.AlarmButton.SubWindow.ReassignRTD4Order()
            self.AlarmButton.SubWindow.ReassignRTDLEFTOrder()
            self.AlarmButton.SubWindow.ReassignPTOrder()
            # self.AlarmButton.SubWindow.ReassignLEFTOrder()
            # self.AlarmButton.SubWindow.ReassignDinOrder()
            # self.AlarmButton.SubWindow.ReassignHTROrder()



        else:
            self.AlarmButton.ButtonAlarmResetSignal()
            self.AlarmButton.SubWindow.ResetOrder()

    # Lock/unlock controls
    def ActivateControls(self, Activate):
        # self.SV4327.Activate(Activate)
        # self.SV4328.Activate(Activate)
        # self.SV4329.Activate(Activate)
        # self.SV4331.Activate(Activate)
        # self.SV4332.Activate(Activate)
        # self.SV3307.Activate(Activate)
        # self.SV3310.Activate(Activate)
        # self.HFSV3312.Activate(Activate)
        # self.SV3322.Activate(Activate)
        # self.HFSV3323.Activate(Activate)
        # self.SV3325.Activate(Activate)
        # self.SV3329.Activate(Activate)
        # self.HFSV3331.Activate(Activate)
        return

    # This section call the right PLC function when you change a value on the display
    @QtCore.Slot(str)
    def SetSVMode(self, value):
        self.P.SetSValveMode(value)

    @QtCore.Slot(str)
    def SetHotRegionMode(self, value):
        self.PLC.SetHotRegionPIDMode(value)

    @QtCore.Slot(float)
    def SetHotRegionSetpoint(self, value):
        self.PLC.SetHotRegionSetpoint(value)

    @QtCore.Slot(float)
    def SetHotRegionP(self, value):
        self.PLC.SetHotRegionP(value)

    @QtCore.Slot(float)
    def SetHotRegionI(self, value):
        self.PLC.SetHotRegionI(value)

    @QtCore.Slot(float)
    def SetHotRegionD(self, value):
        self.PLC.SetHotRegionD(value)

    @QtCore.Slot(str)
    def SetColdRegionMode(self, value):
        self.PLC.SetColdRegionPIDMode(value)

    @QtCore.Slot(float)
    def SetColdRegionSetpoint(self, value):
        self.PLC.SetColdRegionSetpoint(value)

    @QtCore.Slot(float)
    def SetColdRegionP(self, value):
        self.PLC.SetColdRegionP(value)

    @QtCore.Slot(float)
    def SetColdRegionI(self, value):
        self.PLC.SetColdRegionI(value)

    @QtCore.Slot(float)
    def SetColdRegionD(self, value):
        self.PLC.SetColdRegionD(value)

    @QtCore.Slot(float)
    def SetBottomChillerSetpoint(self, value):
        self.PLC.SetColdRegionD(value)

    @QtCore.Slot(str)
    def SetBottomChillerState(self, value):
        self.PLC.SetBottomChillerState(value)

    @QtCore.Slot(float)
    def SetTopChillerSetpoint(self, value):
        self.PLC.SetTopChillerSetpoint(value)

    @QtCore.Slot(str)
    def SetTopChillerState(self, value):
        self.PLC.SetTopChillerState(value)

    @QtCore.Slot(float)
    def SetCameraChillerSetpoint(self, value):
        self.PLC.SetCameraChillerSetpoint(value)

    @QtCore.Slot(str)
    def SetCameraChillerState(self, value):
        self.PLC.SetCameraChillerState(value)

    @QtCore.Slot(str)
    def SetInnerHeaterState(self, value):
        self.PLC.SetInnerPowerState(value)

    @QtCore.Slot(float)
    def SetInnerHeaterPower(self, value):
        self.PLC.SetInnerPower(value)

    @QtCore.Slot(str)
    def SetFreonHeaterState(self, value):
        self.PLC.SetFreonPowerState(value)

    @QtCore.Slot(float)
    def SetFreonHeaterPower(self, value):
        self.PLC.SetFreonPower(value)

    @QtCore.Slot(str)
    def SetOuterCloseHeaterState(self, value):
        self.PLC.SetOuterClosePowerState(value)

    @QtCore.Slot(float)
    def SetOuterCloseHeaterPower(self, value):
        self.PLC.SetOuterClosePower(value)

    @QtCore.Slot(str)
    def SetOuterFarHeaterState(self, value):
        self.PLC.SetOuterFarPowerState(value)

    @QtCore.Slot(float)
    def SetOuterFarHeaterPower(self, value):
        self.PLC.SetOuterFarPower(value)

    @QtCore.Slot(float)
    def SetCoolingFlow(self, value):
        self.PLC.SetFlowValve(value)

    @QtCore.Slot(str)
    def setCartMode(self, value):
        if value == "Auto":
            self.P.GoIdle()
        elif value == "Manual":
            self.P.GoManual()

    @QtCore.Slot(float)
    def SetCartSetpoint(self, value):
        self.P.SetPressureSetpoint(value)

    @QtCore.Slot(str)
    def SetCartState(self, value):
        if value == "Compress":
            self.P.Compress()
        elif value == "Expand":
            self.P.Expand()

    @QtCore.Slot(float)
    def SetRegSetpoint(self, value):
        self.P.SetAirRegulatorSetpoint(value)

    @QtCore.Slot(str)
    def SetFast1(self, value):
        self.P.SetFastCompressValve1(value)

    @QtCore.Slot(str)
    def SetFast2(self, value):
        self.P.SetFastCompressValve2(value)

    @QtCore.Slot(str)
    def SetFast3(self, value):
        self.P.SetFastCompressValve3(value)

    @QtCore.Slot(str)
    def SetFreonIn(self, value):
        self.P.SetFreonInValve(value)

    @QtCore.Slot(str)
    def SetFreonOut(self, value):
        self.P.SetFreonOutValve(value)

    @QtCore.Slot(str)
    def SetFast(self, value):
        self.P.SetFastCompressValveCart(value)

    @QtCore.Slot(str)
    def SetSlow(self, value):
        self.P.SetSlowCompressValve(value)

    @QtCore.Slot(str)
    def SetExpansion(self, value):
        self.P.SetExpansionValve(value)

    @QtCore.Slot(str)
    def SetOil(self, value):
        self.P.SetOilReliefValve(value)

    @QtCore.Slot(str)
    def SetPump(self, value):
        self.P.SetPumpState(value)

    @QtCore.Slot(str)
    def SetWaterChillerState(self, value):
        self.PLC.SetWaterChillerState(value)

    @QtCore.Slot(float)
    def SetWaterChillerSetpoint(self, value):
        self.PLC.SetWaterChillerSetpoint(value)

    @QtCore.Slot(str)
    def SetPrimingValve(self, value):
        if value == "Open":
            self.PLC.SetWaterPrimingPower("On")
        elif value == "Close":
            self.PLC.SetWaterPrimingPower("Off")


class UpdateClient(QtCore.QObject):
    client_data_transport = QtCore.Signal()
    client_command_fectch = QtCore.Signal()
    client_clear_commands = QtCore.Signal()

    # def __init__(self, MW, parent=None):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")
        self.Running = False
        self.readcommand = False
        self.period = 1
        self.socket.setsockopt(zmq.LINGER, 0)

        print("client is connecting to the ZMQ server")

        self.TT_AD1_dic_ini = sec.TT_AD1_DIC
        self.TT_AD2_dic_ini = sec.TT_AD2_DIC
        self.HTRTD_dic_ini = sec.HTRTD_DIC
        self.PT_dic_ini = sec.PT_DIC
        self.LEFT_REAL_ini = sec.LEFT_REAL_DIC
        self.TT_AD1_LowLimit_ini = sec.TT_AD1_LOWLIMIT
        self.TT_AD1_HighLimit_ini = sec.TT_AD1_HIGHLIMIT
        self.TT_AD2_LowLimit_ini = sec.TT_AD2_LOWLIMIT
        self.TT_AD2_HighLimit_ini = sec.TT_AD2_HIGHLIMIT
        self.HTRTD_LowLimit_ini = sec.HTRTD_LOWLIMIT
        self.HTRTD_HighLimit_ini = sec.HTRTD_HIGHLIMIT
        self.PT_LowLimit_ini = sec.PT_LOWLIMIT
        self.PT_HighLimit_ini = sec.PT_HIGHLIMIT
        self.LEFT_REAL_LowLimit_ini = sec.LEFT_REAL_LOWLIMIT
        self.LEFT_REAL_HighLimit_ini = sec.LEFT_REAL_HIGHLIMIT
        self.TT_AD1_Alarm_ini = sec.TT_AD1_ALARM
        self.TT_AD2_Alarm_ini = sec.TT_AD2_ALARM
        self.HTRTD_Alarm_ini = sec.HTRTD_ALARM
        self.TT_AD1_Activated_ini = sec.TT_AD1_ACTIVATED
        self.TT_AD2_Activated_ini = sec.TT_AD2_ACTIVATED
        self.HTRTD_Activated_ini = sec.HTRTD_ACTIVATED
        self.PT_Activated_ini = sec.PT_ACTIVATED
        self.PT_Alarm_ini = sec.PT_ALARM
        self.LEFT_REAL_Activated_ini = sec.LEFT_REAL_ACTIVATED
        self.LEFT_REAL_Alarm_ini = sec.LEFT_REAL_ALARM
        self.MainAlarm_ini = sec.MAINALARM
        self.MAN_SET = sec.MAN_SET
        self.Valve_OUT_ini = sec.VALVE_OUT
        self.Valve_MAN_ini = sec.VALVE_MAN
        self.Valve_INTLKD_ini = sec.VALVE_INTLKD
        self.Valve_ERR_ini = sec.VALVE_ERR
        self.Valve_Busy_ini = sec.VALVE_BUSY
        # self.Switch_OUT_ini = sec.SWITCH_OUT
        # self.Switch_MAN_ini = sec.SWITCH_MAN
        # self.Switch_INTLKD_ini = sec.SWITCH_INTLKD
        # self.Switch_ERR_ini = sec.SWITCH_ERR
        self.Din_dic_ini = sec.DIN_DIC
        self.Din_HighLimit_ini = sec.DIN_HIGHLIMIT
        self.Din_LowLimit_ini = sec.DIN_LOWLIMIT
        self.Din_Activated_ini = sec.DIN_ACTIVATED
        self.Din_Alarm_ini = sec.DIN_ALARM

        self.LOOPPID_MODE0_ini = sec.LOOPPID_MODE0
        self.LOOPPID_MODE1_ini = sec.LOOPPID_MODE1
        self.LOOPPID_MODE2_ini = sec.LOOPPID_MODE2
        self.LOOPPID_MODE3_ini = sec.LOOPPID_MODE3
        self.LOOPPID_INTLKD_ini = sec.LOOPPID_INTLKD
        self.LOOPPID_MAN_ini = sec.LOOPPID_MAN
        self.LOOPPID_TT_ini = sec.LOOPPID_TT
        self.LOOPPID_ERR_ini = sec.LOOPPID_ERR
        self.LOOPPID_SATHI_ini = sec.LOOPPID_SATHI
        self.LOOPPID_SATLO_ini = sec.LOOPPID_SATLO
        self.LOOPPID_EN_ini = sec.LOOPPID_EN
        self.LOOPPID_OUT_ini = sec.LOOPPID_OUT
        self.LOOPPID_IN_ini = sec.LOOPPID_IN
        self.LOOPPID_HI_LIM_ini = sec.LOOPPID_HI_LIM
        self.LOOPPID_LO_LIM_ini = sec.LOOPPID_LO_LIM
        self.LOOPPID_SET0_ini = sec.LOOPPID_SET0
        self.LOOPPID_SET1_ini = sec.LOOPPID_SET1
        self.LOOPPID_SET2_ini = sec.LOOPPID_SET2
        self.LOOPPID_SET3_ini = sec.LOOPPID_SET3
        self.LOOPPID_Busy_ini = sec.LOOPPID_BUSY
        self.LOOPPID_Alarm_ini = sec.LOOPPID_ALARM
        self.LOOPPID_Activated_ini = sec.LOOPPID_ACTIVATED
        self.LOOPPID_Alarm_HighLimit_ini = sec.LOOPPID_ALARM_HI_LIM
        self.LOOPPID_Alarm_LowLimit_ini = sec.LOOPPID_ALARM_LO_LIM

        self.LOOP2PT_MODE0_ini = sec.LOOP2PT_MODE0
        self.LOOP2PT_MODE1_ini = sec.LOOP2PT_MODE1
        self.LOOP2PT_MODE2_ini = sec.LOOP2PT_MODE2
        self.LOOP2PT_MODE3_ini = sec.LOOP2PT_MODE3
        self.LOOP2PT_INTLKD_ini = sec.LOOP2PT_INTLKD
        self.LOOP2PT_MAN_ini = sec.LOOP2PT_MAN
        self.LOOP2PT_ERR_ini = sec.LOOP2PT_ERR
        self.LOOP2PT_OUT_ini = sec.LOOP2PT_OUT
        self.LOOP2PT_SET1_ini = sec.LOOP2PT_SET1
        self.LOOP2PT_SET2_ini = sec.LOOP2PT_SET2
        self.LOOP2PT_SET3_ini = sec.LOOP2PT_SET3
        self.LOOP2PT_Busy_ini = sec.LOOP2PT_BUSY

        self.Procedure_running_ini = sec.PROCEDURE_RUNNING
        self.Procedure_INTLKD_ini = sec.PROCEDURE_INTLKD
        self.Procedure_EXIT_ini = sec.PROCEDURE_EXIT

        self.INTLK_D_ADDRESS_ini = sec.INTLK_D_ADDRESS
        self.INTLK_D_DIC_ini = sec.INTLK_D_DIC
        self.INTLK_D_EN_ini = sec.INTLK_D_EN
        self.INTLK_D_COND_ini = sec.INTLK_D_COND
        self.INTLK_D_Busy_ini = sec.INTLK_D_BUSY
        self.INTLK_A_ADDRESS_ini = sec.INTLK_A_ADDRESS
        self.INTLK_A_DIC_ini = sec.INTLK_A_DIC
        self.INTLK_A_EN_ini = sec.INTLK_A_EN
        self.INTLK_A_COND_ini = sec.INTLK_A_COND
        self.INTLK_A_SET_ini = sec.INTLK_A_SET
        self.INTLK_A_Busy_ini = sec.INTLK_A_BUSY

        self.FLAG_ADDRESS_ini = sec.FLAG_ADDRESS
        self.FLAG_DIC_ini = sec.FLAG_DIC
        self.FLAG_INTLKD_ini = sec.FLAG_INTLKD
        self.FLAG_Busy_ini = sec.FLAG_BUSY

        self.FF_DIC_ini = copy.copy(sec.FF_DIC)
        self.PARAM_F_DIC_ini = copy.copy(sec.PARAM_F_DIC)
        self.PARAM_I_DIC_ini = copy.copy(sec.PARAM_I_DIC)
        self.PARAM_B_DIC_ini = copy.copy(sec.PARAM_B_DIC)
        self.PARAM_T_DIC_ini = copy.copy(sec.PARAM_T_DIC)
        self.TIME_DIC_ini = copy.copy(sec.TIME_DIC)

        self.Ini_Check_ini = sec.INI_CHECK

        self.LL_dic_ini = sec.LL_DIC
        self.LL_LowLimit_ini = sec.LL_LOWLIMIT
        self.LL_HighLimit_ini = sec.LL_HIGHLIMIT
        self.LL_Alarm_ini = sec.LL_ALARM
        self.LL_Activated_ini = sec.LL_ACTIVATED

        self.Ini_Check_ini = sec.INI_CHECK

        self.receive_dic =  {"data": {"TT": {"AD1": {"value": self.TT_AD1_dic_ini, "high": self.TT_AD1_HighLimit_ini, "low": self.TT_AD1_LowLimit_ini},
                                         "AD2": {"value": self.TT_AD2_dic_ini, "high": self.TT_AD2_HighLimit_ini, "low": self.TT_AD2_LowLimit_ini},
                                         "LS":{"value": self.HTRTD_dic_ini, "high": self.HTRTD_HighLimit_ini, "low": self.HTRTD_HighLimit_ini}},
                                  "PT": {"value": self.PT_dic_ini, "high": self.PT_HighLimit_ini, "low": self.PT_LowLimit_ini},
                                  "LEFT_REAL": {"value": self.LEFT_REAL_ini, "high": self.LEFT_REAL_HighLimit_ini, "low": self.LEFT_REAL_LowLimit_ini},
                                  "LL": {"value": self.LL_dic_ini, "high": self.LL_HighLimit_ini,
                                         "low": self.LL_LowLimit_ini},
                                  "Valve": {"OUT": self.Valve_OUT_ini,
                                            "INTLKD": self.Valve_INTLKD_ini,
                                            "MAN": self.Valve_MAN_ini,
                                            "ERR": self.Valve_ERR_ini,
                                            "Busy":self.Valve_Busy_ini},
                                  # "Switch": {"OUT": self.Switch_OUT_ini,
                                  #            "INTLKD": self.Switch_INTLKD_ini,
                                  #            "MAN": self.Switch_MAN_ini,
                                  #            "ERR": self.Switch_ERR_ini},
                                  "Din": {'value': self.Din_dic_ini,"high": self.Din_HighLimit_ini, "low": self.Din_LowLimit_ini},
                                  "LOOPPID": {"MODE0": self.LOOPPID_MODE0_ini,
                                              "MODE1": self.LOOPPID_MODE1_ini,
                                              "MODE2": self.LOOPPID_MODE2_ini,
                                              "MODE3": self.LOOPPID_MODE3_ini,
                                              "INTLKD": self.LOOPPID_INTLKD_ini,
                                              "TT":self.LOOPPID_TT_ini,
                                              "MAN": self.LOOPPID_MAN_ini,
                                              "ERR": self.LOOPPID_ERR_ini,
                                              "SATHI": self.LOOPPID_SATHI_ini,
                                              "SATLO": self.LOOPPID_SATLO_ini,
                                              "EN": self.LOOPPID_EN_ini,
                                              "OUT": self.LOOPPID_OUT_ini,
                                              "IN": self.LOOPPID_IN_ini,
                                              "HI_LIM": self.LOOPPID_HI_LIM_ini,
                                              "LO_LIM": self.LOOPPID_LO_LIM_ini,
                                              "SET0": self.LOOPPID_SET0_ini,
                                              "SET1": self.LOOPPID_SET1_ini,
                                              "SET2": self.LOOPPID_SET2_ini,
                                              "SET3": self.LOOPPID_SET3_ini,
                                              "Busy":self.LOOPPID_Busy_ini,
                                              "Alarm":self.LOOPPID_Alarm_ini,
                                              "Alarm_HighLimit":self.LOOPPID_Alarm_HighLimit_ini,
                                              "Alarm_LowLimit":self.LOOPPID_Alarm_LowLimit_ini},
                                  "LOOP2PT": {"MODE0": self.LOOP2PT_MODE0_ini,
                                              "MODE1": self.LOOP2PT_MODE1_ini,
                                              "MODE2": self.LOOP2PT_MODE2_ini,
                                              "MODE3": self.LOOP2PT_MODE3_ini,
                                              "INTLKD": self.LOOP2PT_INTLKD_ini,
                                              "MAN": self.LOOP2PT_MAN_ini,
                                              "ERR": self.LOOP2PT_ERR_ini,
                                              "OUT": self.LOOP2PT_OUT_ini,
                                              "SET1": self.LOOP2PT_SET1_ini,
                                              "SET2": self.LOOP2PT_SET2_ini,
                                              "SET3": self.LOOP2PT_SET3_ini,
                                              "Busy":self.LOOP2PT_Busy_ini},
                                  "INTLK_D": {"value": self.INTLK_D_DIC_ini,
                                              "EN": self.INTLK_D_EN_ini,
                                              "COND": self.INTLK_D_COND_ini,
                                              "Busy":self.INTLK_D_Busy_ini},
                                  "INTLK_A": {"value":self.INTLK_A_DIC_ini,
                                              "EN":self.INTLK_A_EN_ini,
                                              "COND":self.INTLK_A_COND_ini,
                                              "SET":self.INTLK_A_SET_ini,
                                              "Busy":self.INTLK_A_Busy_ini},
                                  "FLAG": {"value":self.FLAG_DIC_ini,
                                           "INTLKD":self.FLAG_INTLKD_ini,
                                           "Busy":self.FLAG_Busy_ini},
                                  "Procedure": {"Running": self.Procedure_running_ini, "INTLKD": self.Procedure_INTLKD_ini, "EXIT": self.Procedure_EXIT_ini},
                                  "FF":self.FF_DIC_ini,
                                  "PARA_I":self.PARAM_I_DIC_ini,
                                  "PARA_F":self.PARAM_F_DIC_ini,
                                  "PARA_B":self.PARAM_B_DIC_ini,
                                  "PARA_T":self.PARAM_T_DIC_ini,
                                  "TIME":self.TIME_DIC_ini},
                         "Alarm": {"TT": {"AD1": self.TT_AD1_Alarm_ini,
                                          "AD2": self.TT_AD2_Alarm_ini,
                                          "LS":self.HTRTD_Alarm_ini
                                          },
                                   "PT": self.PT_Alarm_ini,
                                   "LEFT_REAL": self.LEFT_REAL_Alarm_ini,
                                   "Din": self.Din_Alarm_ini,
                                   "LOOPPID": self.LOOPPID_Alarm_ini,
                                   "LL":self.LL_Alarm_ini},
                         "Active": {"TT": {"AD1": self.TT_AD1_Activated_ini,
                                           "AD2": self.TT_AD2_Activated_ini,
                                           "LS":self.HTRTD_Activated_ini},
                                   "PT": self.PT_Activated_ini,
                                   "LEFT_REAL": self.LEFT_REAL_Activated_ini,
                                    "Din": self.Din_Activated_ini,
                                    "LOOPPID": self.LOOPPID_Activated_ini,
                                    "INI_CHECK": self.Ini_Check_ini,
                                    "LL":self.LL_Activated_ini},
                         "MainAlarm": self.MainAlarm_ini
                         }


        self.commands_package = pickle.dumps({})

    @QtCore.Slot()
    def run(self):
        self.Running = True
        while self.Running:
            try:

                print(f"Sending request...")

                #  Send reply back to client
                # self.socket.send(b"Hello")

                self.client_command_fectch.emit()
                # # wait until command read from the main thread
                while not self.readcommand:
                    print("read command from GUI...")
                    time.sleep(0.1)
                self.readcommand = False

                # self.commands({})
                # print(self.receive_dic)
                message = pickle.loads(self.socket.recv())

                # print(f"Received reply [ {message} ]")
                self.update_data(message)
                time.sleep(self.period)
            except:
                (type, value, traceback) = sys.exc_info()
                exception_hook(type, value, traceback)

    @QtCore.Slot()
    def stop(self):
        self.Running = False
        try:
            self.socket.send('bye')
            self.socket.recv()
        except:
            print("Error disconnecting.")
        self.socket.close()

    def update_data(self, message):
        # message mush be a dictionary
        self.receive_dic = message
        self.client_data_transport.emit()

    @QtCore.Slot(object)
    def commands(self, MWcommands):
        # claim that whether MAN_SET is True or false
        print("Commands are here", datetime.datetime.now())
        print("commands", MWcommands)
        self.commands_package = pickle.dumps(MWcommands)
        print("commands len", len(MWcommands))
        if len(MWcommands) != 0:
            self.socket.send(self.commands_package)
            self.client_clear_commands.emit()
        else:
            self.socket.send(pickle.dumps({}))
        self.readcommand = True
        print("finished sending commands")


# Code entry point

if __name__ == "__main__":

    App = QtWidgets.QApplication(sys.argv)

    MW = MainWindow()

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

    # AW = AlarmWin()
    # if platform.system() == "Linux":
    #     AW.show()
    #     AW.showMinimized()
    # else:
    #     AW.show()
    # AW.activateWindow()
    # sys.exit(App.exec_())

"""
Note to run on VS on my computer...

import os
os.chdir("D:\\Pico\\SlowDAQ\\Qt\\SlowDAQ")
exec(open("SlowDAQ.py").read())
"""
