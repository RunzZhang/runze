"""
This is the main SlowDAQ code used to read/setproperties of the TPLC and PPLC

By: Mathieu Laurin

v0.1.0 Initial code 29/11/19 ML
v0.1.1 Read and write implemented 08/12/19 ML
v0.1.2 Alarm implemented 07/01/20 ML
v0.1.3 PLC online detection, poll PLCs only when values are updated, fix Centos window size bug 04/03/20 ML
"""

import os, sys, time, platform, datetime, random, pickle, cgitb, copy

from PySide2 import QtWidgets, QtCore, QtGui

#from SlowDAQ_UCSB_v2 import *
from PLC import *
from PICOPW import VerifyPW
from SlowDAQWidgets_UCSB_v2 import *
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

# SMALL_LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 10px; font-family: \"Calibri\";" \
#                     " font-size: 14px;" \
#                     " font-weight: bold;"

# LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 10px; font-family: \"Calibri\"; " \
#               "font-size: 18px; font-weight: bold;"
# TITLE_STYLE = "background-color: rgb(204,204,204); border-radius: 10px; font-family: \"Calibri\";" \
#               " font-size: 22px; font-weight: bold;"

# Settings adapted to sbc slowcontrol machine
SMALL_LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Times\";" \
                    " font-size: 10px;" \
                    " font-weight: bold;"
LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Times\"; " \
              "font-size: 12px; font-weight: bold;"
TITLE_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Times\";" \
              " font-size: 14px; font-weight: bold;"

BORDER_STYLE = " border-radius: 2px; border-color: black;"

# SMALL_LABEL_STYLE = " background-color: rgb(204,204,204); "
# #
# LABEL_STYLE = " background-color: rgb(204,204,204); "
# TITLE_STYLE = " background-color: rgb(204,204,204); "
# BORDER_STYLE = "  "


# SMALL_LABEL_STYLE = "background-color: rgb(204,204,204);  " \
#                         " font-size: 10px;" \
#
# LABEL_STYLE = "background-color: rgb(204,204,204);  " \
#                   "font-size: 12px; "
# TITLE_STYLE = "background-color: rgb(204,204,204);  " \
#                   "  font-size: 14px;"




ADMIN_TIMER = 30000
PLOTTING_SCALE = 0.66
ADMIN_PASSWORD = "60b6a2988e4ee1ad831ad567ad938adcc8e294825460bbcab26c1948b935bdf133e9e2c98ad4eafc622f4" \
                 "f5845cf006961abcc0a4007e3ac87d26c8981b792259f3f4db207dc14dbff315071c2f419122f1367668" \
                 "31c12bff0da3a2314ca2266"


R=0.6 # Resolution settings


sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print("ExceptType: ", exctype, "Value: ", value, "Traceback: ", traceback)
    # sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook


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
        #print(self.ImagePath)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.resize(2400*R, 1400*R)  # Open at center using resized
        self.setMinimumSize(2400*R, 1400*R)
        self.setWindowTitle("SlowDAQ " + VERSION)
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.ImagePath, "ucsb_phy.jpg")))

        # Tabs, backgrounds & labels

        self.Tab = QtWidgets.QTabWidget(self)
        self.Tab.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Tab.setStyleSheet("font-weight: bold; font-size: 20px; font-family: Times;")
        self.Tab.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.Tab.setGeometry(QtCore.QRect(0*R, 0*R, 2400*R, 1400*R))

        self.ThermosyphonTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.ThermosyphonTab, "Thermosyphon Main Panel")

        self.ThermosyphonTab.Background = QtWidgets.QLabel(self.ThermosyphonTab)
        self.ThermosyphonTab.Background.setScaledContents(True)
        self.ThermosyphonTab.Background.setStyleSheet('background-color:black;')
        pixmap_thermalsyphon = QtGui.QPixmap(os.path.join(self.ImagePath,"henry_ts_panel.png"))
        pixmap_thermalsyphon = pixmap_thermalsyphon.scaledToWidth(2400*R)
        self.ThermosyphonTab.Background.setPixmap(QtGui.QPixmap(pixmap_thermalsyphon))
        self.ThermosyphonTab.Background.move(0*R, 0*R)
        self.ThermosyphonTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.GasTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.GasTab, "Gas Panel")

        self.GasTab.Background = QtWidgets.QLabel(self.GasTab)
        self.GasTab.Background.setScaledContents(True)
        self.GasTab.Background.setStyleSheet('background-color:black;')
        pixmap_gas = QtGui.QPixmap(os.path.join(self.ImagePath,"henry_gas_panel.png"))
        pixmap_gas = pixmap_gas.scaledToWidth(2400 * R)
        self.GasTab.Background.setPixmap(QtGui.QPixmap(pixmap_gas))
        self.GasTab.Background.move(0 * R, 0 * R)
        self.GasTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.TubeTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.TubeTab, "Inner Tube")

        self.TubeTab.Background = QtWidgets.QLabel(self.TubeTab)
        self.TubeTab.Background.setScaledContents(True)
        self.TubeTab.Background.setStyleSheet('background-color:black;')
        pixmap_tube = QtGui.QPixmap(os.path.join(self.ImagePath,"henry_tube.png"))
        pixmap_tube = pixmap_tube.scaledToWidth(2400 * R)
        self.TubeTab.Background.setPixmap(QtGui.QPixmap(pixmap_tube))
        self.TubeTab.Background.move(0 * R, 0 * R)
        self.TubeTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.DatanSignalTab = QtWidgets.QWidget(self.Tab)
        self.Tab.addTab(self.DatanSignalTab, "Data and Signal Panel")

        self.DatanSignalTab.Background = QtWidgets.QLabel(self.DatanSignalTab)
        self.DatanSignalTab.Background.setScaledContents(True)
        self.DatanSignalTab.Background.setStyleSheet('background-color:black;')
        pixmap_DatanSignal = QtGui.QPixmap(os.path.join(self.ImagePath,"Default_Background"))
        pixmap_DatanSignal = pixmap_DatanSignal.scaledToWidth(2400*R)
        self.DatanSignalTab.Background.setPixmap(QtGui.QPixmap(pixmap_DatanSignal))
        self.DatanSignalTab.Background.move(0*R, 0*R)
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
        self.ReadSettings.move(50*R, 50*R)
        self.ReadSettings.LoadFileButton.clicked.connect(
            lambda x: self.Recover(address=self.ReadSettings.FilePath.text()))

        self.SaveSettings = CustomSave(self.DatanSignalTab)
        self.SaveSettings.move(700*R, 50*R)
        self.SaveSettings.SaveFileButton.clicked.connect(
            lambda x: self.Save(directory=self.SaveSettings.Head, project=self.SaveSettings.Tail))


        # Alarm button
        self.AlarmWindow = AlarmWin()
        self.AlarmButton = AlarmButton(self.AlarmWindow, self)
        self.AlarmButton.SubWindow.resize(1000*R, 500*R)
        # self.AlarmButton.StatusWindow.AlarmWindow()

        self.AlarmButton.move(2100*R, 50*R)
        self.AlarmButton.Button.setText("Alarm Button")


        #Thermosyphon Widgets
        self.PV1001 = Valve(self.ThermosyphonTab)
        self.PV1001.Label.setText("PV1001")
        self.PV1001.move(1015 *R,155*R)

        self.PV1002 = Valve(self.ThermosyphonTab)
        self.PV1002.Label.setText("PV1002")
        self.PV1002.move(2115 * R, 920 * R)

        self.PV1003 = Valve(self.ThermosyphonTab)
        self.PV1003.Label.setText("PV1003")
        self.PV1003.move(2115 * R, 1257 * R)

        self.PV1004 = Valve(self.ThermosyphonTab)
        self.PV1004.Label.setText("PV1004")
        self.PV1004.move(1500 * R, 1100 * R)

        self.PV1005 = Valve(self.ThermosyphonTab)
        self.PV1005.Label.setText("PV1005")
        self.PV1005.move(1440 * R, 585 * R)

        self.PV1006 = Valve(self.ThermosyphonTab)
        self.PV1006.Label.setText("PV1006")
        self.PV1006.move(865 * R, 925 * R)

        self.PV1007 = Valve(self.ThermosyphonTab)
        self.PV1007.Label.setText("PV1007")
        self.PV1007.move(865* R, 1257 * R)

        self.MFC1008 = Heater(self.ThermosyphonTab)
        self.MFC1008.move(1795 * R, 700 * R)
        self.MFC1008.Label.setText("MFC1008")
        self.MFC1008.HeaterSubWindow.setWindowTitle("MFC1008")
        self.MFC1008.HeaterSubWindow.Label.setText("MFC1008")

        self.PT1000 = PressureIndicator(self.ThermosyphonTab)
        self.PT1000.Label.setText("PT1000")
        self.PT1000.move(145 * R, 30 * R)

        self.PT1001 = PressureIndicator(self.ThermosyphonTab)
        self.PT1001.Label.setText("PT1001")
        self.PT1001.move(155 * R, 975 * R)

        self.PT1002 = PressureIndicator(self.ThermosyphonTab)
        self.PT1002.Label.setText("PT1002")
        self.PT1002.move(160 * R, 1160 * R)

        #Gas Panel Widgets
        
        #self.PNV001 = Valve(self.GasTab)
        #self.PNV001.Label.setText("PNV001")
        #self.PNV001.move(470 * R, 750 * R)

        self.BGA1 = PressureIndicator(self.GasTab)
        self.BGA1.Label.setText("BGA1")
        self.BGA1.move(1350 * R, 350 * R)

        self.BGA2 = PressureIndicator(self.GasTab)
        self.BGA2.Label.setText("BGA2")
        self.BGA2.move(1700 * R, 350 * R)

        self.PT001 = PressureIndicator(self.GasTab)
        self.PT001.Label.setText("PT001")
        self.PT001.move(190 * R, 560 * R)

        self.PT002 = PressureIndicator(self.GasTab)
        self.PT002.Label.setText("PT002")
        self.PT002.move(1073 * R, 445 * R)
        
        self.PT003 = PressureIndicator(self.GasTab)
        self.PT003.Label.setText("PT003")
        self.PT003.move(1091 * R, 740 * R)

        self.PT004 = PressureIndicator(self.GasTab)
        self.PT004.Label.setText("PT004")
        self.PT004.move(1455 * R, 440 * R)

        """
        self.IDPV001 = PnID_Alone(self.GasTab)
        self.IDPV001.Label.setText("PV001")
        self.IDPV001.move(1360 * R, 800 * R)

        self.IDPV002 = PnID_Alone(self.GasTab)
        self.IDPV002.Label.setText("PV002")
        self.IDPV002.move(1420 * R, 800 * R)

        self.IDPV003 = PnID_Alone(self.GasTab)
        self.IDPV003.Label.setText("PV003")
        self.IDPV003.move(1500 * R, 800 * R)

        self.IDPV004 = PnID_Alone(self.GasTab)
        self.IDPV004.Label.setText("PV004")
        self.IDPV004.move(1580 * R, 800 * R)

        self.IDPV005 = PnID_Alone(self.GasTab)
        self.IDPV005.Label.setText("PV005")
        self.IDPV005.move(1660 * R, 800 * R)

        self.IDPV006 = PnID_Alone(self.GasTab)
        self.IDPV006.Label.setText("PV006")
        self.IDPV006.move(1740 * R, 800 * R)

        self.IDPV007 = PnID_Alone(self.GasTab)
        self.IDPV007.Label.setText("PV007")
        self.IDPV007.move(1820 * R, 800 * R)

        self.IDPV008 = PnID_Alone(self.GasTab)
        self.IDPV008.Label.setText("PV008")
        self.IDPV008.move(1900 * R, 800 * R)

        self.IDPV009 = PnID_Alone(self.GasTab)
        self.IDPV009.Label.setText("PV009")
        self.IDPV009.move(1980 * R, 800 * R)

        self.IDPV010 = PnID_Alone(self.GasTab)
        self.IDPV010.Label.setText("PV010")
        self.IDPV010.move(2060 * R, 800 * R)

        self.IDPV011 = PnID_Alone(self.GasTab)
        self.IDPV011.Label.setText("PV011")
        self.IDPV011.move(2140 * R, 800 * R)
        """

        self.PV001 = Valve(self.GasTab)
        self.PV001.Label.setText("PV001")
        self.PV001.move(890*R,960*R)

        self.PV002 = Valve(self.GasTab)
        self.PV002.Label.setText("PV002")
        self.PV002.move(1840 * R, 415 * R)

        self.PV003 = Valve(self.GasTab)
        self.PV003.Label.setText("PV003")
        self.PV003.move(1840 * R, 492 * R)

        self.PV004 = Valve(self.GasTab)
        self.PV004.Label.setText("PV004")
        self.PV004.move(1840 * R, 569* R)

        self.PV005 = Valve(self.GasTab)
        self.PV005.Label.setText("PV005")
        self.PV005.move(1840 * R, 646 * R)

        self.PV006 = Valve(self.GasTab)
        self.PV006.Label.setText("PV006")
        self.PV006.move(1840 * R, 723 * R)

        self.PV007 = Valve(self.GasTab)
        self.PV007.Label.setText("PV007")
        self.PV007.move(1840 * R, 800 * R)

        self.PV008 = Valve(self.GasTab)
        self.PV008.Label.setText("PV008")
        self.PV008.move(1840 * R, 877 * R)

        self.PV009 = Valve(self.GasTab)
        self.PV009.Label.setText("PV009")
        self.PV009.move(1840 * R, 954 * R)

        self.PV010 = Valve(self.GasTab)
        self.PV010.Label.setText("PV010")
        self.PV010.move(1840 * R, 1031 * R)

        self.PV011 = Valve(self.GasTab)
        self.PV011.Label.setText("PV011")
        self.PV011.move(1840 * R, 1108 * R)

        self.PV012 = Valve(self.GasTab)
        self.PV012.Label.setText("PV012")
        self.PV012.move(1840 * R, 1185 * R)

        self.PV013 = Valve(self.GasTab)
        self.PV013.Label.setText("PV013")
        self.PV013.move(1840 * R, 1262 * R)

        self.MFC1 = Heater(self.GasTab)
        self.MFC1.move(1160 * R, 525 * R)
        self.MFC1.Label.setText("MFC1")
        self.MFC1.HeaterSubWindow.setWindowTitle("MFC1")
        self.MFC1.HeaterSubWindow.Label.setText("MFC1")

        self.MFC2 = Heater(self.GasTab)
        self.MFC2.move(1525 * R, 525 * R)
        self.MFC2.Label.setText("MFC2")
        self.MFC2.HeaterSubWindow.setWindowTitle("MFC2")
        self.MFC2.HeaterSubWindow.Label.setText("MFC2")


        # inner tube widgets 


        self.RTD1 = Indicator(self.TubeTab)
        self.RTD1.Label.setText("RTD1")
        self.RTD1.move(145 * R, 30 * R)

        self.RTD2 = Indicator(self.TubeTab)
        self.RTD2.Label.setText("RTD2")
        self.RTD2.move(145 * R, 80 * R)

        self.RTD3 = Indicator(self.TubeTab)
        self.RTD3.Label.setText("RTD3")
        self.RTD3.move(145 * R, 130 * R)

        self.RTD4 = Indicator(self.TubeTab)
        self.RTD4.Label.setText("RTD4")
        self.RTD4.move(145 * R, 180 * R)

        self.RTD5 = Indicator(self.TubeTab)
        self.RTD5.Label.setText("RTD5")
        self.RTD5.move(145 * R, 230 * R)

        self.RTD6 = Indicator(self.TubeTab)
        self.RTD6.Label.setText("RTD6")
        self.RTD6.move(145 * R, 280 * R)

        self.LiqLev = LiquidLevel(self.TubeTab)
        self.LiqLev.Label.setText("Liq Lev")
        self.LiqLev.move(145 * R, 330 * R)
        
        self.H1 = Heater(self.TubeTab)
        self.H1.move(295 * R, 30 * R)
        self.H1.Label.setText("Heater1")
        self.H1.HeaterSubWindow.setWindowTitle("Heater1")
        self.H1.HeaterSubWindow.Label.setText("Heater1")

        self.H2 = Heater(self.TubeTab)
        self.H2.move(295 * R, 130 * R)
        self.H2.Label.setText("Heater2")
        self.H2.HeaterSubWindow.setWindowTitle("Heater2")
        self.H2.HeaterSubWindow.Label.setText("Heater2")

        self.H3 = Heater(self.TubeTab)
        self.H3.move(295 * R, 230 * R)
        self.H3.Label.setText("Heater3")
        self.H3.HeaterSubWindow.setWindowTitle("Heater3")
        self.H3.HeaterSubWindow.Label.setText("Heater3")

        self.H4 = Heater(self.TubeTab)
        self.H4.move(295 * R, 330 * R)
        self.H4.Label.setText("Heater4")
        self.H4.HeaterSubWindow.setWindowTitle("Heater4")
        self.H4.HeaterSubWindow.Label.setText("Heater4")

        self.H5 = Heater(self.TubeTab)
        self.H5.move(295 * R, 430 * R)
        self.H5.Label.setText("Heater5")
        self.H5.HeaterSubWindow.setWindowTitle("Heater5")
        self.H5.HeaterSubWindow.Label.setText("Heater5")


        self.IDH1 = PnID_Alone(self.TubeTab)
        self.IDH1.Label.setText("Heater 1")
        self.IDH1.move(800 * R, 100 * R)

        self.IDH2 = PnID_Alone(self.TubeTab)
        self.IDH2.Label.setText("Heater 2")
        self.IDH2.move(800 * R, 160 * R)

        self.IDH3 = PnID_Alone(self.TubeTab)
        self.IDH3.Label.setText("Heater 3")
        self.IDH3.move(1342 * R, 705 * R)

        self.IDH4 = PnID_Alone(self.TubeTab)
        self.IDH4.Label.setText("Heater 4")
        self.IDH4.move(1267 * R, 1020 * R)

        self.IDH5 = PnID_Alone(self.TubeTab)
        self.IDH5.Label.setText("Heater 5")
        self.IDH5.move(1417 * R, 1020 * R)

        self.IDRTD1 = PnID_Alone(self.TubeTab)
        self.IDRTD1.Label.setText("RTD 1")
        self.IDRTD1.move(1150 * R, 940 * R)

        self.IDRTD2 = PnID_Alone(self.TubeTab)
        self.IDRTD2.Label.setText("RTD 2")
        self.IDRTD2.move(1515 * R, 940 * R)

        self.IDRTD3 = PnID_Alone(self.TubeTab)
        self.IDRTD3.Label.setText("RTD 3")
        self.IDRTD3.move(1342 * R, 725 * R)

        self.IDRTD4 = PnID_Alone(self.TubeTab)
        self.IDRTD4.Label.setText("RTD 4")
        self.IDRTD4.move(1342 * R, 685 * R)

        self.IDRTD5 = PnID_Alone(self.TubeTab)
        self.IDRTD5.Label.setText("RTD 5")
        self.IDRTD5.move(800 * R, 130 * R)

        #self.IDRTD6 = PnID_Alone(self.TubeTab)
        #self.IDRTD6.Label.setText("RTD 6")
        #self.IDRTD6.move(145 * R, 490 * R)
        


        #commands stack
        self.address = sec.merge_dic(sec.TT_AD1_ADDRESS,sec.TT_AD2_ADDRESS,sec.PT_ADDRESS,sec.LEFT_REAL_ADDRESS,sec.VALVE_ADDRESS,sec.LOOPPID_ADR_BASE,sec.PROCEDURE_ADDRESS, sec.INTLK_A_ADDRESS)
        self.commands = {}

        self.signal_connection()

        self.command_buffer_waiting = 1
        # self.statustransition={}

        self.Valve_buffer = copy.copy(sec.VALVE_OUT)
        self.CHECKED = False

        self.LOOPPID_EN_buffer = copy.copy(sec.LOOPPID_EN)


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
        # self.SV3326.Signals.sSignal.connect(self.SetSVMode)
        # self.SV3329.Signals.sSignal.connect(self.SetSVMode)
        # self.HFSV3331.Signals.sSignal.connect(self.SetSVMode)
        self.LoginT.Button.clicked.connect(self.ChangeUser)
        self.LoginP.Button.clicked.connect(self.ChangeUser)


        App.aboutToQuit.connect(self.StopUpdater)
        # Start display updater;
        self.StartUpdater()

    def StartUpdater(self):
        # Open connection to both PLCs
        # self.PLC = PLC()

        # Read PLC value on another thread
        # self.PLCUpdateThread = QtCore.QThread()
        # self.UpPLC = UpdatePLC(self.PLC)
        # self.UpPLC.moveToThread(self.PLCUpdateThread)
        # self.PLCUpdateThread.started.connect(self.UpPLC.run)
        # self.PLCUpdateThread.start()

        self.ClientUpdateThread = QtCore.QThread()
        self.UpClient = UpdateClient(self)
        self.UpClient.moveToThread(self.ClientUpdateThread)
        self.ClientUpdateThread.started.connect(self.UpClient.run)
        self.ClientUpdateThread.start()


        # Make sure PLCs values are initialized before trying to access them with update function
        time.sleep(2)

        # Update display values on another thread
        self.DUpdateThread = QtCore.QThread()
        self.UpDisplay = UpdateDisplay(self,self.UpClient)
        self.UpDisplay.moveToThread(self.DUpdateThread)
        self.DUpdateThread.started.connect(self.UpDisplay.run)
        self.DUpdateThread.start()


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


        # # Beckoff RTDs

        #
        # #FP rtd updatebutton
        #
        # self.AlarmButton.SubWindow.TT2420.updatebutton.clicked.connect(
        #     lambda: self.FPTTBoxUpdate(pid=self.AlarmButton.SubWindow.TT2420.Label.text(),
        #                                Act=self.AlarmButton.SubWindow.TT2420.AlarmMode.isChecked(),
        #                                LowLimit=self.AlarmButton.SubWindow.TT2420.Low_Limit.Field.text(),
        #                                HighLimit=self.AlarmButton.SubWindow.TT2420.High_Limit.Field.text()))



        #PT settings

        self.AlarmButton.SubWindow.PT1000.updatebutton.clicked.connect(
            lambda: self.FPTTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1000.Label.text(),
                                       Act=self.AlarmButton.SubWindow.PT1000.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.PT1000.Low_Limit.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.PT1000.High_Limit.Field.text()))

        self.AlarmButton.SubWindow.PT1001.updatebutton.clicked.connect(
            lambda: self.FPTTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1001.Label.text(),
                                       Act=self.AlarmButton.SubWindow.PT1001.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.PT1001.Low_Limit.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.PT1001.High_Limit.Field.text()))

        self.AlarmButton.SubWindow.PT1002.updatebutton.clicked.connect(
            lambda: self.FPTTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1002.Label.text(),
                                       Act=self.AlarmButton.SubWindow.PT1002.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.PT1002.Low_Limit.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.PT1002.High_Limit.Field.text()))


    @QtCore.Slot()
    def LButtonClicked(self,pid):
        self.commands[pid]={"server":"BO","address": self.address[pid], "type":"valve","operation":"OPEN", "value":1}
        print(self.commands)
        print(pid,"L Button is clicked")

    @QtCore.Slot()
    def RButtonClicked(self, pid):
        self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "valve", "operation": "CLOSE",
                              "value": 1}
        print(self.commands)
        print(pid, "R Button is clicked")

    @QtCore.Slot()
    def HTLButtonClicked(self, pid):
        self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_power", "operation": "EN",
                              "value": 1}
        print(self.commands)
        print(pid, "L Button is clicked")

    @QtCore.Slot()
    def HTRButtonClicked(self, pid):
        self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_power", "operation": "DISEN",
                              "value": 1}
        print(self.commands)
        print(pid, "R Button is clicked")

    @QtCore.Slot()
    def HTSwitchSet(self, pid, value):
        if value in [0,1,2,3]:
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater", "operation": "SETMODE", "value": value}
        else:
            print("value should be 0, 1, 2, 3")
        print(self.commands)

    @QtCore.Slot()
    def HTHISet(self, pid, value):
        self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater",
                                  "operation": "HI_LIM", "value": value}

        print(self.commands)

    @QtCore.Slot()
    def HTLOSet(self, pid, value):
        self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater",
                              "operation": "LO_LIM", "value": value}

        print(self.commands)

    @QtCore.Slot()
    def HTSETPOINTSet(self, pid, value1, value2):
        if value1 == 0:
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater",
                              "operation": "SET0", "value": value2}
        elif value1 == 1:
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater",
                                  "operation": "SET1", "value": value2}
        elif value1 == 2:
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater",
                                  "operation": "SET2", "value": value2}
        elif value1 == 3:
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater",
                                  "operation": "SET3", "value": value2}
        else:
            print("MODE number should be in 0-3")

        print(self.commands)

    @QtCore.Slot()
    def HTRGroupButtonClicked(self, pid, setN):
        if setN == 0:
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_setmode",
                                  "operation": "SET0", "value": True}
        elif setN == 1:
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_setmode",
                                  "operation": "SET1", "value": True}
        elif setN == 2:
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_setmode",
                                  "operation": "SET2", "value": True}
        elif setN == 3:
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_setmode",
                                  "operation": "SET3", "value": True}
        else:
            print("not a valid address")

        print(self.commands)

    @QtCore.Slot()
    def HTRupdate(self,pid, modeN, setpoint, HI, LO):
        if modeN == 'MODE0':
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_para",
                              "operation": "SET0", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
        elif modeN == 'MODE1':
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_para",
                                  "operation": "SET1", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
        elif modeN == 'MODE2':
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_para",
                                  "operation": "SET2", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
        elif modeN == 'MODE3':
            self.commands[pid] = {"server": "BO", "address": self.address[pid], "type": "heater_para",
                                  "operation": "SET3", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
        else:
            print("MODE number should be in MODE0-3 and is a string")

        print(self.commands)

    @QtCore.Slot()
    def BOTTBoxUpdate(self,pid, Act,LowLimit, HighLimit):
        self.commands[pid]={"server": "BO", "address": self.address[pid], "type": "TT", "operation": {"Act":Act,
                                "LowLimit":LowLimit,"HighLimit":HighLimit}}
        print(pid,Act,LowLimit,HighLimit,"ARE OK?")

    @QtCore.Slot()
    def FPTTBoxUpdate(self,pid, Act,LowLimit, HighLimit):
        self.commands[pid]={"server": "FP", "address": self.address[pid], "type": "TT", "operation": {"Act":Act,
                                "LowLimit":LowLimit,"HighLimit":HighLimit}}
        print(pid,Act,LowLimit,HighLimit,"ARE OK?")


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
        return 0
        # if self.User == "Guest":
        #     Dialog = QtWidgets.QInputDialog()
        #     Dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
        #     Dialog.setLabelText("Please entre password")
        #     Dialog.setModal(True)
        #     Dialog.setWindowTitle("Login")
        #     Dialog.exec()
        #     if Dialog.result():
        #         if VerifyPW(ADMIN_PASSWORD, Dialog.textValue()):
        #             self.User = "Admin"
        #             self.LoginT.Button.setText("Admin")
        #             self.LoginP.Button.setText("Admin")
        #             self.LoginW.Button.setText("Admin")
        #
        #             self.ActivateControls(True)
        #
        #             self.UserTimer.start(ADMIN_TIMER)
        # else:
        #     self.User = "Guest"
        #     self.LoginT.Button.setText("Guest")
        #     self.LoginP.Button.setText("Guest")
        #     self.LoginW.Button.setText("Guest")
        #
        #     self.ActivateControls(False)

    @QtCore.Slot()
    def update_alarmwindow(self,dic):

        self.AlarmButton.CollectAlarm([self.AlarmButton.SubWindow.PT1000.Alarm,
                                          self.AlarmButton.SubWindow.PT1001.Alarm,
                                          self.AlarmButton.SubWindow.PT1002.Alarm])
        # print("Alarm Status=", self.AlarmButton.Button.Alarm)
        if self.AlarmButton.Button.Alarm:
            self.AlarmButton.ButtonAlarmSetSignal()
            self.AlarmButton.SubWindow.ReassignPTOrder()

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
        # self.SV3326.Activate(Activate)
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

    def closeEvent(self, event):
        self.CloseMessage = QtWidgets.QMessageBox()
        self.CloseMessage.setText("The program is to be closed")
        self.CloseMessage.setInformativeText("Do you want to save the settings?")
        self.CloseMessage.setStandardButtons(
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
        self.CloseMessage.setDefaultButton(QtWidgets.QMessageBox.Save)
        self.ret = self.CloseMessage.exec()
        if self.ret == QtWidgets.QMessageBox.Save:
            self.Save()
            event.accept()
        elif self.ret == QtWidgets.QMessageBox.Discard:
            event.accept()
        elif self.ret == QtWidgets.QMessageBox.Cancel:
            event.ignore()
        else:
            print("Some problems with closing windows...")
            pass

    def Save(self, directory=None, company="SBC", project="Slowcontrol"):
        # dir is the path storing the ini setting file
        if directory is None:
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2111/CheckBox",
                                   self.AlarmButton.SubWindow.TT2111.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2401/CheckBox",
                                   self.AlarmButton.SubWindow.TT2401.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2406/CheckBox",
                                   self.AlarmButton.SubWindow.TT2406.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2411/CheckBox",
                                   self.AlarmButton.SubWindow.TT2411.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2416/CheckBox",
                                   self.AlarmButton.SubWindow.TT2416.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2421/CheckBox",
                                   self.AlarmButton.SubWindow.TT2421.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2426/CheckBox",
                                   self.AlarmButton.SubWindow.TT2426.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2431/CheckBox",
                                   self.AlarmButton.SubWindow.TT2431.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2435/CheckBox",
                                   self.AlarmButton.SubWindow.TT2435.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2440/CheckBox",
                                   self.AlarmButton.SubWindow.TT2440.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT4330/CheckBox",
                                   self.AlarmButton.SubWindow.TT4330.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/CheckBox",
                                   self.AlarmButton.SubWindow.TT6220.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/CheckBox",
                                   self.AlarmButton.SubWindow.TT6220.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6221/CheckBox",
                                   self.AlarmButton.SubWindow.TT6221.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6222/CheckBox",
                                   self.AlarmButton.SubWindow.TT6222.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6223/CheckBox",
                                   self.AlarmButton.SubWindow.TT6223.AlarmMode.isChecked())
            # set PT value
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT1101/CheckBox",
                                   self.AlarmButton.SubWindow.PT1101.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2316/CheckBox",
                                   self.AlarmButton.SubWindow.PT2316.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2321/CheckBox",
                                   self.AlarmButton.SubWindow.PT2321.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2330/CheckBox",
                                   self.AlarmButton.SubWindow.PT2330.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2335/CheckBox",
                                   self.AlarmButton.SubWindow.PT2335.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3308/CheckBox",
                                   self.AlarmButton.SubWindow.PT3308.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3309/CheckBox",
                                   self.AlarmButton.SubWindow.PT3309.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3310/CheckBox",
                                   self.AlarmButton.SubWindow.PT3310.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3311/CheckBox",
                                   self.AlarmButton.SubWindow.PT3311.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3314/CheckBox",
                                   self.AlarmButton.SubWindow.PT3314.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3320/CheckBox",
                                   self.AlarmButton.SubWindow.PT3320.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3333/CheckBox",
                                   self.AlarmButton.SubWindow.PT3333.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4306/CheckBox",
                                   self.AlarmButton.SubWindow.PT4306.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4315/CheckBox",
                                   self.AlarmButton.SubWindow.PT4315.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4319/CheckBox",
                                   self.AlarmButton.SubWindow.PT4319.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4322/CheckBox",
                                   self.AlarmButton.SubWindow.PT4322.AlarmMode.isChecked())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4325/CheckBox",
                                   self.AlarmButton.SubWindow.PT4325.AlarmMode.isChecked())

            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2111/LowLimit",
                                   self.AlarmButton.SubWindow.TT2111.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2401/LowLimit",
                                   self.AlarmButton.SubWindow.TT2401.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2406/LowLimit",
                                   self.AlarmButton.SubWindow.TT2406.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2411/LowLimit",
                                   self.AlarmButton.SubWindow.TT2411.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2416/LowLimit",
                                   self.AlarmButton.SubWindow.TT2416.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2421/LowLimit",
                                   self.AlarmButton.SubWindow.TT2421.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2426/LowLimit",
                                   self.AlarmButton.SubWindow.TT2426.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2431/LowLimit",
                                   self.AlarmButton.SubWindow.TT2431.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2435/LowLimit",
                                   self.AlarmButton.SubWindow.TT2435.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2440/LowLimit",
                                   self.AlarmButton.SubWindow.TT2440.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT4330/LowLimit",
                                   self.AlarmButton.SubWindow.TT4330.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/LowLimit",
                                   self.AlarmButton.SubWindow.TT6220.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/LowLimit",
                                   self.AlarmButton.SubWindow.TT6220.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6221/LowLimit",
                                   self.AlarmButton.SubWindow.TT6221.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6222/LowLimit",
                                   self.AlarmButton.SubWindow.TT6222.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6223/LowLimit",
                                   self.AlarmButton.SubWindow.TT6223.Low_Limit.Field.text())
            # set PT value
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT1101/LowLimit",
                                   self.AlarmButton.SubWindow.PT1101.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2316/LowLimit",
                                   self.AlarmButton.SubWindow.PT2316.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2321/LowLimit",
                                   self.AlarmButton.SubWindow.PT2321.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2330/LowLimit",
                                   self.AlarmButton.SubWindow.PT2330.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2335/LowLimit",
                                   self.AlarmButton.SubWindow.PT2335.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3308/LowLimit",
                                   self.AlarmButton.SubWindow.PT3308.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3309/LowLimit",
                                   self.AlarmButton.SubWindow.PT3309.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3310/LowLimit",
                                   self.AlarmButton.SubWindow.PT3310.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3311/LowLimit",
                                   self.AlarmButton.SubWindow.PT3311.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3314/LowLimit",
                                   self.AlarmButton.SubWindow.PT3314.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3320/LowLimit",
                                   self.AlarmButton.SubWindow.PT3320.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3333/LowLimit",
                                   self.AlarmButton.SubWindow.PT3333.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4306/LowLimit",
                                   self.AlarmButton.SubWindow.PT4306.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4315/LowLimit",
                                   self.AlarmButton.SubWindow.PT4315.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4319/LowLimit",
                                   self.AlarmButton.SubWindow.PT4319.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4322/LowLimit",
                                   self.AlarmButton.SubWindow.PT4322.Low_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4325/LowLimit",
                                   self.AlarmButton.SubWindow.PT4325.Low_Limit.Field.text())

            # high limit

            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2111/HighLimit",
                                   self.AlarmButton.SubWindow.TT2111.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2401/HighLimit",
                                   self.AlarmButton.SubWindow.TT2401.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2406/HighLimit",
                                   self.AlarmButton.SubWindow.TT2406.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2411/HighLimit",
                                   self.AlarmButton.SubWindow.TT2411.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2416/HighLimit",
                                   self.AlarmButton.SubWindow.TT2416.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2421/HighLimit",
                                   self.AlarmButton.SubWindow.TT2421.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2426/HighLimit",
                                   self.AlarmButton.SubWindow.TT2426.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2431/HighLimit",
                                   self.AlarmButton.SubWindow.TT2431.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2435/HighLimit",
                                   self.AlarmButton.SubWindow.TT2435.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT2440/HighLimit",
                                   self.AlarmButton.SubWindow.TT2440.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT4330/HighLimit",
                                   self.AlarmButton.SubWindow.TT4330.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/HighLimit",
                                   self.AlarmButton.SubWindow.TT6220.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/HighLimit",
                                   self.AlarmButton.SubWindow.TT6220.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6221/HighLimit",
                                   self.AlarmButton.SubWindow.TT6221.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6222/HighLimit",
                                   self.AlarmButton.SubWindow.TT6222.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/TT6223/HighLimit",
                                   self.AlarmButton.SubWindow.TT6223.High_Limit.Field.text())
            # set PT value
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT1101/HighLimit",
                                   self.AlarmButton.SubWindow.PT1101.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2316/HighLimit",
                                   self.AlarmButton.SubWindow.PT2316.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2321/HighLimit",
                                   self.AlarmButton.SubWindow.PT2321.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2330/HighLimit",
                                   self.AlarmButton.SubWindow.PT2330.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT2335/HighLimit",
                                   self.AlarmButton.SubWindow.PT2335.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3308/HighLimit",
                                   self.AlarmButton.SubWindow.PT3308.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3309/HighLimit",
                                   self.AlarmButton.SubWindow.PT3309.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3310/HighLimit",
                                   self.AlarmButton.SubWindow.PT3310.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3311/HighLimit",
                                   self.AlarmButton.SubWindow.PT3311.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3314/HighLimit",
                                   self.AlarmButton.SubWindow.PT3314.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3320/HighLimit",
                                   self.AlarmButton.SubWindow.PT3320.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT3333/HighLimit",
                                   self.AlarmButton.SubWindow.PT3333.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4306/HighLimit",
                                   self.AlarmButton.SubWindow.PT4306.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4315/HighLimit",
                                   self.AlarmButton.SubWindow.PT4315.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4319/HighLimit",
                                   self.AlarmButton.SubWindow.PT4319.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4322/HighLimit",
                                   self.AlarmButton.SubWindow.PT4322.High_Limit.Field.text())
            self.settings.setValue("MainWindow/AlarmButton/SubWindow/PT4325/HighLimit",
                                   self.AlarmButton.SubWindow.PT4325.High_Limit.Field.text())

            print("saving data to Default path: $HOME/.config//SBC/SlowControl.ini")
        else:
            try:
                # modify the qtsetting default save settings. if the directory is inside a folder named sbc, then save
                # the file into the folder. If not, create a folder named sbc and save the file in it.
                (path_head, path_tail) = os.path.split(directory)
                if path_tail == company:
                    path = os.path.join(directory, project)
                else:
                    path = os.path.join(directory, company, project)
                print(path)
                self.customsettings = QtCore.QSettings(path, QtCore.QSettings.IniFormat)

                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2111/CheckBox",
                                             self.AlarmButton.SubWindow.TT2111.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2401/CheckBox",
                                             self.AlarmButton.SubWindow.TT2401.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2406/CheckBox",
                                             self.AlarmButton.SubWindow.TT2406.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2411/CheckBox",
                                             self.AlarmButton.SubWindow.TT2411.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2416/CheckBox",
                                             self.AlarmButton.SubWindow.TT2416.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2421/CheckBox",
                                             self.AlarmButton.SubWindow.TT2421.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2426/CheckBox",
                                             self.AlarmButton.SubWindow.TT2426.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2431/CheckBox",
                                             self.AlarmButton.SubWindow.TT2431.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2435/CheckBox",
                                             self.AlarmButton.SubWindow.TT2435.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2440/CheckBox",
                                             self.AlarmButton.SubWindow.TT2440.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT4330/CheckBox",
                                             self.AlarmButton.SubWindow.TT4330.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/CheckBox",
                                             self.AlarmButton.SubWindow.TT6220.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/CheckBox",
                                             self.AlarmButton.SubWindow.TT6220.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6221/CheckBox",
                                             self.AlarmButton.SubWindow.TT6221.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6222/CheckBox",
                                             self.AlarmButton.SubWindow.TT6222.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6223/CheckBox",
                                             self.AlarmButton.SubWindow.TT6223.AlarmMode.isChecked())
                # set PT value
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT1101/CheckBox",
                                             self.AlarmButton.SubWindow.PT1101.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2316/CheckBox",
                                             self.AlarmButton.SubWindow.PT2316.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2321/CheckBox",
                                             self.AlarmButton.SubWindow.PT2321.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2330/CheckBox",
                                             self.AlarmButton.SubWindow.PT2330.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2335/CheckBox",
                                             self.AlarmButton.SubWindow.PT2335.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3308/CheckBox",
                                             self.AlarmButton.SubWindow.PT3308.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3309/CheckBox",
                                             self.AlarmButton.SubWindow.PT3309.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3310/CheckBox",
                                             self.AlarmButton.SubWindow.PT3310.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3311/CheckBox",
                                             self.AlarmButton.SubWindow.PT3311.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3314/CheckBox",
                                             self.AlarmButton.SubWindow.PT3314.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3320/CheckBox",
                                             self.AlarmButton.SubWindow.PT3320.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3333/CheckBox",
                                             self.AlarmButton.SubWindow.PT3333.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4306/CheckBox",
                                             self.AlarmButton.SubWindow.PT4306.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4315/CheckBox",
                                             self.AlarmButton.SubWindow.PT4315.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4319/CheckBox",
                                             self.AlarmButton.SubWindow.PT4319.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4322/CheckBox",
                                             self.AlarmButton.SubWindow.PT4322.AlarmMode.isChecked())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4325/CheckBox",
                                             self.AlarmButton.SubWindow.PT4325.AlarmMode.isChecked())

                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2111/LowLimit",
                                             self.AlarmButton.SubWindow.TT2111.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2401/LowLimit",
                                             self.AlarmButton.SubWindow.TT2401.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2406/LowLimit",
                                             self.AlarmButton.SubWindow.TT2406.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2411/LowLimit",
                                             self.AlarmButton.SubWindow.TT2411.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2416/LowLimit",
                                             self.AlarmButton.SubWindow.TT2416.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2421/LowLimit",
                                             self.AlarmButton.SubWindow.TT2421.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2426/LowLimit",
                                             self.AlarmButton.SubWindow.TT2426.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2431/LowLimit",
                                             self.AlarmButton.SubWindow.TT2431.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2435/LowLimit",
                                             self.AlarmButton.SubWindow.TT2435.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2440/LowLimit",
                                             self.AlarmButton.SubWindow.TT2440.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT4330/LowLimit",
                                             self.AlarmButton.SubWindow.TT4330.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/LowLimit",
                                             self.AlarmButton.SubWindow.TT6220.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/LowLimit",
                                             self.AlarmButton.SubWindow.TT6220.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6221/LowLimit",
                                             self.AlarmButton.SubWindow.TT6221.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6222/LowLimit",
                                             self.AlarmButton.SubWindow.TT6222.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6223/LowLimit",
                                             self.AlarmButton.SubWindow.TT6223.Low_Limit.Field.text())
                # set PT value
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT1101/LowLimit",
                                             self.AlarmButton.SubWindow.PT1101.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2316/LowLimit",
                                             self.AlarmButton.SubWindow.PT2316.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2321/LowLimit",
                                             self.AlarmButton.SubWindow.PT2321.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2330/LowLimit",
                                             self.AlarmButton.SubWindow.PT2330.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2335/LowLimit",
                                             self.AlarmButton.SubWindow.PT2335.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3308/LowLimit",
                                             self.AlarmButton.SubWindow.PT3308.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3309/LowLimit",
                                             self.AlarmButton.SubWindow.PT3309.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3310/LowLimit",
                                             self.AlarmButton.SubWindow.PT3310.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3311/LowLimit",
                                             self.AlarmButton.SubWindow.PT3311.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3314/LowLimit",
                                             self.AlarmButton.SubWindow.PT3314.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3320/LowLimit",
                                             self.AlarmButton.SubWindow.PT3320.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3333/LowLimit",
                                             self.AlarmButton.SubWindow.PT3333.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4306/LowLimit",
                                             self.AlarmButton.SubWindow.PT4306.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4315/LowLimit",
                                             self.AlarmButton.SubWindow.PT4315.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4319/LowLimit",
                                             self.AlarmButton.SubWindow.PT4319.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4322/LowLimit",
                                             self.AlarmButton.SubWindow.PT4322.Low_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4325/LowLimit",
                                             self.AlarmButton.SubWindow.PT4325.Low_Limit.Field.text())

                # high limit

                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2111/HighLimit",
                                             self.AlarmButton.SubWindow.TT2111.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2401/HighLimit",
                                             self.AlarmButton.SubWindow.TT2401.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2406/HighLimit",
                                             self.AlarmButton.SubWindow.TT2406.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2411/HighLimit",
                                             self.AlarmButton.SubWindow.TT2411.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2416/HighLimit",
                                             self.AlarmButton.SubWindow.TT2416.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2421/HighLimit",
                                             self.AlarmButton.SubWindow.TT2421.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2426/HighLimit",
                                             self.AlarmButton.SubWindow.TT2426.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2431/HighLimit",
                                             self.AlarmButton.SubWindow.TT2431.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2435/HighLimit",
                                             self.AlarmButton.SubWindow.TT2435.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT2440/HighLimit",
                                             self.AlarmButton.SubWindow.TT2440.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT4330/HighLimit",
                                             self.AlarmButton.SubWindow.TT4330.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/HighLimit",
                                             self.AlarmButton.SubWindow.TT6220.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6220/HighLimit",
                                             self.AlarmButton.SubWindow.TT6220.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6221/HighLimit",
                                             self.AlarmButton.SubWindow.TT6221.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6222/HighLimit",
                                             self.AlarmButton.SubWindow.TT6222.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/TT6223/HighLimit",
                                             self.AlarmButton.SubWindow.TT6223.High_Limit.Field.text())
                # set PT value
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT1101/HighLimit",
                                             self.AlarmButton.SubWindow.PT1101.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2316/HighLimit",
                                             self.AlarmButton.SubWindow.PT2316.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2321/HighLimit",
                                             self.AlarmButton.SubWindow.PT2321.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2330/HighLimit",
                                             self.AlarmButton.SubWindow.PT2330.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT2335/HighLimit",
                                             self.AlarmButton.SubWindow.PT2335.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3308/HighLimit",
                                             self.AlarmButton.SubWindow.PT3308.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3309/HighLimit",
                                             self.AlarmButton.SubWindow.PT3309.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3310/HighLimit",
                                             self.AlarmButton.SubWindow.PT3310.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3311/HighLimit",
                                             self.AlarmButton.SubWindow.PT3311.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3314/HighLimit",
                                             self.AlarmButton.SubWindow.PT3314.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3320/HighLimit",
                                             self.AlarmButton.SubWindow.PT3320.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT3333/HighLimit",
                                             self.AlarmButton.SubWindow.PT3333.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4306/HighLimit",
                                             self.AlarmButton.SubWindow.PT4306.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4315/HighLimit",
                                             self.AlarmButton.SubWindow.PT4315.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4319/HighLimit",
                                             self.AlarmButton.SubWindow.PT4319.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4322/HighLimit",
                                             self.AlarmButton.SubWindow.PT4322.High_Limit.Field.text())
                self.customsettings.setValue("MainWindow/AlarmButton/SubWindow/PT4325/HighLimit",
                                             self.AlarmButton.SubWindow.PT4325.High_Limit.Field.text())
                print("saving data to ", path)
            except:
                print("Failed to custom save the settings.")

    def Recover(self, address="$HOME/.config//SBC/SlowControl.ini"):
        # address is the ini file 's directory you want to recover

        try:
            # default recover. If no other address is claimed, then recover settings from default directory
            if address == "$HOME/.config//SBC/SlowControl.ini":
                self.RecoverChecked(self.AlarmButton.SubWindow.TT4330,
                                    "MainWindow/AlarmButton/SubWindow/TT4330/CheckBox")
                self.RecoverChecked(self.AlarmButton.SubWindow.PT4306,
                                    "MainWindow/AlarmButton/SubWindow/PT4306/CheckBox")
                self.RecoverChecked(self.AlarmButton.SubWindow.PT4315,
                                    "MainWindow/AlarmButton/SubWindow/PT4315/CheckBox")
                self.RecoverChecked(self.AlarmButton.SubWindow.PT4319,
                                    "MainWindow/AlarmButton/SubWindow/PT4319/CheckBox")
                self.RecoverChecked(self.AlarmButton.SubWindow.PT4322,
                                    "MainWindow/AlarmButton/SubWindow/PT4322/CheckBox")
                self.RecoverChecked(self.AlarmButton.SubWindow.PT4325,
                                    "MainWindow/AlarmButton/SubWindow/PT4325/CheckBox")

                self.AlarmButton.SubWindow.TT4330.Low_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/TT4330/LowLimit"))
                self.AlarmButton.SubWindow.TT4330.Low_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4306.Low_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4306/LowLimit"))
                self.AlarmButton.SubWindow.PT4306.Low_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4315.Low_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4315/LowLimit"))
                self.AlarmButton.SubWindow.PT4315.Low_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4319.Low_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4319/LowLimit"))
                self.AlarmButton.SubWindow.PT4319.Low_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4322.Low_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4322/LowLimit"))
                self.AlarmButton.SubWindow.PT4322.Low_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4325.Low_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4325/LowLimit"))
                self.AlarmButton.SubWindow.PT4325.Low_Limit.UpdateValue()

                self.AlarmButton.SubWindow.TT4330.High_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/TT4330/HighLimit"))
                self.AlarmButton.SubWindow.TT4330.High_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4306.High_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4306/HighLimit"))
                self.AlarmButton.SubWindow.PT4306.High_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4315.High_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4315/HighLimit"))
                self.AlarmButton.SubWindow.PT4315.High_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4319.High_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4319/HighLimit"))
                self.AlarmButton.SubWindow.PT4319.High_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4322.High_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4322/HighLimit"))
                self.AlarmButton.SubWindow.PT4322.High_Limit.UpdateValue()
                self.AlarmButton.SubWindow.PT4325.High_Limit.Field.setText(self.settings.value(
                    "MainWindow/AlarmButton/SubWindow/PT4325/HighLimit"))
                self.AlarmButton.SubWindow.PT4325.High_Limit.UpdateValue()
            else:
                try:
                    # else, recover from the claimed directory
                    # address should be surfix with ini. Example:$HOME/.config//SBC/SlowControl.ini
                    directory = QtCore.QSettings(str(address), QtCore.QSettings.IniFormat)
                    print("Recovering from " + str(address))
                    self.RecoverChecked(GUIid=self.AlarmButton.SubWindow.TT4330,
                                        subdir="MainWindow/AlarmButton/SubWindow/TT4330/CheckBox",
                                        loadedsettings=directory)
                    self.RecoverChecked(GUIid=self.AlarmButton.SubWindow.PT4306,
                                        subdir="MainWindow/AlarmButton/SubWindow/PT4306/CheckBox",
                                        loadedsettings=directory)
                    self.RecoverChecked(GUIid=self.AlarmButton.SubWindow.PT4315,
                                        subdir="MainWindow/AlarmButton/SubWindow/PT4315/CheckBox",
                                        loadedsettings=directory)
                    self.RecoverChecked(GUIid=self.AlarmButton.SubWindow.PT4319,
                                        subdir="MainWindow/AlarmButton/SubWindow/PT4319/CheckBox",
                                        loadedsettings=directory)
                    self.RecoverChecked(GUIid=self.AlarmButton.SubWindow.PT4322,
                                        subdir="MainWindow/AlarmButton/SubWindow/PT4322/CheckBox",
                                        loadedsettings=directory)
                    self.RecoverChecked(GUIid=self.AlarmButton.SubWindow.PT4325,
                                        subdir="MainWindow/AlarmButton/SubWindow/PT4325/CheckBox",
                                        loadedsettings=directory)

                    self.AlarmButton.SubWindow.TT4330.Low_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/TT4330/LowLimit"))
                    self.AlarmButton.SubWindow.TT4330.Low_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4306.Low_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4306/LowLimit"))
                    self.AlarmButton.SubWindow.PT4306.Low_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4315.Low_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4315/LowLimit"))
                    self.AlarmButton.SubWindow.PT4315.Low_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4319.Low_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4319/LowLimit"))
                    self.AlarmButton.SubWindow.PT4319.Low_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4322.Low_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4322/LowLimit"))
                    self.AlarmButton.SubWindow.PT4322.Low_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4325.Low_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4325/LowLimit"))
                    self.AlarmButton.SubWindow.PT4325.Low_Limit.UpdateValue()

                    self.AlarmButton.SubWindow.TT4330.High_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/TT4330/HighLimit"))
                    self.AlarmButton.SubWindow.TT4330.High_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4306.High_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4306/HighLimit"))
                    self.AlarmButton.SubWindow.PT4306.High_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4315.High_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4315/HighLimit"))
                    self.AlarmButton.SubWindow.PT4315.High_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4319.High_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4319/HighLimit"))
                    self.AlarmButton.SubWindow.PT4319.High_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4322.High_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4322/HighLimit"))
                    self.AlarmButton.SubWindow.PT4322.High_Limit.UpdateValue()
                    self.AlarmButton.SubWindow.PT4325.High_Limit.Field.setText(directory.value(
                        "MainWindow/AlarmButton/SubWindow/PT4325/HighLimit"))
                    self.AlarmButton.SubWindow.PT4325.High_Limit.UpdateValue()

                except:
                    print("Wrong Path to recover")
        except:
            print("1st time run the code in this environment. "
                  "Nothing to recover the settings. Please save the configuration to a ini file")
            pass

    def RecoverChecked(self, GUIid, subdir, loadedsettings=None):
        # add a function because you can not directly set check status to checkbox
        # GUIid should be form of "self.AlarmButton.SubWindow.PT4315", is the variable name in the Main window
        # subdir like ""MainWindow/AlarmButton/SubWindow/PT4306/CheckBox"", is the path file stored in the ini file
        # loadedsettings is the Qtsettings file the program is to load
        if loadedsettings is None:
            # It is weired here, when I save the data and close the program, the setting value
            # in the address is string true
            # while if you maintain the program, the setting value in the address is bool True
            if self.settings.value(subdir) == "true" or self.settings.value(subdir) == True:
                GUIid.AlarmMode.setChecked(True)
            elif self.settings.value(subdir) == "false" or self.settings.value(subdir) == False:
                GUIid.AlarmMode.setChecked(False)
            else:
                print("Checkbox's value is neither true nor false")
        else:
            try:
                if loadedsettings.value(subdir) == "True" or loadedsettings.value(subdir) == True:
                    GUIid.AlarmMode.setChecked(True)
                elif self.settings.value(subdir) == "false" or loadedsettings.value(subdir) == False:
                    GUIid.AlarmMode.setChecked(False)
                else:
                    print("Checkbox's value is neither true nor false")
            except:
                print("Failed to load the status of checkboxs")


