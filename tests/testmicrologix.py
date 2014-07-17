
import sys
from random import randint

sys.path.append("../")

from tuxeip import TuxEIP, SLC500, PLC_FLOATING

tux = TuxEIP(libpath="../libtuxeip.dylib")

myctr = randint(0,9999)

sess = tux.OpenSession("192.168.0.1")
reg = tux.RegisterSession(sess)

conn = tux.ConnectPLCOverCNET(sess, SLC500, 0, 100, 0, 1, 123, 321, 100, 5000, 1, '01')

read_num = 1
read_var = "F100:40"

tux.WritePLCData(sess, conn, None, None, 0, SLC500, 123, read_var, PLC_FLOATING, myctr, 1)

data = tux.ReadPLCDataAsInteger(sess, conn, None, None, 0, SLC500, 123, read_var, read_num)

print data

tux.Forward_Close(conn)
tux.UnRegisterSession(sess)
tux.CloseSession(sess)

