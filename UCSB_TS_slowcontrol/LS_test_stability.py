
import struct, time, zmq, sys, pickle, copy, logging
import numpy as np
from PySide2 import QtWidgets, QtCore, QtGui
from Database_UCSB import *
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket
import requests
import logging,os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import slowcontrol_env_cons as sec
import alarm_set as AS

# delete random number package when you read real data from PLC
import random
from pymodbus.client.sync import ModbusTcpClient



# Initialization of Address, Value Matrix

logging.basicConfig(filename="/home/hep/sbc_error_log.log")
sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print("ExceptType: ", exctype, "Value: ", value, "Traceback: ", traceback)
    # sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

#output address to attribute function in FP ()
def FPADS_OUT_AT(outaddress):
    # 1e5 digit
    e5 = outaddress // 10000
    e4 = (outaddress % 10000) // 1000
    e3 = (outaddress % 1000) // 100
    e2 = (outaddress % 100) // 10
    e1 = (outaddress % 10) // 1
    new_e5 = e5-2
    new_e4 = e4
    new_e321=(e3*100+e2*10+e1)*4
    new_address=new_e5*10000+new_e4*1000+new_e321
    print(e5,e4,e3,e2,e1)
    print(new_address)
    return new_address

def LS_TT_translate(receive):
    # receive would be "float1,float2,float3,float4\r\n"
    # we need to return (float1, float2, float3, float4)
    stripped =  receive.strip("\n")
    stripped =  stripped.strip("\r")
    # stripped = stripped.strip("+")
    # print(stripped)
    str_list = eval(stripped)
    # print("split",str_list)
    float_list =  [float(i) for i in str_list]
    res = tuple(float_list)
    # print("res",res)
    return(res)




# Class to read PLC value every 2 sec
class UpdatePLC(QtCore.QObject):
    AI_slack_alarm = QtCore.Signal(str)
    COUPP_TEXT_alarm = QtCore.Signal(str)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.IP_LS = "10.111.19.109"
        # Lakeshore1 10.111.19.100 and lakeshore 2 10.111.19.102
        self.PORT_LS = 7777
        self.BUFFER_SIZE = 1024
        self.period =1
        self.Client_LS = ModbusTcpClient(self.IP_LS, port=self.PORT_LS)
        self.Connected_LS = self.Client_LS.connect()
        print("LS connected: " + self.IP_LS + str(self.Connected_LS))

    @QtCore.Slot()
    def run(self):
            self.Running = True
            while self.Running:
                try:
                    print("PLC updating", datetime.datetime.now())
                    self.ReadAll()
                except:
                    print("failed")
                    break
                finally:
                    time.sleep(self.period)




    @QtCore.Slot()
    def stop(self):
        self.Running = False

    def ReadAll(self):
        # test part

        self.socket_LS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_LS.connect((self.IP_LS, self.PORT_LS))
        self.socket_LS.settimeout(5)
        print("connection success!2")

        # command = "*RST\r\n"
        command = "KRDG?0\r\n"
        print("size", sys.getsizeof(command))
        cm_code = command.encode('utf-8')
        self.socket_LS.send(cm_code)
        receive = self.socket_LS.recv(1024).decode('utf-8')
        print("decode", command,receive)
        self.socket_LS.close()
        print("connection success!3")

if __name__ =="__main__":
    upplc = UpdatePLC()
    upplc.run()