# Defines a reusable layout containing widgets
class RegionPID(QtWidgets.QWidget):
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

        self.Mode = Toggle(self)
        self.Mode.Label.setText("Mode")
        self.Mode.SetToggleStateNames("Auto", "Manual")
        self.HL.addWidget(self.Mode)

        self.Setpoint = Control(self)
        self.Setpoint.Label.setText("Setpoint")
        self.HL.addWidget(self.Setpoint)

        self.P = Control(self)
        self.P.Label.setText("P")
        self.P.Unit = ""
        self.P.Max = 20.
        self.P.Min = 0.
        self.P.Step = 0.1
        self.P.Decimals = 1
        self.HL.addWidget(self.P)

        self.I = Control(self)
        self.I.Label.setText("I")
        self.I.Unit = ""
        self.I.Max = 20.
        self.I.Min = 0.
        self.I.Step = 0.1
        self.I.Decimals = 1
        self.HL.addWidget(self.I)

        self.D = Control(self)
        self.D.Label.setText("D")
        self.D.Unit = ""
        self.D.Max = 20.
        self.D.Min = 0.
        self.D.Step = 0.1
        self.D.Decimals = 1
        self.HL.addWidget(self.D)



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

# Class to read PLC value every 2 sec
class UpdatePLC(QtCore.QObject):
    def __init__(self, PLC, parent=None):
        super().__init__(parent)
        self.PLC = PLC

        self.Running = False

    @QtCore.Slot()
    def run(self):
        self.Running = True

        while self.Running:
            print("PLC updating", datetime.datetime.now())
            self.PLC.ReadAll()
            time.sleep(1)

    @QtCore.Slot()
    def stop(self):
        self.Running = False


