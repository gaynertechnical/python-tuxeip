
from tuxeip import TuxEIP, SLC500

tux = TuxEIP()

sess = tux.OpenSession("10.205.0.236")
print sess

reg = tux.RegisterSession(sess)
print reg

conn = tux.ConnectPLCOverCNET(sess, SLC500, 0, 100, 0, 1, 123, 321, 100, 5000, 1, '01')
print conn

read_num = 1
read_var = "F8:0"

myctr = 0
while True:

    data1 = tux.ReadPLCData(sess, conn, None, None, 0, SLC500, myctr, "F8:0", 10)
    
    print tux.PCCC_GetValueAsFloat(data1)

    data2 = tux.ReadPLCData(sess, conn, None, None, 0, SLC500, myctr, "N7:1", 1)
    
    print tux.PCCC_GetValueAsInt(data2)

    myctr += 1

