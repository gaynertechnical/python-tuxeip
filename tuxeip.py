#! /usr/bin/env python

from ctypes import *

# PLC TYPES
Unknow=0
PLC=1
SLC500=2
LGX=3

# EIP DATA TYPES
PLC_BIT=1
PLC_BIT_STRING=2
PLC_BYTE_STRING=3,
PLC_INTEGER=4
PLC_TIMER=5
PLC_COUNTER=6
PLC_CONTROL=7
PLC_FLOATING=8
PLC_ARRAY=9
PLC_ADRESS=15
PLC_BCD=16

class Eip_Session(Structure):
    _fields_ = [
        ('sock',c_int),
        ('Session_Handle', c_uint),
        ('Sender_ContextL',c_int),
        ('Sender_ContextH',c_int),
        ('timeout', c_int),
        ('references', c_int),
        ('Data', c_void_p),
    ]

class Eip_Connection(Structure):
    _fields_ = [
        ('Eip_Session', Eip_Session),
        ('references', c_int),
        ('Data', c_void_p),
        ('ConnectionSerialNumber', c_uint),
        ('OriginatorVendorID', c_uint),
        ('OriginatorSerialNumber', c_int),
        ('OT_ConnID', c_int),
        ('TO_ConnID', c_int),
        ('packet', c_short),
        ('Path_size', c_byte)
    ]

class Eip_PLC_Read(Structure):
    _fields_ = [
        ('type', c_int),
        ('Varcount', c_int),
        ('totalise', c_int),
        ('elementsize', c_int),
        ('mask', c_uint),
    ]

class TuxEIP_CouldntOpenSession(Exception):
    def __init__(self):
        Exception.__init__(self)

class TuxEIP_CouldntRegisterSession(Exception):
    def __init__(self):
        Exception.__init__(self)

class TuxEIP_CouldntBeginEIPConnection(Exception):
    def __init__(self):
        Exception.__init__(self)

class TuxEIP_ReadPLCDataFailed(Exception):
    def __init__(self):
        Exception.__init__(self)

class TuxEIP:

    def __init__(self, **kwargs):
        self.__libpath = kwargs.get("libpath", "libtuxeip.dylib")
        self.__tuxeip = CDLL(self.__libpath)

    def OpenSession(self, slaveip_, slaveport_=44818, slavetimeout_=1000):
        self.__tuxeip._OpenSession.restype = POINTER(Eip_Session)

        # Convert params to C types
        slaveip = c_char_p(slaveip_)
        slaveport = c_int(slaveport_)
        slavetimeout = c_int(slavetimeout_)

        session = self.__tuxeip._OpenSession(slaveip, slaveport, slavetimeout)

        if bool(session) == False:
            raise TuxEIP_CouldntOpenSession()

        return session

    def RegisterSession(self, sess_):
        self.__tuxeip._RegisterSession.restype = c_int
        reg = self.__tuxeip._RegisterSession(sess_)

        print reg
        #if bool(reg) == False:
        #    raise TuxEIP_CouldntRegisterSession()

        return reg

    def ConnectPLCOverCNET(self, sess_, plctype_, priority_, timeoutticks_, connid_, conserial_, 
                            vendorid_, serialnum_, timeoutmult_, rpi_, transport_, slavepath_):
        # Convert params to C types
        priority = c_byte(priority_)
        timeoutticks = c_byte(timeoutticks_)
        connid = c_uint(connid_)
        conserial = c_ushort(conserial_)
        vendorid = c_ushort(vendorid_)
        serialnum = c_uint(serialnum_)
        timeutmult = c_byte(timeoutmult_)
        rpi = c_uint(rpi_)
        transport = c_byte(transport_)
        slavepath = c_char_p(slavepath_)
        pathlength = len(slavepath_)

        self.__tuxeip._ConnectPLCOverCNET.restype = POINTER(Eip_Connection)

        connection = self.__tuxeip._ConnectPLCOverCNET(
            sess_,
            plctype_,
            priority, 
            timeoutticks,
            connid, 
            conserial,
            vendorid,
            serialnum,
            timeutmult,
            rpi, 
            transport,
            slavepath,
            pathlength
        )

        if bool(connection) == False:
            raise TuxEIP_CouldntBeginEIPConnection()

        return connection

    def ReadPLCData(self, sess_, conn_, dhp_, routepath_, routesize_, plctype_, tns_, address_, number_):
        self.__tuxeip._ReadPLCData.restype = POINTER(Eip_PLC_Read)
        readdata = self.__tuxeip._ReadPLCData(sess_, conn_, dhp_, routepath_, routesize_, plctype_,
                                                tns_, address_, number_)

        if bool(readdata) == False:
            raise TuxEIP_ReadPLCDataFailed()

        return readdata
    
    def PCCC_GetValueAsFloat(self, readdata_):
        if bool(readdata_) == False:
            return None

        self.__tuxeip._PCCC_GetValueAsFloat.restype = c_float
        values = []
        for i in range(0, readdata_.contents.Varcount):
            v = self.__tuxeip._PCCC_GetValueAsFloat(readdata_, i)
            values.append(v)

        return values

    def PCCC_GetValueAsInt(self, readdata_):
        if bool(readdata_) == False:
            return None

        self.__tuxeip._PCCC_GetValueAsInteger.restype = c_int
        values = []
        for i in range(0, readdata_.contents.Varcount):
            v = self.__tuxeip._PCCC_GetValueAsInteger(readdata_, i)
            values.append(v)

        return values

    def WritePLCData(self):
        pass

    def CloseSession(self, sess_):
        pass
    
