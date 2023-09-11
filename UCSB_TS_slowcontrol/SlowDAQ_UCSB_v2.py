"""
This is the main SlowDAQ code used to read/setproperties of the TPLC and PPLC

By: Mathieu Laurin

v0.1.0 Initial code 29/11/19 ML
v0.1.1 Read and write implemented 08/12/19 ML
v0.1.2 Alarm implemented 07/01/20 ML
v0.1.3 PLC online detection, poll PLCs only when values are updated, fix Centos window size bug 04/03/20 ML
"""

import os, sys, time, platform, datetime, random, pickle, cgitb

from PySide6 import QtWidgets, QtCore, QtGui

#from SlowDAQ_UCSB_v2 import *
from PLC import *
from PICOPW import VerifyPW
from SlowDAQWidgets_UCSB_v2 import *
import zmq

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
        pixmap_thermalsyphon = QtGui.QPixmap("/Users/haleyfogg/Desktop/henry_ts_panel")
        pixmap_thermalsyphon = pixmap_thermalsyphon.scaledToWidth(2400*R)
        self.ThermosyphonTab.Background.setPixmap(QtGui.QPixmap(pixmap_thermalsyphon))
        self.ThermosyphonTab.Background.move(0*R, 0*R)
        self.ThermosyphonTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.GasTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.GasTab, "Gas Panel")

        self.GasTab.Background = QtWidgets.QLabel(self.GasTab)
        self.GasTab.Background.setScaledContents(True)
        self.GasTab.Background.setStyleSheet('background-color:black;')
        pixmap_gas = QtGui.QPixmap("/Users/haleyfogg/Desktop/henry_gas_panel") 
        pixmap_gas = pixmap_gas.scaledToWidth(2400 * R)
        self.GasTab.Background.setPixmap(QtGui.QPixmap(pixmap_gas))
        self.GasTab.Background.move(0 * R, 0 * R)
        self.GasTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.TubeTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.TubeTab, "Inner Tube")

        self.TubeTab.Background = QtWidgets.QLabel(self.TubeTab)
        self.TubeTab.Background.setScaledContents(True)
        self.TubeTab.Background.setStyleSheet('background-color:black;')
        pixmap_tube = QtGui.QPixmap("/Users/haleyfogg/Desktop/henry_tube")
        pixmap_tube = pixmap_tube.scaledToWidth(2400 * R)
        self.TubeTab.Background.setPixmap(QtGui.QPixmap(pixmap_tube))
        self.TubeTab.Background.move(0 * R, 0 * R)
        self.TubeTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.DatanSignalTab = QtWidgets.QWidget(self.Tab)
        self.Tab.addTab(self.DatanSignalTab, "Data and Signal Panel")

        self.DatanSignalTab.Background = QtWidgets.QLabel(self.DatanSignalTab)
        self.DatanSignalTab.Background.setScaledContents(True)
        self.DatanSignalTab.Background.setStyleSheet('background-color:black;')
        pixmap_DatanSignal = QtGui.QPixmap("/Users/haleyfogg/Desktop/Default_Background")
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

        self.PT1012 = PressureIndicator(self.ThermosyphonTab)
        self.PT1012.Label.setText("PT1012")
        self.PT1012.move(145 * R, 30 * R)

        self.PT1013 = PressureIndicator(self.ThermosyphonTab)
        self.PT1013.Label.setText("PT1013")
        self.PT1013.move(155 * R, 975 * R)

        self.PT1014 = PressureIndicator(self.ThermosyphonTab)
        self.PT1014.Label.setText("PT1014")
        self.PT1014.move(160 * R, 1160 * R)

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
        self.address ={'PV1001':10001,'PV1002':10002,'PV1003':10003,'PV1004':10004,'PV1005':10005,'PV1006':10006,'PV1007':10007,'PT1012':10012,
                       'PT1013':10013,'PT1014':10014, 
                       'PV001':20001,'PV002':20002,'PV003':20003,'PV004':20004, 'PV005':20005,'PV006':20006,'PV007':20007,'PV008':20008,
                       'PV009':20009,'PV010':20010,'PV011':20011,'PV012':20012,'PV013':20013,'PT001':30001,'PT002':30002,'PT003':30003,'PT004':30004,
                       'BGA1':40001,'BGA2':40002,'MFC1':50001, 'MFC2':50002,
                       'H1':60001,'H2':60002, 'H3':60003, 'H4':60004, 'LiqLev':70000, 
                       'RTD1':80001,'RTD2':80002,'RTD3':80003,'RTD4':80004,'RTD5':80005,'RTD6':80006}
        self.commands = {}

        self.signal_connection()

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

        self.AlarmButton.SubWindow.PT1012.updatebutton.clicked.connect(
            lambda: self.FPTTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1012.Label.text(),
                                       Act=self.AlarmButton.SubWindow.PT1012.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.PT1012.Low_Limit.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.PT1012.High_Limit.Field.text()))

        self.AlarmButton.SubWindow.PT1013.updatebutton.clicked.connect(
            lambda: self.FPTTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1013.Label.text(),
                                       Act=self.AlarmButton.SubWindow.PT1013.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.PT1013.Low_Limit.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.PT1013.High_Limit.Field.text()))

        self.AlarmButton.SubWindow.PT1014.updatebutton.clicked.connect(
            lambda: self.FPTTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1014.Label.text(),
                                       Act=self.AlarmButton.SubWindow.PT1014.AlarmMode.isChecked(),
                                       LowLimit=self.AlarmButton.SubWindow.PT1014.Low_Limit.Field.text(),
                                       HighLimit=self.AlarmButton.SubWindow.PT1014.High_Limit.Field.text()))


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
    def update_alarmwindow(self,dic):

        self.AlarmButton.CollectAlarm([self.AlarmButton.SubWindow.PT1012.Alarm,
                                          self.AlarmButton.SubWindow.PT1013.Alarm,
                                          self.AlarmButton.SubWindow.PT1014.Alarm])
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

        self.TT_FP_dic = {"TT2420": 0}

        self.PT_dic = {"PT1012": 0, "PT1013": 0, "PT1014": 0, "PT001": 0, "PT002": 0, "PT003": 0, "PT004": 0, "BGA1": 0, "BGA2": 0}

        self.TT_FP_LowLimit = {"TT2420": 0}

        self.TT_FP_HighLimit = {"TT2420": 30}

        self.PT_LowLimit = {"PT1012": 0, "PT1013": 0, "PT1014": 0, "PT001": 0, "PT002": 0, "PT003": 0, "PT004": 0, "BGA1": 0, "BGA2": 0}

        self.PT_HighLimit = {"PT1012": 0, "PT1013": 0, "PT1014": 0, "PT001": 0, "PT002": 0, "PT003": 0, "PT004": 0, "BGA1": 0, "BGA2": 0}

        self.TT_FP_Activated = {"TT2420": True}

        self.PT_Activated = {"PT1012": True, "PT1013": True, "PT1014": True}

        self.TT_FP_Alarm = {"TT2420": False}

        self.PT_Alarm = {"PT1012": False, "PT1013": False, "PT1014": False}
        self.MainAlarm = False

        self.Valve_OUT = {"PV1001": 0, "PV1002": 0, "PV1003": 0, "PV1004": 0, "PV1005": 0, "PV1006": 0,
                          "PV1007": 0, "MFC1008": 0, "PV001": 0,"PV002": 0, "PV003": 0, "PV004": 0, 
                          "PV005": 0, "PV006": 0,"PV007": 0, "PV008": 0, "PV009": 0, "PV010": 0, 
                          "PV011": 0, "PV012": 0, "PV013": 0, "MFC1":0, "MFC2": 0}

        self.Valve_MAN = {"PV1001": True, "PV1002": True, "PV1003": True, "PV1004": True, "PV1005": True, "PV1006": True,
                          "PV1007": True, "MFC1008": True,"PV001": True, "PV002": True, "PV003": True, "PV004": True,
                          "PV005": True, "PV006": True, "PV007": True, "PV008": True, "PV009": True, "PV010": True, 
                          "PV011": True, "PV012": True, "PV013": True, "MFC1": True, "MFC2": True}

        self.Valve_INTLKD = {"PV1001": False, "PV1002": False, "PV1003": False, "PV1004": False, "PV1005": False, "PV1006": False,
                          "PV1007": False, "MFC1008": False,"PV001": False, "PV002": False, "PV003": False, "PV004": False,
                          "PV005": False, "PV006": False, "PV007": False, "PV008": False, "PV009": False, "PV010": False, 
                          "PV011": False, "PV012": False, "PV013": False, "MFC1": False, "MFC2": False}

        self.Valve_ERR = {"PV1001": False, "PV1002": False, "PV1003": False, "PV1004": False, "PV1005": False, "PV1006": False,
                          "PV1007": False, "MFC1008": False,"PV001": False, "PV002": False, "PV003": False, "PV004": False,
                          "PV005": False, "PV006": False, "PV007": False, "PV008": False, "PV009": False, "PV010": False, 
                          "PV011": False, "PV012": False, "PV013": False, "MFC1": False, "MFC2": False}


        self.receive_dic = {"data":{"TT":{"FP":self.TT_FP_dic,
                                          },
                                    "PT":self.PT_dic,
                                    "Valve":{"OUT":self.Valve_OUT,
                                             "INTLKD":self.Valve_INTLKD,
                                             "MAN":self.Valve_MAN,
                                             "ERR":self.Valve_ERR},
                                   },
                             "Alarm":{"TT" : {"FP":self.TT_FP_Alarm,
                                              },
                                      "PT" : self.PT_Alarm},
                             "MainAlarm" : self.MainAlarm}
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

                self.MW.AlarmButton.SubWindow.PT1012.UpdateAlarm(self.Client.receive_dic["Alarm"]["PT"]["PT1012"])
                self.MW.AlarmButton.SubWindow.PT1012.Indicator.SetValue(
                    self.Client.receive_dic["data"]["PT"]["PT1012"])

                self.MW.AlarmButton.SubWindow.PT1013.UpdateAlarm(self.Client.receive_dic["Alarm"]["PT"]["PT1013"])
                self.MW.AlarmButton.SubWindow.PT1013.Indicator.SetValue(
                    self.Client.receive_dic["data"]["PT"]["PT1013"])

                self.MW.AlarmButton.SubWindow.PT1014.UpdateAlarm(self.Client.receive_dic["Alarm"]["PT"]["PT1014"])
                self.MW.AlarmButton.SubWindow.PT1014.Indicator.SetValue(
                    self.Client.receive_dic["data"]["PT"]["PT1014"])

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

                self.MW.PT1012.SetValue(self.Client.receive_dic["data"]["PT"]["PT1012"])
                self.MW.PT1013.SetValue(self.Client.receive_dic["data"]["PT"]["PT1013"])
                self.MW.PT1014.SetValue(self.Client.receive_dic["data"]["PT"]["PT1014"])

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

    sys.exit(App.exec())

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