class UpdateClient(QtCore.QObject):
    def __init__(self, MW, parent=None):
        super().__init__(parent)
        self.MW = MW
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")
        self.Running=False
        self.period=1
        print("client is connecting to the ZMQ server")

        self.TT_AD1_dic_ini = copy.deepcopy(sec.TT_AD1_DIC)
        self.TT_AD2_dic_ini = copy.deepcopy(sec.TT_AD2_DIC)
        self.PT_dic_ini = copy.deepcopy(sec.PT_DIC)
        self.LEFT_REAL_ini = copy.deepcopy(sec.LEFT_REAL_DIC)
        self.TT_AD1_LowLimit_ini = copy.deepcopy(sec.TT_AD1_LOWLIMIT)
        self.TT_AD1_HighLimit_ini = copy.deepcopy(sec.TT_AD1_HIGHLIMIT)
        self.TT_AD2_LowLimit_ini = copy.deepcopy(sec.TT_AD2_LOWLIMIT)
        self.TT_AD2_HighLimit_ini = copy.deepcopy(sec.TT_AD2_HIGHLIMIT)
        self.PT_LowLimit_ini = copy.deepcopy(sec.PT_LOWLIMIT)
        self.PT_HighLimit_ini = copy.deepcopy(sec.PT_HIGHLIMIT)
        self.LEFT_REAL_LowLimit_ini = copy.deepcopy(sec.LEFT_REAL_LOWLIMIT)
        self.LEFT_REAL_HighLimit_ini = copy.deepcopy(sec.LEFT_REAL_HIGHLIMIT)
        self.TT_AD1_Alarm_ini = copy.deepcopy(sec.TT_AD1_ALARM)
        self.TT_AD2_Alarm_ini = copy.deepcopy(sec.TT_AD2_ALARM)
        self.TT_AD1_Activated_ini = copy.deepcopy(sec.TT_AD1_ACTIVATED)
        self.TT_AD2_Activated_ini = copy.deepcopy(sec.TT_AD2_ACTIVATED)
        self.PT_Activated_ini = copy.deepcopy(sec.PT_ACTIVATED)
        self.PT_Alarm_ini = copy.deepcopy(sec.PT_ALARM)
        self.LEFT_REAL_Activated_ini = copy.deepcopy(sec.LEFT_REAL_ACTIVATED)
        self.LEFT_REAL_Alarm_ini = copy.deepcopy(sec.LEFT_REAL_ALARM)
        self.MainAlarm_ini = copy.deepcopy(sec.MAINALARM)
        self.MAN_SET = copy.deepcopy(sec.MAN_SET)
        self.Valve_OUT_ini = copy.deepcopy(sec.VALVE_OUT)
        self.Valve_MAN_ini = copy.deepcopy(sec.VALVE_MAN)
        self.Valve_INTLKD_ini = copy.deepcopy(sec.VALVE_INTLKD)
        self.Valve_ERR_ini = copy.deepcopy(sec.VALVE_ERR)
        self.Valve_Busy_ini = copy.deepcopy(sec.VALVE_BUSY)
        self.Switch_OUT_ini = copy.deepcopy(sec.SWITCH_OUT)
        self.Switch_MAN_ini = copy.deepcopy(sec.SWITCH_MAN)
        self.Switch_INTLKD_ini = copy.deepcopy(sec.SWITCH_INTLKD)
        self.Switch_ERR_ini = copy.deepcopy(sec.SWITCH_ERR)
        self.Din_dic_ini = copy.deepcopy(sec.DIN_DIC)
        self.Din_HighLimit_ini = copy.deepcopy(sec.DIN_HIGHLIMIT)
        self.Din_LowLimit_ini = copy.deepcopy(sec.DIN_LOWLIMIT)
        self.Din_Activated_ini = copy.deepcopy(sec.DIN_ACTIVATED)
        self.Din_Alarm_ini = copy.deepcopy(sec.DIN_ALARM)

        self.LOOPPID_MODE0_ini = copy.deepcopy(sec.LOOPPID_MODE0)
        self.LOOPPID_MODE1_ini = copy.deepcopy(sec.LOOPPID_MODE1)
        self.LOOPPID_MODE2_ini = copy.deepcopy(sec.LOOPPID_MODE2)
        self.LOOPPID_MODE3_ini = copy.deepcopy(sec.LOOPPID_MODE3)
        self.LOOPPID_INTLKD_ini = copy.deepcopy(sec.LOOPPID_INTLKD)
        self.LOOPPID_MAN_ini = copy.deepcopy(sec.LOOPPID_MAN)
        self.LOOPPID_ERR_ini = copy.deepcopy(sec.LOOPPID_ERR)
        self.LOOPPID_SATHI_ini = copy.deepcopy(sec.LOOPPID_SATHI)
        self.LOOPPID_SATLO_ini = copy.deepcopy(sec.LOOPPID_SATLO)
        self.LOOPPID_EN_ini = copy.deepcopy(sec.LOOPPID_EN)
        self.LOOPPID_OUT_ini = copy.deepcopy(sec.LOOPPID_OUT)
        self.LOOPPID_IN_ini = copy.deepcopy(sec.LOOPPID_IN)
        self.LOOPPID_HI_LIM_ini = copy.deepcopy(sec.LOOPPID_HI_LIM)
        self.LOOPPID_LO_LIM_ini = copy.deepcopy(sec.LOOPPID_LO_LIM)
        self.LOOPPID_SET0_ini = copy.deepcopy(sec.LOOPPID_SET0)
        self.LOOPPID_SET1_ini = copy.deepcopy(sec.LOOPPID_SET1)
        self.LOOPPID_SET2_ini = copy.deepcopy(sec.LOOPPID_SET2)
        self.LOOPPID_SET3_ini = copy.deepcopy(sec.LOOPPID_SET3)
        self.LOOPPID_Busy_ini = copy.deepcopy(sec.LOOPPID_BUSY)
        self.LOOPPID_Alarm_ini = copy.deepcopy(sec.LOOPPID_ALARM)
        self.LOOPPID_Activated_ini = copy.deepcopy(sec.LOOPPID_ACTIVATED)
        self.LOOPPID_Alarm_HighLimit_ini = copy.deepcopy(sec.LOOPPID_ALARM_HI_LIM)
        self.LOOPPID_Alarm_LowLimit_ini = copy.deepcopy(sec.LOOPPID_ALARM_LO_LIM)

        self.LOOP2PT_MODE0_ini = copy.deepcopy(sec.LOOP2PT_MODE0)
        self.LOOP2PT_MODE1_ini = copy.deepcopy(sec.LOOP2PT_MODE1)
        self.LOOP2PT_MODE2_ini = copy.deepcopy(sec.LOOP2PT_MODE2)
        self.LOOP2PT_MODE3_ini = copy.deepcopy(sec.LOOP2PT_MODE3)
        self.LOOP2PT_INTLKD_ini = copy.deepcopy(sec.LOOP2PT_INTLKD)
        self.LOOP2PT_MAN_ini = copy.deepcopy(sec.LOOP2PT_MAN)
        self.LOOP2PT_ERR_ini = copy.deepcopy(sec.LOOP2PT_ERR)
        self.LOOP2PT_OUT_ini = copy.deepcopy(sec.LOOP2PT_OUT)
        self.LOOP2PT_SET1_ini = copy.deepcopy(sec.LOOP2PT_SET1)
        self.LOOP2PT_SET2_ini = copy.deepcopy(sec.LOOP2PT_SET2)
        self.LOOP2PT_SET3_ini = copy.deepcopy(sec.LOOP2PT_SET3)
        self.LOOP2PT_Busy_ini = copy.deepcopy(sec.LOOP2PT_BUSY)

        self.Procedure_running_ini = copy.deepcopy(sec.PROCEDURE_RUNNING)
        self.Procedure_INTLKD_ini = copy.deepcopy(sec.PROCEDURE_INTLKD)
        self.Procedure_EXIT_ini = copy.deepcopy(sec.PROCEDURE_EXIT)

        self.INTLK_D_ADDRESS_ini = copy.deepcopy(sec.INTLK_D_ADDRESS)
        self.INTLK_D_DIC_ini = copy.deepcopy(sec.INTLK_D_DIC)
        self.INTLK_D_EN_ini = copy.deepcopy(sec.INTLK_D_EN)
        self.INTLK_D_COND_ini = copy.deepcopy(sec.INTLK_D_COND)
        self.INTLK_D_Busy_ini = copy.deepcopy(sec.INTLK_D_BUSY)
        self.INTLK_A_ADDRESS_ini = copy.deepcopy(sec.INTLK_A_ADDRESS)
        self.INTLK_A_DIC_ini = copy.deepcopy(sec.INTLK_A_DIC)
        self.INTLK_A_EN_ini = copy.deepcopy(sec.INTLK_A_EN)
        self.INTLK_A_COND_ini = copy.deepcopy(sec.INTLK_A_COND)
        self.INTLK_A_SET_ini = copy.deepcopy(sec.INTLK_A_SET)
        self.INTLK_A_Busy_ini = copy.deepcopy(sec.INTLK_A_BUSY)

        self.FLAG_ADDRESS_ini = copy.deepcopy(sec.FLAG_ADDRESS)
        self.FLAG_DIC_ini = copy.deepcopy(sec.FLAG_DIC)
        self.FLAG_INTLKD_ini = copy.deepcopy(sec.FLAG_INTLKD)
        self.FLAG_Busy_ini = copy.deepcopy(sec.FLAG_BUSY)

        self.FF_DIC_ini = copy.deepcopy(sec.FF_DIC)
        self.PARAM_F_DIC_ini = copy.deepcopy(sec.PARAM_F_DIC)
        self.PARAM_I_DIC_ini = copy.deepcopy(sec.PARAM_I_DIC)
        self.PARAM_B_DIC_ini = copy.deepcopy(sec.PARAM_B_DIC)
        self.PARAM_T_DIC_ini = copy.deepcopy(sec.PARAM_T_DIC)
        self.TIME_DIC_ini = copy.deepcopy(sec.TIME_DIC)

        self.Ini_Check_ini = sec.INI_CHECK

        self.data_dic = {"data": {"TT": {
            "AD1": {"value": self.TT_AD1_dic_ini, "high": self.TT_AD1_HighLimit_ini, "low": self.TT_AD1_LowLimit_ini},
            "AD2": {"value": self.TT_AD2_dic_ini, "high": self.TT_AD2_HighLimit_ini, "low": self.TT_AD2_LowLimit_ini}},
                                  "PT": {"value": self.PT_dic_ini, "high": self.PT_HighLimit_ini,
                                         "low": self.PT_LowLimit_ini},
                                  "LEFT_REAL": {"value": self.LEFT_REAL_ini, "high": self.LEFT_REAL_HighLimit_ini,
                                                "low": self.LEFT_REAL_LowLimit_ini},
                                  "Valve": {"OUT": self.Valve_OUT_ini,
                                            "INTLKD": self.Valve_INTLKD_ini,
                                            "MAN": self.Valve_MAN_ini,
                                            "ERR": self.Valve_ERR_ini,
                                            "Busy": self.Valve_Busy_ini},
                                  "Switch": {"OUT": self.Switch_OUT_ini,
                                             "INTLKD": self.Switch_INTLKD_ini,
                                             "MAN": self.Switch_MAN_ini,
                                             "ERR": self.Switch_ERR_ini},
                                  "Din": {'value': self.Din_dic_ini, "high": self.Din_HighLimit_ini,
                                          "low": self.Din_LowLimit_ini},
                                  "LOOPPID": {"MODE0": self.LOOPPID_MODE0_ini,
                                              "MODE1": self.LOOPPID_MODE1_ini,
                                              "MODE2": self.LOOPPID_MODE2_ini,
                                              "MODE3": self.LOOPPID_MODE3_ini,
                                              "INTLKD": self.LOOPPID_INTLKD_ini,
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
                                              "Busy": self.LOOPPID_Busy_ini,
                                              "Alarm": self.LOOPPID_Alarm_ini,
                                              "Alarm_HighLimit": self.LOOPPID_Alarm_HighLimit_ini,
                                              "Alarm_LowLimit": self.LOOPPID_Alarm_LowLimit_ini},
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
                                              "Busy": self.LOOP2PT_Busy_ini},
                                  "INTLK_D": {"value": self.INTLK_D_DIC_ini,
                                              "EN": self.INTLK_D_EN_ini,
                                              "COND": self.INTLK_D_COND_ini,
                                              "Busy": self.INTLK_D_Busy_ini},
                                  "INTLK_A": {"value": self.INTLK_A_DIC_ini,
                                              "EN": self.INTLK_A_EN_ini,
                                              "COND": self.INTLK_A_COND_ini,
                                              "SET": self.INTLK_A_SET_ini,
                                              "Busy": self.INTLK_A_Busy_ini},
                                  "FLAG": {"value": self.FLAG_DIC_ini,
                                           "INTLKD": self.FLAG_INTLKD_ini,
                                           "Busy": self.FLAG_Busy_ini},
                                  "Procedure": {"Running": self.Procedure_running_ini,
                                                "INTLKD": self.Procedure_INTLKD_ini, "EXIT": self.Procedure_EXIT_ini},
                                  "FF": self.FF_DIC_ini,
                                  "PARA_I": self.PARAM_I_DIC_ini,
                                  "PARA_F": self.PARAM_F_DIC_ini,
                                  "PARA_B": self.PARAM_B_DIC_ini,
                                  "PARA_T": self.PARAM_T_DIC_ini,
                                  "TIME": self.TIME_DIC_ini},
                         "Alarm": {"TT": {"AD1": self.TT_AD1_Alarm_ini,
                                          "AD2": self.TT_AD2_Alarm_ini
                                          },
                                   "PT": self.PT_Alarm_ini,
                                   "LEFT_REAL": self.LEFT_REAL_Alarm_ini,
                                   "Din": self.Din_Alarm_ini,
                                   "LOOPPID": self.LOOPPID_Alarm_ini},
                         "Active": {"TT": {"AD1": self.TT_AD1_Activated_ini,
                                           "AD2": self.TT_AD2_Activated_ini},
                                    "PT": self.PT_Activated_ini,
                                    "LEFT_REAL": self.LEFT_REAL_Activated_ini,
                                    "Din": self.Din_Activated_ini,
                                    "LOOPPID": self.LOOPPID_Activated_ini,
                                    "INI_CHECK": self.Ini_Check_ini},
                         "MainAlarm": self.MainAlarm_ini
                         }
        self.commands_package= pickle.dumps({})
    @QtCore.Slot()
    def run(self):
        self.Running = True
        while self.Running:

            print(f"Sending request...")

            #  Send reply back to client
            # self.socket.send(b"Hello")
            self.commands()
            # print(self.receive_dic)
            message = pickle.loads(self.socket.recv())


            # print(f"Received reply [ {message} ]")
            self.update_data(message)
            time.sleep(self.period)

    @QtCore.Slot()
    def stop(self):
        self.Running = False
    def update_data(self,message):
        #message mush be a dictionary
        self.receive_dic = message
    def commands(self):
        print("Commands are here",datetime.datetime.now())
        print("commands",self.MW.commands)
        self.commands_package= pickle.dumps(self.MW.commands)
        print("commands len",len(self.MW.commands))
        if len(self.MW.commands) != 0:
            self.socket.send(self.commands_package)
            self.MW.commands={}
        else:
            self.socket.send(pickle.dumps({}))


