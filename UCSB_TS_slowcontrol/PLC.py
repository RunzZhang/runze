"""
Class PLC is used to read/write via modbus to the temperature PLC

To read the variable, just call the ReadAll() method
To write to a variable, call the proper setXXX() method

By: Mathieu Laurin

v1.0 Initial code 25/11/19 ML
v1.1 Initialize values, flag when values are updated more modbus variables 04/03/20 ML
"""

import struct, time, zmq, sys, pickle
import numpy as np
from PySide2 import QtWidgets, QtCore, QtGui
# from Database_SBC import *
import socket
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import requests
import os

# delete random number package when you read real data from PLC
import random
from pymodbus.client.sync import ModbusTcpClient

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


class PLC:
    def __init__(self):
        super().__init__()

        IP_NI = "10.111.19.100"
        # Lakeshore1 10.111.19.100 and lakeshore 2 10.111.19.102
        PORT_NI = 7777
        self.BUFFER_SIZE = 1024


        self.Client = ModbusTcpClient(IP_NI, port=PORT_NI)
        self.Connected = self.Client.connect()
        print("NI connected: " + str(self.Connected))

        self.socket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((IP_NI,PORT_NI))

        #Adam
        IP_BO = "10.111.19.101"
        PORT_BO = 502
        #135,,139, 445,3389,5700,6000,9012
        self.Client_BO = ModbusTcpClient(IP_BO, port=PORT_BO)
        self.Connected_BO = self.Client_BO.connect()

        # for i in range(0,10000):
        #     self.Client_BO = ModbusTcpClient(IP_BO, port=i)
        #     self.Connected_BO = self.Client_BO.connect()
        #     if self.Connected_BO == True:
        #         print(i)

        print(" Beckoff connected: " + str(self.Connected_BO))

        self.socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_2.connect((IP_BO, PORT_BO))


        self.TT_FP_address = {"TT2420": 10001}


        self.PT_address={'PT1012':10012,'PT1013':10013,'PT10014':10014}

        self.TT_FP_dic = {"TT2420": 0}

        self.PT_dic = {'PT1012':0,'PT1013':0,'PT10014':0}

        self.TT_FP_LowLimit = {"TT2420": 0}

        self.TT_FP_HighLimit = {"TT2420": 30}

        self.PT_LowLimit = {'PT1012':0,'PT1013':0,'PT10014':0}
        self.PT_HighLimit = {'PT1012':300,'PT1013':300,'PT10014':300}

        self.TT_FP_Activated = {"TT2420": True}

        self.PT_Activated = {"PT1012": True, "PT1013": True, "PT1014": True}

        self.TT_FP_Alarm = {"TT2420": False}

        self.PT_Alarm = {"PT1012": False, "PT1013": False, "PT1014": False}

        self.MainAlarm = False
        self.nTT_FP = len(self.TT_FP_address)
        self.nPT = len(self.PT_address)
        self.PT_setting = [0.] * self.nPT
        self.nPT_Attribute = [0.] * self.nPT

        self.valve_address = {'PV1001':10001,'PV1002':10002,'PV1003':10003,'PV1004':10004,'PV1005':10005,'PV1006':10006,'PV1007':10007}
        self.nValve = len(self.valve_address)
        self.Valve = {}
        self.Valve_OUT = {"PV1001": 0, "PV1002": 0, "PV1003": 0, "PV1004": 0, "PV1005": 0, "PV1006": 0,
                          "PV1007": 0, "MFC1008": 0}

        self.Valve_MAN = {"PV1001": True, "PV1002": True, "PV1003": True, "PV1004": True, "PV1005": True, "PV1006": True,
                          "PV1007": True, "MFC1008": True}

        self.Valve_INTLKD = {"PV1001": False, "PV1002": False, "PV1003": False, "PV1004": False, "PV1005": False, "PV1006": False,
                             "PV1007": False, "MFC1008": False}

        self.Valve_ERR = {"PV1001": False, "PV1002": False, "PV1003": False, "PV1004": False, "PV1005": False, "PV1006": False,
                          "PV1007": False, "MFC1008": False}

        self.LiveCounter = 0
        self.NewData_Display = False
        self.NewData_Database = False
        self.NewData_ZMQ=False

    def __del__(self):
        self.Client.close()
        self.Client_BO.close()

    def read_LS(self):
        # print("socket connection",self.socket.stillconnected())
        # command = "HTR?1\n"
        command = "DISPLAY?\n"
        print(command)
        cm_code = command.encode()
        self.socket.send(cm_code)
        data = self.socket.recv(self.BUFFER_SIZE)
        self.socket.close()
        print(data.decode())
        # request = pymodbus.Custom
        # command =1
        # if self.Connected:
            # self.Client.send(command)
            # value = self.Client.execute(request=command)
            # value = self.Client.execute()
            # raw_data = self.Client.send(command)
            # value = self.Client.recv(1024)
            # value = round(
            #         struct.unpack("<f", struct.pack("<HH", raw_data.getRegister(1), raw_data.getRegister(0)))[0], 3)
            # print(value)

    def read_AD(self):

        # Raw_BO_TT_BO = self.Client_BO.read_holding_registers(1, count=2, unit=0x01)
        # print(Raw_BO_TT_BO)
        # TT_BO_dic = round(
        #             struct.unpack(">f", struct.pack(">HH", Raw_BO_TT_BO.getRegister(1), Raw_BO_TT_BO.getRegister(0)))[0], 3)
        # print(TT_BO_dic)

        command2 = "#01\n"
        print("coded command",command2.encode())
        cm_code = command2.encode()
        self.socket_2.send(cm_code)
        data = self.socket_2.recv(self.BUFFER_SIZE)
        self.socket_2.close()
        print("origin data",data)
        print("decode data", data.decode())

    def ReadAll(self):

        if self.Connected:
            # Reading all the RTDs
            Raw_RTDs_FP={}
            for key in self.TT_FP_address:
                Raw_RTDs_FP[key] = self.Client.read_holding_registers(self.TT_FP_address[key], count=2, unit=0x01)
                self.TT_FP_dic[key] = round(
                    struct.unpack("<f", struct.pack("<HH", Raw_RTDs_FP[key].getRegister(1), Raw_RTDs_FP[key].getRegister(0)))[0], 3)
                # print(key,self.TT_FP_address[key], "RTD",self.TT_FP_dic[key])

            # # Set Attributes could be commented(disabled) after it is done
            # Attribute_TTFP_address = {}
            # Raw_TT_FP_Attribute = {}
            # for key in self.TT_FP_address:
            #     Attribute_TTFP_address[key] = FPADS_OUT_AT(self.TT_FP_address[key])
            # print(Attribute_TTFP_address)
            # for key in Attribute_TTFP_address:
            #     print(self.ReadFPAttribute(address = Attribute_TTFP_address[key]))
            #
            #     # self.SetFPRTDAttri(mode = 0x2601, address = Attribute_TTFP_address[key])

                ####################################################################################
        #
        #     Raw2 = self.Client.read_holding_registers(38000, count=self.nRTD * 2, unit=0x01)
        #     for i in range(0, self.nRTD):
        #         self.RTD[i] = round(
        #             struct.unpack("<f", struct.pack("<HH", Raw.getRegister((2 * i) + 1), Raw.getRegister(2 * i)))[0], 3)
        #         # self.RTD[i] = round(
        #         #     struct.unpack("<f", Raw2.getRegister(i))[0], 3)
        #         # self.RTD[i] = round(Raw2.getRegister(i), 3)
        #         # print("Updating PLC", i, "RTD",self.RTD[i])
        #
        #
        #
        #     Attribute = [0.] * self.nRTD
        #     for i in range(0, self.nRTD):
        #         Attribute[i] = self.Client.read_holding_registers(18000 + i * 8, count=1, unit=0x01)
        #         self.nAttribute[i] = hex(Attribute[i].getRegister(0))
        #     # print("Attributes", self.nAttribute)

        if self.Connected_BO:
            Raw_BO_TT_BO = {}
            for key in self.TT_BO_address:
                Raw_BO_TT_BO[key] = self.Client_BO.read_holding_registers(self.TT_BO_address[key], count=2, unit=0x01)
                self.TT_BO_dic[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_BO_TT_BO[key].getRegister(1), Raw_BO_TT_BO[key].getRegister(0)))[0], 3)
                # print(key, "little endian", hex(Raw_BO_TT_BO[key].getRegister(1)),"big endian",hex(Raw_BO_TT_BO[key].getRegister(0)))
                # print(key, "'s' value is", self.TT_BO_dic[key])

            # for key in self.TT_BO_address:
            #     Raw_BO_TT_BO[key] = self.Client_BO.read_holding_registers(self.TT_BO_address[key], count=4, unit=0x01)
            #     self.TT_BO_dic[key] = round(
            #         struct.unpack("<d", struct.pack("<HHHH", Raw_BO_TT_BO[key].getRegister(3),Raw_BO_TT_BO[key].getRegister(2),Raw_BO_TT_BO[key].getRegister(1), Raw_BO_TT_BO[key].getRegister(0)))[0], 3)
            #     print(key, "0th", hex(Raw_BO_TT_BO[key].getRegister(0)),"1st",hex(Raw_BO_TT_BO[key].getRegister(1)),"2nd",hex(Raw_BO_TT_BO[key].getRegister(2)),"3rd",hex(Raw_BO_TT_BO[key].getRegister(3)))
            #     print(key, "'s' value is", self.TT_BO_dic[key])

            # for key in self.TT_BO_address:
            #     Raw_BO_TT_BO[key] = self.Client_BO.read_holding_registers(self.TT_BO_address[key], count=4, unit=0x01)
            #     self.TT_BO_dic[key] = round(
            #         struct.unpack("<f", struct.pack(">f",  Raw_BO_TT_BO[key].getRegister(0)))[0], 3)
            #     print(key, "0th", hex(Raw_BO_TT_BO[key].getRegister(0)),"1st",hex(Raw_BO_TT_BO[key].getRegister(1)),"2nd",hex(Raw_BO_TT_BO[key].getRegister(2)),"3rd",hex(Raw_BO_TT_BO[key].getRegister(3)))
            #     print(key, "'s' value is", self.TT_BO_dic[key])

            Raw_BO_PT = {}
            for key in self.PT_address:
                Raw_BO_PT[key] = self.Client_BO.read_holding_registers(self.PT_address[key], count=2, unit=0x01)
                self.PT_dic[key] = round(
                    struct.unpack("<f", struct.pack(">HH", Raw_BO_PT[key].getRegister(0 + 1),
                                                    Raw_BO_PT[key].getRegister(0)))[0], 3)

                # print(key, "'s' value is", self.PT_dic[key])


            Raw_BO_Valve = {}
            Raw_BO_Valve_OUT = {}
            for key in self.valve_address:
                Raw_BO_Valve[key] = self.Client_BO.read_holding_registers(self.valve_address[key], count=1, unit=0x01)
                self.Valve[key] = struct.pack("H", Raw_BO_Valve[key].getRegister(0))

                self.Valve_OUT[key]= self.ReadCoil(1,self.valve_address[key])
                self.Valve_INTLKD[key] = self.ReadCoil(8, self.valve_address[key])
                self.Valve_MAN[key] = self.ReadCoil(16, self.valve_address[key])
                self.Valve_ERR[key] = self.ReadCoil(32, self.valve_address[key])
                # print(key,"Address with ", self.valve_address[key], "valve value is", self.Valve_OUT[key])
                # print(key, "Address with ", self.valve_address[key], "INTLKD is", self.Valve_INTLKD[key])
                # print(key, "Address with ", self.valve_address[key], "MAN value is", self.Valve_MAN[key])
                # print(key, "Address with ", self.valve_address[key], "ERR value is", self.Valve_ERR[key])

            Raw_LOOPPID_2 = Raw_LOOPPID_4 = Raw_LOOPPID_6 = Raw_LOOPPID_8 = Raw_LOOPPID_10 = Raw_LOOPPID_12 = Raw_LOOPPID_14 = Raw_LOOPPID_16 ={}
            for key in self.LOOPPID_ADR_BASE:
                self.LOOPPID_MODE0[key] = self.ReadCoil(1, self.LOOPPID_ADR_BASE[key])
                self.LOOPPID_MODE1[key] = self.ReadCoil(2, self.LOOPPID_ADR_BASE[key])
                self.LOOPPID_MODE2[key] = self.ReadCoil(2**2, self.LOOPPID_ADR_BASE[key])
                self.LOOPPID_MODE3[key] = self.ReadCoil(2**3, self.LOOPPID_ADR_BASE[key])
                self.LOOPPID_INTLKD[key] = self.ReadCoil(2**8, self.LOOPPID_ADR_BASE[key])
                self.LOOPPID_MAN[key] = self.ReadCoil(2 ** 9, self.LOOPPID_ADR_BASE[key])
                self.LOOPPID_ERR[key] = self.ReadCoil(2 ** 10, self.LOOPPID_ADR_BASE[key])
                self.LOOPPID_SATHI[key] = self.ReadCoil(2 ** 11, self.LOOPPID_ADR_BASE[key])
                self.LOOPPID_SATLO[key] = self.ReadCoil(2 ** 12, self.LOOPPID_ADR_BASE[key])
                self.LOOPPID_EN[key] = self.ReadCoil(2 ** 15, self.LOOPPID_ADR_BASE[key])
                Raw_LOOPPID_2[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key]+2, count=2, unit=0x01)
                Raw_LOOPPID_4[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 4, count=2,
                                                                           unit=0x01)
                Raw_LOOPPID_6[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 6, count=2,
                                                                           unit=0x01)
                Raw_LOOPPID_8[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 8, count=2,
                                                                           unit=0x01)
                Raw_LOOPPID_10[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 10, count=2,
                                                                           unit=0x01)
                Raw_LOOPPID_12[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 12, count=2,
                                                                           unit=0x01)
                Raw_LOOPPID_14[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 14, count=2,
                                                                           unit=0x01)
                Raw_LOOPPID_16[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 16, count=2,
                                                                           unit=0x01)

                self.LOOPPID_OUT[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_2[key].getRegister(1),
                                                    Raw_LOOPPID_2[key].getRegister(0)))[0], 3)

                self.LOOPPID_IN[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_4[key].getRegister(0 + 1),
                                                    Raw_LOOPPID_4[key].getRegister(0)))[0], 3)
                self.LOOPPID_HI_LIM[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_6[key].getRegister(0 + 1),
                                                    Raw_LOOPPID_6[key].getRegister(0)))[0], 3)
                self.LOOPPID_LO_LIM[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_8[key].getRegister(0 + 1),
                                                    Raw_LOOPPID_8[key].getRegister(0)))[0], 3)
                self.LOOPPID_SET0[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_10[key].getRegister(0 + 1),
                                                    Raw_LOOPPID_10[key].getRegister(0)))[0], 3)
                self.LOOPPID_SET1[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_12[key].getRegister(0 + 1),
                                                    Raw_LOOPPID_12[key].getRegister(0)))[0], 3)
                self.LOOPPID_SET2[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_14[key].getRegister(0 + 1),
                                                    Raw_LOOPPID_14[key].getRegister(0)))[0], 3)
                self.LOOPPID_SET3[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_16[key].getRegister(0 + 1),
                                                    Raw_LOOPPID_16[key].getRegister(0)))[0], 3)


            #test the writing function
            # print(self.Read_BO_2(14308))
            # Raw_BO = self.Client_BO.read_holding_registers(14308, count=2, unit=0x01)
            # print('Raw0',Raw_BO.getRegister(0))
            # print('Raw1', Raw_BO.getRegister(1))
            # output_BO = round(struct.unpack(">f", struct.pack(">HH", Raw_BO.getRegister(1), Raw_BO.getRegister(0)))[
            #                       0], 3)
            # self.Write_BO_2(14308,2.0)
            # print(self.Read_BO_2(14308))


            # print("base",self.LOOPPID_MODE0,"\n",self.LOOPPID_MODE1,"\n",self.LOOPPID_MODE2,"\n",self.LOOPPID_MODE3,"\n")
            #
            # print("other",self.LOOPPID_HI_LIM, "\n", self.LOOPPID_LO_LIM, "\n", self.LOOPPID_SET0, "\n", self.LOOPPID_SET1,
            #           "\n")


            # PLC
            Raw = self.Client.read_holding_registers(0x3E9, count=1, unit=0x01)
            self.LiveCounter = Raw.getRegister(0)

            self.NewData_Display = True
            self.NewData_Database = True
            self.NewData_ZMQ = True

            return 0
        else:
            return 1

    def Read_BO_1(self,address):
        Raw_BO = self.Client_BO.read_holding_registers(address, count=1, unit=0x01)
        output_BO = struct.pack("H", Raw_BO.getRegister(0))
        # print("valve value is", output_BO)
        return output_BO

    def Read_BO_2(self,address):
        Raw_BO = self.Client_BO.read_holding_registers(address, count=2, unit=0x01)
        output_BO = round(struct.unpack(">f", struct.pack(">HH", Raw_BO.getRegister(1), Raw_BO.getRegister(0)))[
                0], 3)
        # print("valve value is", output_BO)
        return output_BO

    def float_to_2words(self,value):
        fl = float(value)
        x = np.arange(fl, fl+1, dtype='<f4')
        if len(x) == 1:
            word = x.tobytes()
            piece1,piece2 = struct.unpack('<HH',word)
        else:
            print("ERROR in float to words")
        return piece1,piece2

    def Write_BO_2(self,address, value):
        word1, word2 = self.float_to_2words(value)
        print('words',word1,word2)
        # pay attention to endian relationship
        Raw1 = self.Client_BO.write_register(address, value=word1, unit=0x01)
        Raw2 = self.Client_BO.write_register(address+1, value=word2, unit=0x01)

        print("write result = ", Raw1, Raw2)


    def WriteOpen(self,address):
        output_BO = self.Read_BO_1(address)
        input_BO= struct.unpack("H",output_BO)[0] | 0x0002
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write open result=", Raw)

    def WriteClose(self,address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H",output_BO)[0] | 0x0004
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write close result=", Raw)

    def Reset(self,address):
        Raw = self.Client_BO.write_register(address, value=0x0010, unit=0x01)
        print("write reset result=", Raw)

    # mask is a number to read a particular digit. for example, if you want to read 3rd digit, the mask is 0100(binary)
    def ReadCoil(self, mask,address):
        output_BO = self.Read_BO_1(address)
        masked_output = struct.unpack("H",output_BO)[0] & mask
        if masked_output == 0:
            return False
        else:
            return True


    def ReadFPAttribute(self,address):
        Raw = self.Client.read_holding_registers(address, count=1, unit=0x01)
        output = struct.pack("H", Raw.getRegister(0))
        print(Raw.getRegister(0))
        return output

    def SetFPRTDAttri(self,mode,address):
        # Highly suggested firstly read the value and then set as the FP menu suggests
        # mode should be wrtten in 0x
        # we use Read_BO_1 function because it can be used here, i.e read 2 word at a certain address
        output = self.ReadFPAttribute(address)
        print("output", address, output)
        Raw = self.Client.write_register(address, value=mode, unit=0x01)
        print("write open result=", Raw)
        return 0

    def LOOPPID_SET_MODE(self, address, mode=0):
        output_BO = self.Read_BO_1(address)
        if mode == 0:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0010
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        elif mode == 1:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0020
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        elif mode == 2:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0040
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        elif mode == 3:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0080
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        else:
            Raw = "ERROR in LOOPPID SET MODE"

        print("write result:", "mode=",  Raw)

    def LOOPPID_OUT_ENA(self,address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x2000
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write OUT result=", Raw)

    def LOOPPID_OUT_DIS(self,address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x4000
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write OUT result=", Raw)

    def LOOPPID_SETPOINT(self, address, setpoint, mode = 0):
        if mode == 0:
            self.Write_BO_2(address+10, setpoint)
        elif mode == 1:
            self.Write_BO_2(address+12, setpoint)
        elif mode == 2:
            self.Write_BO_2(address+14, setpoint)
        elif mode == 3:
            self.Write_BO_2(address+16, setpoint)
        else:
            pass

        print("LOOPPID_SETPOINT")

    def LOOPPID_SET_HI_LIM(self,address, value):
        self.Write_BO_2(address + 6, value)
        print("LOOPPID_HI")

    def LOOPPID_SET_LO_LIM(self,address, value):
        self.Write_BO_2(address + 8, value)
        print("LOOPPID_LO")



        
    


    def SaveSetting(self):
        self.WriteBool(0x0, 0, 1)

        return 0  # There is no way to know if it worked... Cross your fingers!

    def SetFlowValve(self, value):

        return self.WriteFloat(0x0, value)

    def SetBottomChillerSetpoint(self, value):

        return self.WriteFloat(0x0, value)

    def SetBottomChillerState(self, State):
        if State == "Off":
            value = 0
        elif State == "On":
            value = 1
        else:
            print("State is either on or off in string format.")
            value = None

        return self.WriteBool(0x0, 0, value)

    def SetBottomChillerPowerReset(self, State):
        if State == "Off":
            value = 0
        elif State == "On":
            value = 1
        else:
            print("State is either on or off in string format.")
            value = None

        return self.WriteBool(0x0, 0, value)

    def SetTopChillerSetpoint(self, value):

        return self.WriteFloat(0x0, value)

    def SetTopChillerState(self, State):
        if State == "Off":
            value = 0
        elif State == "On":
            value = 1
        else:
            print("State is either on or off in string format.")
            value = None

        return self.WriteBool(0x0, 0, value)

    def SetCameraChillerSetpoint(self, value):

        return self.WriteFloat(0x0, value)

    def SetCameraChillerState(self, State):
        if State == "Off":
            value = 0
        elif State == "On":
            value = 1
        else:
            print("State is either on or off in string format.")
            value = None

        return self.WriteBool(0x0, 0, value)

    def SetWaterChillerSetpoint(self, value):

        return self.WriteFloat(0x0, value)

    def SetWaterChillerState(self, State):
        if State == "Off":
            value = 0
        elif State == "On":
            value = 1
        else:
            print("State is either on or off in string format.")
            value = None

        return self.WriteBool(0x0, 0, value)

    def SetInnerPower(self, value):

        return self.WriteFloat(0x0, value)

    def SetOuterClosePower(self, value):

        return self.WriteFloat(0x0, value)

    def SetOuterFarPower(self, value):

        return self.WriteFloat(0x0, value)

    def SetFreonPower(self, value):

        return self.WriteFloat(0x0, value)

    def SetInnerPowerState(self, State):
        if State == "Off":
            self.WriteBool(0x0, 0, 1)
        elif State == "On":
            self.WriteBool(0x0, 0, 1)

        return 0  # There is no way to know if it worked... Cross your fingers!

    def SetOuterClosePowerState(self, State):
        if State == "Off":
            self.WriteBool(0x0, 0, 1)
        elif State == "On":
            self.WriteBool(0x0, 0, 1)

        return 0  # There is no way to know if it worked... Cross your fingers!

    def SetOuterFarPowerState(self, State):
        if State == "Off":
            self.WriteBool(0x0, 0, 1)
        elif State == "On":
            self.WriteBool(0x0, 0, 1)

        return 0  # There is no way to know if it worked... Cross your fingers!

    def SetFreonPowerState(self, State):
        if State == "Off":
            self.WriteBool(0x0, 0, 1)
        elif State == "On":
            self.WriteBool(0x0, 0, 1)

        return 0  # There is no way to know if it worked... Cross your fingers!

    def SetColdRegionSetpoint(self, value):

        return self.WriteFloat(0x0, value)

    def SetHotRegionSetpoint(self, value):

        return self.WriteFloat(0x0, value)

    def SetHotRegionP(self, value):

        return self.WriteFloat(0x0, value)

    def SetHotRegionI(self, value):

        return self.WriteFloat(0x0, value)

    def SetHotRegionD(self, value):

        return self.WriteFloat(0x0, value)

    def SetColdRegionP(self, value):

        return self.WriteFloat(0x0, value)

    def SetColdRegionI(self, value):

        return self.WriteFloat(0x0, value)

    def SetColdRegionD(self, value):

        return self.WriteFloat(0x0, value)

    def SetHotRegionPIDMode(self, Mode):
        if Mode == "Manual":
            value = 0
        elif Mode == "Auto":
            value = 1
        else:
            print("State is either on or off in string format.")
            value = None

        return self.WriteBool(0x0, 0, value)

    def SetColdRegionPIDMode(self, Mode):
        if Mode == "Manual":
            value = 0
        elif Mode == "Auto":
            value = 1
        else:
            print("State is either on or off in string format.")
            value = None

        return self.WriteBool(0x0, 0, value)

    def SetWaterPrimingPower(self, State):
        if State == "Off":
            value = 0
        elif State == "On":
            value = 1
        else:
            print("State is either on or off in string format.")
            value = None

        return self.WriteBool(0x0, 0, value)

    def WriteFloat(self, Address, value):
        if self.Connected:
            value = round(value, 3)
            Dummy = self.Client.write_register(Address, struct.unpack("<HH", struct.pack("<f", value))[1], unit=0x01)
            Dummy = self.Client.write_register(Address + 1, struct.unpack("<HH", struct.pack("<f", value))[0],
                                               unit=0x01)

            time.sleep(1)

            Raw = self.Client.read_holding_registers(Address, count=2, unit=0x01)
            rvalue = round(struct.unpack("<f", struct.pack("<HH", Raw.getRegister(1), Raw.getRegister(0)))[0], 3)

            if value == rvalue:
                return 0
            else:
                return 2
        else:
            return 1

    def WriteBool(self, Address, Bit, value):
        if self.Connected:
            Raw = self.Client.read_coils(Address, count=Bit, unit=0x01)
            Raw.bits[Bit] = value
            Dummy = self.Client.write_coil(Address, Raw, unit=0x01)

            time.sleep(1)

            Raw = self.Client.read_coils(Address, count=Bit, unit=0x01)
            rvalue = Raw.bits[Bit]

            if value == rvalue:
                return 0
            else:
                return 2
        else:
            return 1


# Class to update myseeq database
class UpdateDataBase(QtCore.QObject):
    def __init__(self, PLC, parent=None):
        super().__init__(parent)

        self.PLC = PLC
        self.db = mydatabase()
        self.Running = False
        self.base_period=1
        self.para_TT=0
        self.rate_TT=100
        self.para_PT=0
        self.rate_PT=100
        # c is for valve status
        self.para_Valve = 0
        self.rate_Valve = 100
        self.para_LOOPPID = 0
        self.rate_LOOPPID = 100
        self.Valve_buffer = {"PV1344": 0, "PV4307": 0, "PV4308": 0, "PV4317": 0, "PV4318": 0, "PV4321": 0,
                          "PV4324": 0, "PV5305": 0, "PV5306": 0,
                          "PV5307": 0, "PV5309": 0, "SV3307": 0, "SV3310": 0, "SV3322": 0,
                          "SV3325": 0, "SV3326": 0, "SV3329": 0,
                          "SV4327": 0, "SV4328": 0, "SV4329": 0, "SV4331": 0, "SV4332": 0,
                          "SV4337": 0, "HFSV3312":0, "HFSV3323": 0, "HFSV3331": 0}
        self.LOOPPID_buffer = {'SERVO3321': False, 'HTR6225': False, 'HTR2123': False, 'HTR2124': False,
                                              'HTR2125': False,
                                              'HTR1202': False, 'HTR2203': False, 'HTR6202': False, 'HTR6206': False, 'HTR6210': False,
                                              'HTR6223': False, 'HTR6224': False, 'HTR6219': False, 'HTR6221': False, 'HTR6214': False}
        print("begin updating Database")

    @QtCore.Slot()
    def run(self):
        self.Running = True
        while self.Running:
            self.dt = datetime_in_1e5micro()
            self.early_dt= early_datetime()
            print("Database Updating", self.dt)

            if self.PLC.NewData_Database:
                if self.para_TT>= self.rate_TT:
                    for key in self.PLC.TT_FP_dic:
                        self.db.insert_data_into_datastorage(key, self.dt, self.PLC.TT_FP_dic[key])
                    for key in self.PLC.TT_BO_dic:
                        self.db.insert_data_into_datastorage(key, self.dt, self.PLC.TT_BO_dic[key])
                    # print("write RTDS")
                    self.para_TT=0
                if self.para_PT >= self.rate_PT:
                    for key in self.PLC.PT_dic:
                        self.db.insert_data_into_datastorage(key, self.dt, self.PLC.PT_dic[key])
                    # print("write pressure transducer")
                    self.para_PT=0

                for key in self.PLC.Valve_OUT:
                    # print(key, self.PLC.Valve_OUT[key] != self.Valve_buffer[key])
                    if self.PLC.Valve_OUT[key] != self.Valve_buffer[key]:
                        self.db.insert_data_into_datastorage(key + '_OUT', self.early_dt, self.Valve_buffer[key])
                        self.db.insert_data_into_datastorage(key+'_OUT', self.dt, self.PLC.Valve_OUT[key])
                        self.Valve_buffer[key] = self.PLC.Valve_OUT[key]
                        # print(self.PLC.Valve_OUT[key])
                    else:
                        pass

                if self.para_Valve >= self.rate_Valve:
                    for key in self.PLC.Valve_OUT:
                        self.db.insert_data_into_datastorage(key+'_OUT', self.dt, self.PLC.Valve_OUT[key])
                        self.Valve_buffer[key] = self.PLC.Valve_OUT[key]
                    self.para_Valve = 0

                for key in self.PLC.LOOPPID_EN:
                    # print(key, self.PLC.Valve_OUT[key] != self.Valve_buffer[key])
                    if self.PLC.LOOPPID_EN[key] != self.LOOPPID_buffer[key]:
                        self.db.insert_data_into_datastorage(key + '_EN', self.early_dt, self.LOOPPID_buffer[key])
                        self.db.insert_data_into_datastorage(key+'_EN', self.dt, self.PLC.LOOPPID_EN[key])
                        self.LOOPPID_buffer[key] = self.PLC.LOOPPID_EN[key]
                        # print(self.PLC.Valve_OUT[key])
                    else:
                        pass

                if self.para_LOOPPID >= self.rate_LOOPPID:
                    for key in self.PLC.LOOPPID_EN:
                        self.db.insert_data_into_datastorage(key+'_EN', self.dt, self.PLC.LOOPPID_EN[key])
                        self.LOOPPID_buffer[key] = self.PLC.LOOPPID_EN[key]
                    self.para_LOOPPID = 0







                # print("a",self.para_TT,"b",self.para_PT )

                print("Wrting PLC data to database...")
                self.para_TT += 1
                self.para_PT += 1
                self.para_Valve += 1
                self.para_LOOPPID += 1
                self.PLC.NewData_Database = False

            else:
                print("No new data from PLC")
                pass

            time.sleep(self.base_period)



    @QtCore.Slot()
    def stop(self):
        self.Running = False

# Class to read PLC value every 2 sec
class UpdatePLC(QtCore.QObject):
    def __init__(self, PLC, parent=None):
        super().__init__(parent)

        self.PLC = PLC
        self.message_manager = message_manager()
        self.Running = False
        self.period=1

    @QtCore.Slot()
    def run(self):
        try:
            self.Running = True

            while self.Running:
                print("PLC updating", datetime.datetime.now())
                self.PLC.ReadAll()
                for keyTT_FP in self.PLC.TT_FP_dic:
                    self.check_TT_FP_alarm(keyTT_FP)
                for keyTT_BO in self.PLC.TT_BO_dic:
                    self.check_TT_BO_alarm(keyTT_BO)
                for keyPT in self.PLC.PT_dic:
                    self.check_PT_alarm(keyPT)
                self.or_alarm_signal()
                time.sleep(self.period)
        except KeyboardInterrupt:
            print("PLC is interrupted by keyboard[Ctrl-C]")
            self.stop()
        except:
            (type, value, traceback) = sys.exc_info()
            exception_hook(type, value, traceback)

    @QtCore.Slot()
    def stop(self):
        self.Running = False

    def check_TT_FP_alarm(self, pid):

        if self.PLC.TT_FP_Activated[pid]:
            if int(self.PLC.TT_FP_LowLimit[pid]) > int(self.PLC.TT_FP_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if int(self.PLC.TT_FP_dic[pid]) < int(self.PLC.TT_FP_LowLimit[pid]):
                    self.setTTFPalarm(pid)
                    self.PLC.TT_FP_Alarm[pid] = True
                    # print(pid , " reading is lower than the low limit")
                elif int(self.PLC.TT_FP_dic[pid]) > int(self.PLC.TT_FP_HighLimit[pid]):
                    self.setTTFPalarm(pid)
                    # print(pid,  " reading is higher than the high limit")
                else:
                    self.resetTTFPalarm(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetTTFPalarm(pid)
            pass

    def check_TT_BO_alarm(self, pid):

        if self.PLC.TT_BO_Activated[pid]:
            if int(self.PLC.TT_BO_LowLimit[pid]) > int(self.PLC.TT_BO_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if int(self.PLC.TT_BO_dic[pid]) < int(self.PLC.TT_BO_LowLimit[pid]):
                    self.setTTBOalarm(pid)
                    self.PLC.TT_BO_Alarm[pid] = True
                    # print(pid , " reading is lower than the low limit")
                elif int(self.PLC.TT_BO_dic[pid]) > int(self.PLC.TT_BO_HighLimit[pid]):
                    self.setTTBOalarm(pid)
                    # print(pid,  " reading is higher than the high limit")
                else:
                    self.resetTTBOalarm(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetTTBOalarm(pid)
            pass

    def check_PT_alarm(self, pid):

        if self.PLC.PT_Activated[pid]:
            if int(self.PLC.PT_LowLimit[pid]) > int(self.PLC.PT_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if int(self.PLC.PT_dic[pid]) < int(self.PLC.PT_LowLimit[pid]):
                    self.setPTalarm(pid)
                    self.PLC.PT_Alarm[pid] = True
                    # print(pid , " reading is lower than the low limit")
                elif int(self.PLC.PT_dic[pid]) > int(self.PLC.PT_HighLimit[pid]):
                    self.setPTalarm(pid)
                    # print(pid,  " reading is higher than the high limit")
                else:
                    self.resetPTalarm(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetPTalarm(pid)
            pass

    def setTTFPalarm(self, pid):
        self.PLC.TT_FP_Alarm[pid] = True
        # and send email or slack messages
        msg = "SBC alarm: {pid} is out of range".format(pid=pid)
        # self.message_manager.tencent_alarm(msg)
        # self.message_manager.slack_alarm(msg)

    def resetTTFPalarm(self, pid):
        self.PLC.TT_FP_Alarm[pid] = False
        # and send email or slack messages

    def setTTBOalarm(self, pid):
        self.PLC.TT_BO_Alarm[pid] = True
        # and send email or slack messages
        msg = "SBC alarm: {pid} is out of range".format(pid=pid)
        # self.message_manager.tencent_alarm(msg)
        # self.message_manager.slack_alarm(msg)

    def resetTTBOalarm(self, pid):
        self.PLC.TT_BO_Alarm[pid] = False
        # and send email or slack messages

    def setPTalarm(self, pid):
        self.PLC.PT_Alarm[pid] = True
        # and send email or slack messages
        msg = "SBC alarm: {pid} is out of range".format(pid=pid)
        # self.message_manager.tencent_alarm(msg)
        # self.message_manager.slack_alarm(msg)

    def resetPTalarm(self, pid):
        self.PLC.PT_Alarm[pid] = False
        # and send email or slack messages

    def or_alarm_signal(self):
        if (True in self.PLC.TT_BO_Alarm) or (True in self.PLC.PT_Alarm) or (True in self.PLC.TT_FP_Alarm):
            self.PLC.MainAlarm = True
        else:
            self.PLC.MainAlarm = False


class UpdateServer(QtCore.QObject):
    def __init__(self, PLC, parent=None):
        super().__init__(parent)
        self.PLC = PLC
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")
        self.Running=False
        self.period=1
        print("connect to the PLC server")


        self.TT_FP_dic_ini = self.PLC.TT_FP_dic
        self.TT_BO_dic_ini = self.PLC.TT_BO_dic
        self.PT_dic_ini = self.PLC.PT_dic
        self.TT_FP_LowLimit_ini = self.PLC.TT_FP_LowLimit
        self.TT_FP_HighLimit_ini = self.PLC.TT_FP_HighLimit
        self.TT_BO_LowLimit_ini = self.PLC.TT_BO_LowLimit
        self.TT_BO_HighLimit_ini = self.PLC.TT_BO_HighLimit
        self.PT_LowLimit_ini = self.PLC.PT_LowLimit
        self.PT_HighLimit_ini = self.PLC.PT_HighLimit
        self.TT_FP_Activated = self.PLC.TT_FP_Activated
        self.TT_BO_Activated_ini = self.PLC.TT_BO_Activated
        self.PT_Activated_ini = self.PLC.PT_Activated
        self.TT_FP_Alarm_ini = self.PLC.TT_FP_Alarm
        self.TT_BO_Alarm_ini = self.PLC.TT_BO_Alarm
        self.PT_Alarm_ini = self.PLC.PT_Alarm
        self.MainAlarm_ini = self.PLC.MainAlarm
        self.Valve_OUT_ini = self.PLC.Valve_OUT
        self.Valve_MAN_ini = self.PLC.Valve_MAN
        self.Valve_INTLKD_ini = self.PLC.Valve_INTLKD
        self.Valve_ERR_ini = self.PLC.Valve_ERR
        self.LOOPPID_MODE0_ini = self.PLC.LOOPPID_MODE0
        self.LOOPPID_MODE1_ini = self.PLC.LOOPPID_MODE1
        self.LOOPPID_MODE2_ini = self.PLC.LOOPPID_MODE2
        self.LOOPPID_MODE3_ini = self.PLC.LOOPPID_MODE3
        self.LOOPPID_INTLKD_ini = self.PLC.LOOPPID_INTLKD
        self.LOOPPID_MAN_ini = self.PLC.LOOPPID_MAN
        self.LOOPPID_ERR_ini = self.PLC.LOOPPID_ERR
        self.LOOPPID_SATHI_ini = self.PLC.LOOPPID_SATHI
        self.LOOPPID_SATLO_ini = self.PLC.LOOPPID_SATLO
        self.LOOPPID_EN_ini = self.PLC.LOOPPID_EN
        self.LOOPPID_OUT_ini = self.PLC.LOOPPID_OUT
        self.LOOPPID_IN_ini = self.PLC.LOOPPID_IN
        self.LOOPPID_HI_LIM_ini = self.PLC.LOOPPID_HI_LIM
        self.LOOPPID_LO_LIM_ini = self.PLC.LOOPPID_LO_LIM
        self.LOOPPID_SET0_ini = self.PLC.LOOPPID_SET0
        self.LOOPPID_SET1_ini = self.PLC.LOOPPID_SET1
        self.LOOPPID_SET2_ini = self.PLC.LOOPPID_SET2
        self.LOOPPID_SET3_ini = self.PLC.LOOPPID_SET3

        self.data_dic={"data":{"TT":{"FP":self.TT_FP_dic_ini,
                                     "BO":self.TT_BO_dic_ini},
                               "PT":self.PT_dic_ini,
                               "Valve":{"OUT":self.Valve_OUT_ini,
                                        "INTLKD":self.Valve_INTLKD_ini,
                                        "MAN":self.Valve_MAN_ini,
                                        "ERR":self.Valve_ERR_ini},
                               "LOOPPID":{"MODE0": self.LOOPPID_MODE0_ini,
                                          "MODE1": self.LOOPPID_MODE1_ini,
                                          "MODE2": self.LOOPPID_MODE2_ini,
                                          "MODE3": self.LOOPPID_MODE3_ini,
                                          "INTLKD" : self.LOOPPID_INTLKD_ini,
                                          "MAN" : self.LOOPPID_MAN_ini,
                                         "ERR" : self.LOOPPID_ERR_ini,
                                         "SATHI" : self.LOOPPID_SATHI_ini,
                                        "SATLO" : self.LOOPPID_SATLO_ini,
                                        "EN" : self.LOOPPID_EN_ini,
                                        "OUT" : self.LOOPPID_OUT_ini,
                                        "IN" : self.LOOPPID_IN_ini,
                                        "HI_LIM" : self.LOOPPID_HI_LIM_ini,
                                        "LO_LIM" : self.LOOPPID_LO_LIM_ini,
                                        "SET0" : self.LOOPPID_SET0_ini,
                                        "SET1" : self.LOOPPID_SET1_ini,
                                        "SET2" : self.LOOPPID_SET2_ini,
                                        "SET3" : self.LOOPPID_SET3_ini}},
                       "Alarm":{"TT" : {"FP":self.TT_FP_Alarm_ini,
                                      "BO":self.TT_BO_Alarm_ini},
                                "PT" : self.PT_Alarm_ini},
                       "MainAlarm" : self.MainAlarm_ini}

        self.data_package=pickle.dumps(self.data_dic)



    @QtCore.Slot()
    def run(self):
        self.Running=True
        while self.Running:
            print("refreshing the server")
            if self.PLC.NewData_ZMQ:

                # message = self.socket.recv()
                # print("refreshing")
                # print(f"Received request: {message}")
                self.write_data()

                #  Send reply back to client
                # self.socket.send(b"World")
                self.pack_data()
                # print(self.data_package)
                # data=pickle.dumps([0,0])
                # self.socket.send(data)
                self.socket.send(self.data_package)
                # self.socket.sendall(self.data_package)
                self.PLC.NewData_ZMQ = False
            else:
                print("PLC server stops")
                pass
            time.sleep(self.period)

    @QtCore.Slot()
    def stop(self):
        self.Running = False

    def pack_data(self):


        for key in self.PLC.TT_FP_dic:
            self.TT_FP_dic_ini[key] = self.PLC.TT_FP_dic[key]

        for key in self.PLC.TT_BO_dic:
            self.TT_BO_dic_ini[key]=self.PLC.TT_BO_dic[key]
        for key in self.PLC.PT_dic:
            self.PT_dic_ini[key]=self.PLC.PT_dic[key]
        for key in self.PLC.Valve_OUT:
            self.Valve_OUT_ini[key]=self.PLC.Valve_OUT[key]
        for key in self.PLC.TT_FP_Alarm:
            self.TT_FP_Alarm_ini[key] = self.PLC.TT_FP_Alarm[key]
        for key in self.PLC.TT_BO_Alarm:
            self.TT_BO_Alarm_ini[key] = self.PLC.TT_BO_Alarm[key]
        for key in self.PLC.PT_dic:
            self.PT_Alarm_ini[key] = self.PLC.PT_Alarm[key]
        for key in self.PLC.LOOPPID_MODE0:
            self.LOOPPID_MODE0_ini[key] = self.PLC.LOOPPID_MODE0[key]
        for key in self.PLC.LOOPPID_MODE1:
            self.LOOPPID_MODE1_ini[key] = self.PLC.LOOPPID_MODE1[key]
        for key in self.PLC.LOOPPID_MODE2:
            self.LOOPPID_MODE2_ini[key] = self.PLC.LOOPPID_MODE2[key]
        for key in self.PLC.LOOPPID_MODE3:
            self.LOOPPID_MODE3_ini[key] = self.PLC.LOOPPID_MODE3[key]
        for key in self.PLC.LOOPPID_INTLKD:
            self.LOOPPID_INTLKD_ini[key] = self.PLC.LOOPPID_INTLKD[key]
        for key in self.PLC.LOOPPID_MAN:
            self.LOOPPID_MAN_ini[key] = self.PLC.LOOPPID_MAN[key]
        for key in self.PLC.LOOPPID_ERR:
            self.LOOPPID_ERR_ini[key] = self.PLC.LOOPPID_ERR[key]
        for key in self.PLC.LOOPPID_SATHI:
            self.LOOPPID_SATHI_ini[key] = self.PLC.LOOPPID_SATHI[key]
        for key in self.PLC.LOOPPID_SATLO:
            self.LOOPPID_SATLO_ini[key] = self.PLC.LOOPPID_SATLO[key]
        for key in self.PLC.LOOPPID_EN:
            self.LOOPPID_EN_ini[key] = self.PLC.LOOPPID_EN[key]
        for key in self.PLC.LOOPPID_OUT:
            self.LOOPPID_OUT_ini[key] = self.PLC.LOOPPID_OUT[key]
        for key in self.PLC.LOOPPID_IN:
            self.LOOPPID_IN_ini[key] = self.PLC.LOOPPID_IN[key]
        for key in self.PLC.LOOPPID_HI_LIM:
            self.LOOPPID_HI_LIM_ini[key] = self.PLC.LOOPPID_HI_LIM[key]
        for key in self.PLC.LOOPPID_LO_LIM:
            self.LOOPPID_LO_LIM_ini[key] = self.PLC.LOOPPID_LO_LIM[key]
        for key in self.PLC.LOOPPID_SET0:
            self.LOOPPID_SET0_ini[key] = self.PLC.LOOPPID_SET0[key]
        for key in self.PLC.LOOPPID_SET1:
            self.LOOPPID_SET1_ini[key] = self.PLC.LOOPPID_SET1[key]
        for key in self.PLC.LOOPPID_SET2:
            self.LOOPPID_SET2_ini[key] = self.PLC.LOOPPID_SET2[key]
        for key in self.PLC.LOOPPID_SET3:
            self.LOOPPID_SET3_ini[key] = self.PLC.LOOPPID_SET3[key]

        self.data_dic["MainAlarm"]=self.PLC.MainAlarm
        # print("pack",self.data_dic)
        # print("HTR6214 \n", "MODE0", self.data_dic["data"]["LOOPPID"]["MODE0"]["HTR6214"],
        #             "\n","MODE1", self.data_dic["data"]["LOOPPID"]["MODE1"]["HTR6214"],
        #             "\n","MODE2", self.data_dic["data"]["LOOPPID"]["MODE2"]["HTR6214"],
        #             "\n","MODE3", self.data_dic["data"]["LOOPPID"]["MODE3"]["HTR6214"],
        #             "\n","INTLKD", self.data_dic["data"]["LOOPPID"]["INTLKD"]["HTR6214"],
        #             "\n","MAN", self.data_dic["data"]["LOOPPID"]["MAN"]["HTR6214"],
        #             "\n","ERR", self.data_dic["data"]["LOOPPID"]["ERR"]["HTR6214"],
        #             "\n","SATHI", self.data_dic["data"]["LOOPPID"]["SATHI"]["HTR6214"],
        #             "\n","SATLO", self.data_dic["data"]["LOOPPID"]["SATLO"]["HTR6214"],
        #             "\n","EN", self.data_dic["data"]["LOOPPID"]["EN"]["HTR6214"],
        #             "\n","OUT", self.data_dic["data"]["LOOPPID"]["OUT"]["HTR6214"],
        #             "\n","IN", self.data_dic["data"]["LOOPPID"]["IN"]["HTR6214"],
        #             "\n","HI_LIM", self.data_dic["data"]["LOOPPID"]["HI_LIM"]["HTR6214"],
        #             "\n","LO_LIM", self.data_dic["data"]["LOOPPID"]["LO_LIM"]["HTR6214"],
        #             "\n","SET0", self.data_dic["data"]["LOOPPID"]["SET0"]["HTR6214"],
        #             "\n","SET1", self.data_dic["data"]["LOOPPID"]["SET1"]["HTR6214"],
        #             "\n","SET2", self.data_dic["data"]["LOOPPID"]["SET2"]["HTR6214"],
        #             "\n","SET3", self.data_dic["data"]["LOOPPID"]["SET3"]["HTR6214"])


        self.data_package=pickle.dumps(self.data_dic)

    def write_data(self):
        message = pickle.loads(self.socket.recv())
        print(message)
        if message == {}:
            pass
        else:
            for key in message:
                print(message[key]["type"])
                print(message[key]["type"]=="valve")
                if message[key]["type"]=="valve":
                    if message[key]["operation"]=="OPEN":
                        self.PLC.WriteOpen(address= message[key]["address"])
                    elif message[key]["operation"]=="CLOSE":
                        self.PLC.WriteClose(address= message[key]["address"])
                    else:
                        pass
                elif message[key]["type"] == "TT":
                    if message[key]["server"] == "BO":
                        self.PLC.TT_BO_Activated[key] = message[key]["operation"]["Act"]
                        self.PLC.TT_BO_LowLimit[key] = message[key]["operation"]["LowLimit"]
                        self.PLC.TT_BO_HighLimit[key] = message[key]["operation"]["HighLimit"]

                    elif message[key]["server"] == "FP":
                        self.PLC.TT_FP_Activated[key] = message[key]["operation"]["Act"]
                        self.PLC.TT_FP_LowLimit[key] = message[key]["operation"]["LowLimit"]
                        self.PLC.TT_FP_HighLimit[key] = message[key]["operation"]["HighLimit"]
                    else:
                        pass
                elif message[key]["type"] == "PT":
                    if message[key]["server"] == "BO":
                        self.PLC.PT_Activated[key] = message[key]["operation"]["Act"]
                        self.PLC.PT_LowLimit[key] = message[key]["operation"]["LowLimit"]
                        self.PLC.PT_HighLimit[key] = message[key]["operation"]["HighLimit"]
                    else:
                        pass
                elif message[key]["type"] == "heater_power":
                    if message[key]["operation"] == "EN":
                        self.PLC.LOOPPID_OUT_ENA(address = message[key]["address"])
                    elif message[key]["operation"] == "DISEN":
                        self.PLC.LOOPPID_OUT_DIS(address=message[key]["address"])
                    else:
                        pass
                    #
                    # if message[key]["operation"] == "SETMODE":
                    #     self.PLC.LOOPPID_SET_MODE(address = message[key]["address"], mode = message[key]["value"])
                    # else:
                    #     pass
                elif message[key]["type"] == "heater_para":
                    if message[key]["operation"] == "SET0":
                        # self.PLC.LOOPPID_SET_MODE(address=message[key]["address"], mode= 0)
                        self.PLC.LOOPPID_SETPOINT( address= message[key]["address"], setpoint = message[key]["value"]["SETPOINT"], mode = 0)
                        # self.PLC.LOOPPID_HI_LIM(address=message[key]["address"], value=message[key]["value"]["HI_LIM"])
                        # self.PLC.LOOPPID_LO_LIM(address=message[key]["address"], value=message[key]["value"]["LO_LIM"])
                        self.PLC.LOOPPID_SET_HI_LIM(address=message[key]["address"],
                                                    value=message[key]["value"]["HI_LIM"])
                        self.PLC.LOOPPID_SET_LO_LIM(address=message[key]["address"],
                                                    value=message[key]["value"]["LO_LIM"])

                    elif message[key]["operation"] == "SET1":
                        # self.PLC.LOOPPID_SET_MODE(address=message[key]["address"], mode=1)
                        self.PLC.LOOPPID_SETPOINT( address= message[key]["address"], setpoint = message[key]["value"]["SETPOINT"], mode = 1)
                        self.PLC.LOOPPID_SET_HI_LIM(address=message[key]["address"],
                                                    value=message[key]["value"]["HI_LIM"])
                        self.PLC.LOOPPID_SET_LO_LIM(address=message[key]["address"],
                                                    value=message[key]["value"]["LO_LIM"])
                    elif message[key]["operation"] == "SET2":
                        # self.PLC.LOOPPID_SET_MODE(address=message[key]["address"], mode=2)
                        self.PLC.LOOPPID_SETPOINT( address= message[key]["address"], setpoint = message[key]["value"]["SETPOINT"], mode = 2)
                        self.PLC.LOOPPID_SET_HI_LIM(address=message[key]["address"],
                                                    value=message[key]["value"]["HI_LIM"])
                        self.PLC.LOOPPID_SET_LO_LIM(address=message[key]["address"],
                                                    value=message[key]["value"]["LO_LIM"])
                    elif message[key]["operation"] == "SET3":
                        # self.PLC.LOOPPID_SET_MODE(address=message[key]["address"], mode=3)
                        self.PLC.LOOPPID_SETPOINT( address= message[key]["address"], setpoint = message[key]["value"]["SETPOINT"], mode = 3)
                        self.PLC.LOOPPID_SET_HI_LIM(address=message[key]["address"], value=message[key]["value"]["HI_LIM"])
                        self.PLC.LOOPPID_SET_LO_LIM(address=message[key]["address"], value=message[key]["value"]["LO_LIM"])

                    elif message[key]["type"] == "heater_setmode":
                        if message[key]["operation"] == "SET0":
                            self.PLC.LOOPPID_SET_MODE(address=message[key]["address"], mode= 0)

                        elif message[key]["operation"] == "SET1":
                            self.PLC.LOOPPID_SET_MODE(address=message[key]["address"], mode = 1)

                        elif message[key]["operation"] == "SET2":
                            self.PLC.LOOPPID_SET_MODE(address=message[key]["address"], mode=2)

                        elif message[key]["operation"] == "SET3":
                            self.PLC.LOOPPID_SET_MODE(address=message[key]["address"], mode=3)

                    else:
                        pass




                    # if message[key]["operation"] == "HI_LIM":
                    #     self.PLC.LOOPPID_HI_LIM(address= message[key]["address"], value = message[key]["value"])
                    # else:
                    #     pass
                    #
                    # if message[key]["operation"] == "LO_LIM":
                    #     self.PLC.LOOPPID_HI_LIM(address= message[key]["address"], value = message[key]["value"])



                else:
                    pass



        # if message == b'this is a command':
        #     self.PLC.WriteOpen()
        #     self.PLC.Read_BO_1()
        #     print("I will set valve")
        # elif message == b'no command':
        #     self.PLC.WriteClose()
        #     self.PLC.Read_BO_1()
        #     print("I will stay here")
        # elif message == b'this an anti_conmmand':
        #
        #     print("reset the valve")
        # else:
        #     print("I didn't see any command")
        #     pass



class Update(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        App.aboutToQuit.connect(self.StopUpdater)
        self.StartUpdater()

    def StartUpdater(self):
        self.PLC = PLC()

        # Read PLC value on another thread
        self.PLCUpdateThread = QtCore.QThread()
        self.UpPLC = UpdatePLC(self.PLC)
        self.UpPLC.moveToThread(self.PLCUpdateThread)
        self.PLCUpdateThread.started.connect(self.UpPLC.run)
        self.PLCUpdateThread.start()

        # wait for PLC initialization finished
        time.sleep(2)

        # Update database on another thread
        self.DataUpdateThread = QtCore.QThread()
        self.UpDatabase = UpdateDataBase(self.PLC)
        self.UpDatabase.moveToThread(self.DataUpdateThread)
        self.DataUpdateThread.started.connect(self.UpDatabase.run)
        self.DataUpdateThread.start()

        # Update database on another thread
        self.ServerUpdateThread = QtCore.QThread()
        self.UpServer = UpdateServer(self.PLC)
        self.UpServer.moveToThread(self.ServerUpdateThread)
        self.ServerUpdateThread.started.connect(self.UpServer.run)
        self.ServerUpdateThread.start()


        # Stop all updater threads
    @QtCore.Slot()
    def StopUpdater(self):
        self.UpPLC.stop()
        self.PLCUpdateThread.quit()
        self.PLCUpdateThread.wait()

        self.UpDatabase.stop()
        self.DataUpdateThread.quit()
        self.DataUpdateThread.wait()

        self.UpServer.stop()
        self.ServerUpdateThread.quit()
        self.ServerUpdateThread.wait()

class message_manager():
    def __init__(self):
        # info about tencent mail settings
        self.host_server = "smtp.qq.com"
        self.sender_qq = "390282332"
        self.pwd = "bngozrzmzsbocafa"
        self.sender_mail = "390282332@qq.com"
        # self.receiver1_mail = "cdahl@northwestern.edu"
        self.receiver1_mail = "runzezhang@foxmail.com"
        self.mail_title = "Alarm from SBC"

        #info about slack settings
        self.slack_webhook_url = 'https://hooks.slack.com/services/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'
        self.slack_channel = None
        self.alert_map = {
            "emoji": {
                "up": ":white_check_mark:",
                "down": ":fire:"
            },
            "text": {
                "up": "RESOLVED",
                "down": "FIRING"
            },
            "message": {
                "up": "Everything is good!",
                "down": "Stuff is burning!"
            },
            "color": {
                "up": "#32a852",
                "down": "#ad1721"
            }
        }

    def tencent_alarm(self, message):
        try:
            # The body content of the mail
            mail_content = " Alarm from SBC slowcontrol: " + message
            # sslLogin
            smtp = SMTP_SSL(self.host_server)
            # set_debuglevel() is used for debugging. The parameter value is 1 to enable debug mode and 0 to disable debug mode.
            smtp.set_debuglevel(1)
            smtp.ehlo(self.host_server)
            smtp.login(self.sender_qq, self.pwd)
            # Define mail content
            msg = MIMEText(mail_content, "plain", "utf-8")
            msg["Subject"] = Header(self.mail_title, "utf-8")
            msg["From"] = self.sender_mail
            msg["To"] = self.receiver1_mail
            # send email
            smtp.sendmail(self.sender_mail, self.receiver1_mail, msg.as_string())
            smtp.quit()
            print("mail sent successfully")
        except Exception as e:
            print("mail failed to send")
            print(e)

    def slack_alarm(self, message, status=None):
        data = {
            "text": "AlertManager",
            "username": "Notifications",
            "channel": self.slack_channel,
            "attachments": [{"text": message}]
        #     "attachments": [g
        #         {
        #             "text": "{emoji} [*{state}*] Status Checker\n {message}".format(
        #                 emoji=self.alert_map["emoji"][status],
        #                 state=self.alert_map["text"][status],
        #                 message=self.alert_map["message"][status]
        #             ),
        #             "color": self.alert_map["color"][status],
        #             "attachment_type": "default",
        #             "actions": [
        #                 {
        #                     "name": "Logs",f
        #                     "text": "Logs",
        #                     "type": "button",
        #                     "style": "primary",
        #                     "url": "https://grafana-logs.dashboard.local"
        #                 },
        #                 {
        #                     "name": "Metrics",
        #                     "text": "Metrics",
        #                     "type": "button",
        #                     "style": "primary",
        #                     "url": "https://grafana-metrics.dashboard.local"
        #                 }
        #             ]
        #         }]
        }
        r = requests.post(self.slack_webhook_url, json=data)
        return r.status_code




if __name__ == "__main__":
    # msg_mana=message_manager()
    # msg_mana.tencent_alarm("this is a test message")

    # App = QtWidgets.QApplication(sys.argv)
    # Update=Update()


    PLC=PLC()
    PLC.read_LS()
    PLC.read_AD()

    # sys.exit(App.exec_())


