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
PLC_BYTE_STRING=3
PLC_INTEGER=4
PLC_TIMER=5
PLC_COUNTER=6
PLC_CONTROL=7
PLC_FLOATING=8
PLC_ARRAY=9
PLC_ADRESS=15
PLC_BCD=16

# LOGIX DATA TYPES
LGX_BOOL=0xC1
LGX_BITARRAY=0xD3
LGX_SINT=0xC2
LGX_INT=0xC3
LGX_DINT=0xC4
LGX_REAL=0xCA

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

class TuxEIPException(Exception):
    def __init__(self):
        Exception.__init__(self)

class TuxEIP:

    def __init__(self, **kwargs):
        self.__libpath = kwargs.get("libpath", "libtuxeip.dylib")
        self.__tuxeip = CDLL(self.__libpath)
        self.__tuxeip._cip_err_msg.restype = c_char_p

    def OpenSession(self, slaveip_, slaveport_=44818, slavetimeout_=1000):
        self.__tuxeip._OpenSession.restype = POINTER(Eip_Session)

        # Convert params to C types
        slaveip = c_char_p(slaveip_)
        slaveport = c_int(slaveport_)
        slavetimeout = c_int(slavetimeout_)

        session = self.__tuxeip._OpenSession(slaveip, slaveport, slavetimeout)
        
        #print self.__tuxeip._cip_err_msg, self.__tuxeip._cip_errno, self.__tuxeip._cip_ext_errno

        if bool(session) == False:
            raise TuxEIPException()

        return session

    def RegisterSession(self, sess_):
        self.__tuxeip._RegisterSession.restype = c_int
        reg = self.__tuxeip._RegisterSession(sess_)

        if reg != False:
            raise TuxEIPException()

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
            raise TuxEIPException()

        return connection

    def ReadLgxData(self, sess_, conn_, var_, num_):
        self.__tuxeip._ReadLgxData.restype = POINTER(Eip_PLC_Read)
        readdata = self.__tuxeip._ReadLgxData(sess_, conn_, var_, num_)

        if bool(readdata) == False:
            raise TuxEIPException()

        return readdata

    def WriteLGXData(self, sess_, conn_, address_, datatype_, data_, num_ ):
        if datatype_ == LGX_INT:
            data = c_int(data_)
        elif datatype_ == LGX_REAL:
            data = c_float(data_)
        else:
            raise TuxEIPException()

        data = self.__tuxeip._WriteLgxData(sess_, conn_, address_, datatype_, byref(data), num_)

        return data

    def ReadLGXDataAsFloat(self, sess_, conn_, var_, num_):
        data = self.ReadLgxData(sess_, conn_, var_, num_)
        d = self.GetLGXValueAsFloat(data)
        self.FreePLCRead(data)
        return d

    def ReadLGXDataAsInteger(self, sess_, conn_, var_, num_):
        data = self.ReadLgxData(sess_, conn_, var_, num_)
        d = self.GetLGXValueAsInteger(data)
        self.FreePLCRead(data)
        return d

    def ReadPLCDataAsFloat(self, sess_, conn_, dhp_, routepath_, routesize_, plctype_, tns_, address_, number_):
        data = self.ReadPLCData(sess_, conn_, dhp_, routepath_, routesize_, plctype_, tns_, address_, number_)
        d = self.PCCC_GetValueAsFloat(data)
        self.FreePLCRead(data)
        return d

    def ReadPLCDataAsInteger(self, sess_, conn_, dhp_, routepath_, routesize_, plctype_, tns_, address_, number_):
        data = self.ReadPLCData(sess_, conn_, dhp_, routepath_, routesize_, plctype_, tns_, address_, number_)
        d = self.PCCC_GetValueAsInteger(data)
        self.FreePLCRead(data)
        return d

    def ReadPLCData(self, sess_, conn_, dhp_, routepath_, routesize_, plctype_, tns_, address_, number_):
        self.__tuxeip._ReadPLCData.restype = POINTER(Eip_PLC_Read)
        readdata = self.__tuxeip._ReadPLCData(sess_, conn_, dhp_, routepath_, routesize_, plctype_,
                                                tns_, address_, number_)

        if bool(readdata) == False:
            raise TuxEIPException()

        return readdata

    def GetLGXValueAsFloat(self, readdata_):
        if bool(readdata_) == False:
            return None

        self.__tuxeip._GetLGXValueAsFloat.restype = c_float
        values = []
        for i in range(0, readdata_.contents.Varcount):
            v = self.__tuxeip._GetLGXValueAsFloat(readdata_, i)
            values.append(v)

        return values

    def GetLGXValueAsInteger(self, readdata_):
        if bool(readdata_) == False:
            return None

        self.__tuxeip._GetLGXValueAsInteger.restype = c_int
        values = []
        for i in range(0, readdata_.contents.Varcount):
            v = self.__tuxeip._GetLGXValueAsInteger(readdata_, i)
            values.append(v)

        return values
    
    def PCCC_GetValueAsFloat(self, readdata_):
        if bool(readdata_) == False:
            return None

        self.__tuxeip._PCCC_GetValueAsFloat.restype = c_float
        values = []
        for i in range(0, readdata_.contents.Varcount):
            v = self.__tuxeip._PCCC_GetValueAsFloat(readdata_, i)
            values.append(v)

        return values

    def PCCC_GetValueAsInteger(self, readdata_):
        if bool(readdata_) == False:
            return None

        self.__tuxeip._PCCC_GetValueAsInteger.restype = c_int
        values = []
        for i in range(0, readdata_.contents.Varcount):
            v = self.__tuxeip._PCCC_GetValueAsInteger(readdata_, i)
            values.append(v)

        return values

    def WritePLCData(self, sess_, conn_, dhp_, routepath_, routesize_, plctype_, tns_, address_, datatype_, data_, number_):

        if datatype_ == PLC_INTEGER:
            data = c_int(data_)
        elif datatype_ == PLC_FLOATING:
            data = c_float(data_)
        else:
            raise TuxEIPException()

        result = self.__tuxeip._WritePLCData(sess_, conn_, dhp_, routepath_, routesize_, plctype_,
                                                tns_, address_,  datatype_, byref(data), number_)

        return result

    def Forward_Close(self, conn_):
        self.__tuxeip._Forward_Close(conn_)

    def UnRegisterSession(self, sess_):
        self.__tuxeip._UnRegisterSession(sess_)

    def CloseSession(self, sess_):
        self.__tuxeip.CloseSession(sess_)

    def FreePLCRead(self, data_):
        self.__tuxeip._FreePLCRead(data_)
    
