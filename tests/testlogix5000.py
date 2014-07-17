
import sys
from random import randint

sys.path.append("../")

from tuxeip import TuxEIP, LGX, LGX_REAL

tux = TuxEIP(libpath="../libtuxeip.dylib")

myctr = randint(0,9999)
    
sess = tux.OpenSession("192.168.0.1")
reg = tux.RegisterSession(sess)

conn = tux.ConnectPLCOverCNET(sess, LGX, 1, 100, 123, randint(0,9999), 123, 321, 100, 5000, 1, '01')

read_num = 1
read_var = "Settings[40]"

tux.WriteLGXData(sess, conn, read_var, LGX_REAL, myctr, 1)

data = tux.ReadLGXDataAsFloat(sess, conn, read_var, read_num)

print data

tux.Forward_Close(conn)
tux.UnRegisterSession(sess)
tux.CloseSession(sess)