# Class to update display with PLC values every time PLC values ave been updated
# All commented lines are modbus variables not yet implemented on the PLCs
class UpdateDisplay(QtCore.QObject):
    display_update = QtCore.Signal(dict)
    def __init__(self, MW, Client,parent=None):
        super().__init__(parent)

        self.MW = MW
        self.Client = Client
        self.Running = False

        self.display_update.connect(self.MW.update_alarmwindow)
        self.button_refreshing_count = 0
        self.count = 0

    @QtCore.Slot()
    def run(self):
        try:
            self.Running = True
            while self.Running:
                print("Display updating", datetime.datetime.now())

                # if self.MW.PLC.NewData_Display:

                dic=self.Client.receive_dic
                # print(dic)
                # print(type(dic))

                self.MW.AlarmButton.SubWindow.PT1000.UpdateAlarm(self.Client.receive_dic["Alarm"]["PT"]["PT1000"])
                self.MW.AlarmButton.SubWindow.PT1000.Indicator.SetValue(
                    self.Client.receive_dic["data"]["PT"]["PT1000"])

                self.MW.AlarmButton.SubWindow.PT1001.UpdateAlarm(self.Client.receive_dic["Alarm"]["PT"]["PT1001"])
                self.MW.AlarmButton.SubWindow.PT1001.Indicator.SetValue(
                    self.Client.receive_dic["data"]["PT"]["PT1001"])

                self.MW.AlarmButton.SubWindow.PT1002.UpdateAlarm(self.Client.receive_dic["Alarm"]["PT"]["PT1002"])
                self.MW.AlarmButton.SubWindow.PT1002.Indicator.SetValue(
                    self.Client.receive_dic["data"]["PT"]["PT1002"])

                self.display_update.emit(dic)

                self.MW.PV1001.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV1001"])
                self.MW.PV1002.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV1002"])
                self.MW.PV1003.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV1003"])
                self.MW.PV1004.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV1004"])
                self.MW.PV1005.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV1005"])
                self.MW.PV1006.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV1006"])
                self.MW.PV1007.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV1007"])

                self.MW.PV001.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV001"])
                self.MW.PV002.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV002"])
                self.MW.PV003.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV003"])
                self.MW.PV004.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV004"])
                self.MW.PV005.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV005"])
                self.MW.PV006.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV006"])
                self.MW.PV007.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV007"])
                self.MW.PV008.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV008"])
                self.MW.PV009.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV009"])
                self.MW.PV010.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV010"])
                self.MW.PV011.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV011"])
                self.MW.PV012.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV012"])
                self.MW.PV013.Set.Activate(self.Client.receive_dic["data"]["Valve"]["MAN"]["PV013"])



                # refreshing the valve status from PLC every 30s
                if self.count > 0:
                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1001"]:
                        self.MW.PV1001.Set.ButtonLClicked()
                    else:
                        self.MW.PV1001.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1002"]:
                        self.MW.PV1002.Set.ButtonLClicked()
                    else:
                        self.MW.PV1002.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1003"]:
                        self.MW.PV1003.Set.ButtonLClicked()
                    else:
                        self.MW.PV1003.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1004"]:
                        self.MW.PV1004.Set.ButtonLClicked()
                    else:
                        self.MW.PV1004.Set.ButtonRClicked()


                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1005"]:
                        self.MW.PV1005.Set.ButtonLClicked()
                    else:
                        self.MW.PV1005.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1006"]:
                        self.MW.PV1006.Set.ButtonLClicked()
                    else:
                        self.MW.PV1006.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV1007.Set.ButtonLClicked()
                    else:
                        self.MW.PV1007.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV001.Set.ButtonLClicked()
                    else:
                        self.MW.PV001.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV002.Set.ButtonLClicked()
                    else:
                        self.MW.PV002.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV003.Set.ButtonLClicked()
                    else:
                        self.MW.PV1003.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV004.Set.ButtonLClicked()
                    else:
                        self.MW.PV004.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV005.Set.ButtonLClicked()
                    else:
                        self.MW.PV005.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV006.Set.ButtonLClicked()
                    else:
                        self.MW.PV006.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV007.Set.ButtonLClicked()
                    else:
                        self.MW.PV007.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV008.Set.ButtonLClicked()
                    else:
                        self.MW.PV008.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV009.Set.ButtonLClicked()
                    else:
                        self.MW.PV009.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV010.Set.ButtonLClicked()
                    else:
                        self.MW.PV010.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV010.Set.ButtonLClicked()
                    else:
                        self.MW.PV010.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV011.Set.ButtonLClicked()
                    else:
                        self.MW.PV011.Set.ButtonRClicked()

                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV012.Set.ButtonLClicked()
                    else:
                        self.MW.PV012.Set.ButtonRClicked()
                    
                    if self.Client.receive_dic["data"]["Valve"]["OUT"]["PV1007"]:
                        self.MW.PV013.Set.ButtonLClicked()
                    else:
                        self.MW.PV013.Set.ButtonRClicked()

            

                    self.count = 0
                self.count += 1

                self.MW.PT1000.SetValue(self.Client.receive_dic["data"]["PT"]["PT1000"])
                self.MW.PT1001.SetValue(self.Client.receive_dic["data"]["PT"]["PT1001"])
                self.MW.PT1002.SetValue(self.Client.receive_dic["data"]["PT"]["PT1002"])

                self.MW.PT001.SetValue(self.Client.receive_dic["data"]["PT"]["PT001"])
                self.MW.PT002.SetValue(self.Client.receive_dic["data"]["PT"]["PT002"])
                self.MW.PT003.SetValue(self.Client.receive_dic["data"]["PT"]["PT003"])
                self.MW.PT004.SetValue(self.Client.receive_dic["data"]["PT"]["PT004"])

                self.MW.BGA1.SetValue(self.Client.receive_dic["data"]["PT"]["BGA1"])
                self.MW.BGA2.SetValue(self.Client.receive_dic["data"]["PT"]["BGA2"])
        
    

                # self.MW.TT2118.SetValue(self.MW.PLC.RTD[0])






                if self.Client.receive_dic["MainAlarm"]:
                    self.MW.AlarmButton.ButtonAlarmSetSignal()
                else:
                    self.MW.AlarmButton.ButtonAlarmResetSignal()
                # # # generally checkbutton.clicked -> move to updatedisplay



                time.sleep(1)
        except:
            (type, value, traceback) = sys.exc_info()
            exception_hook(type, value, traceback)

    @QtCore.Slot()
    def stop(self):
        self.Running = False

    def FindDistinctTrue(self,v0, v1, v2, v3):
        if v0 == True:
            if True in [v1, v2, v3]:
                print("Multiple True values")
                return "False"
            else:
                return "MODE0"
        elif v1 == True:
            if True in [ v2, v3]:
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
            if True in [ v2, v3]:
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
