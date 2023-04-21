import pyvisa as visa
import matplotlib.pyplot as plt
import matplotlib
import socket
import crcmod
import threading
import struct
import time

BOARD_HOST='192.168.3.91'
BOARD_PORT=5005
START_Gs = 1000.0 #起始磁场
END_Gs = 4500.0 #终止磁场
resolution = 100.0 #分辨率
time_continue = 180 #持续时间

matplotlib.rc("font", family='YouYuan')

def wt(a,str):
    a.write(str)
    print(a.query(":SYST:ERR?"))

def crc16Add(read):
    crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
    readcrcout = crc16(read)
#     print(readcrcout)
    return readcrcout

def NMR_PC():
    rm = visa.ResourceManager()
    res = rm.list_resources()
    print(res)
    mydev = rm.open_resource(res[0])

    print(mydev.query('*IDN?;'))
    mydev.write('*CLS;')
    # print(mydev.query(":SYST:ERR?"))
    # print(mydev.query(':FORMat?;:ROUT:CLOS:STAT?;ACT?;'))
    # print(mydev.query(":SYST:ERR?"))
    # #print(mydev.query('MMEM:CAT?;*OPC?'))
    # mydev.write(':CONF:SEAR:MODE AUTO;')
    # print(mydev.query(":SYST:ERR?"))
    # mydev.write(':CONF:SEAR:LIM:HIGH 5436.148837602139790;LOW 1260.342589532940110;')
    # print(mydev.query(":SYST:ERR?"))
    # mydev.write(':CONF:MEAS:MODE AUTO')
    # print(mydev.query(":SYST:ERR?"))
    # print(mydev.query(':STAT:OPER:ENAB?;'))
    # mydev.write(':STAT:OPER:ENAB 4920;')
    # print(mydev.query(":SYST:ERR?"))
    # print(mydev.query(':STAT:OPER:NTR?;'))
    # mydev.write(':STAT:OPER:NTR 56;')
    # print(mydev.query(":SYST:ERR?"))


    # mydev.write(":FORM:DATA ASC;")
    # print(mydev.query(":SYST:ERR?"))
    # mydev.write(":UNIT GAUSS")#单位Gs
    # print(mydev.query(":SYST:ERR?"))


    # mydev.write(":ROUT:ESCAN?")#查找探针
    # mydev.write(":CONF:SEAR:ENAB 1;:CONF:SEAR:MODE AUTO")#打开搜索
    wt(mydev, ":INIT:CONT 0")

    wt(mydev, ":FORM:DATA ASC;")
    wt(mydev, ":UNIT GAUSS;")

    print(mydev.query(":ROUT:PROB:SCAN?"))
    wt(mydev, ":ROUT:CLOS (@1);")

    wt(mydev, ":CONF:SEAR:MODE AUTO;")
    wt(mydev, ':CONF:SEAR:LIM:HIGH 5436.148837602139790;LOW 1260.342589532940110;')

    wt(mydev, ":AVERage2:STAT ON;:AVERage2:TCON EXP;:AVERage2:COUN 20")

    wt(mydev, ":CONF:MEAS:MODE AUTO")
    wt(mydev, ":AVERage2:STAT ON;:AVERage2:TCON EXP;:AVERage2:COUN 20")
    wt(mydev, ":TRIG:SEQuence1:SOUR IMM;COUN 1;")

    wt(mydev, ':STAT:OPER:ENAB 4920;')
    wt(mydev, ':STAT:OPER:NTR 56;')

    wt(mydev, ":INIT:CONT 1")

    curr = []
    i = []
    n = 0
    plt.figure(figsize=(10, 5))
    plt.grid(linestyle='-.')
    plt.title('磁场显示')
    plt.xlabel('点数')
    plt.ylabel('磁场值-Gs')
    while True:
        n = n+1
        print(mydev.query(":STAT:OPER:COND?;"))#搜索进度
        print(mydev.query(":SYST:ERR?"))
        print(mydev.query(":FETC:SPR?;"))
        time.sleep(1)
        # cur_val = float(print(mydev.query(":FETC:SPR?")))#搜索进度
        #cur_val = float(print(mydev.query(":FETC:ARR:FLUX? 1")))#磁场
        # curr.append(cur_val)
        # i.append(n)
        # plt.clf()  # 清除之前画的图
        # plt.grid(linestyle='-.')
        # plt.title('磁场显示')
        # plt.xlabel('点数') 
        # plt.ylabel('磁场值-Gs')
        # plt.plot(i,curr)
        # plt.pause(0.5)

def clent_BOARD():
    clent=socket.socket(socket.AF_INET,socket.SOCK_STREAM)      #定义socket类型，网络通信，TCP
    clent.connect((BOARD_HOST,BOARD_PORT))       #要连接的IP与端口
    print("板卡的ip地址和端口号:", BOARD_HOST,BOARD_PORT)
    now_mf = START_Gs
    while now_mf <= END_Gs:
        arr = [0xA0,0x0B,0x00,0x03,0x53,0x04,0x01]

        arr.extend(bytes.fromhex(struct.pack('<f' ,float(now_mf)).hex()))
        CRC_value = crc16Add(bytes(arr))
        arr.extend(CRC_value.to_bytes(2, "little"))
        clent.send(bytes(arr))
        now_mf = now_mf + resolution
        time.sleep(time_continue)
    clent.close()   #关闭连接
# 创建新线程
thread1 = threading.Thread(target=clent_BOARD)
thread2 = threading.Thread(target=NMR_PC)
threads = []
# 开启新线程
#thread1.start()
thread2.start()

# 添加线程到线程列表
#threads.append(thread1)
threads.append(thread2)

# 等待所有线程完成
for t in threads:
    t.join()
print ("退出主线程")        

