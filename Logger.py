import matplotlib
import matplotlib.pyplot as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import scipy.integrate as integrate
import scipy.io as io
import scipy.signal as sig
import scipy.ndimage as ndmg
import scipy.stats as stat
import numpy as np
import pandas as pd
import seaborn as sns
import os
import time
import serial
import csv
import sys
import datetime as dt
from Settings import *

print("-> Starting logger")

if fileOut == 'AUTO':
    i=0
    while os.path.exists(f"{logFile}{i}.csv"):
        i += 1
    outFile = f"{logFile}{i}.csv"
else:
    outFile = f"{logFile}{fileOut}.csv"

print("-> Opening serial " + serialPort)
if os.path.exists(serialPort):
    print("-> Found serial " + serialPort)
else: 
    print("-> Serial not found")
    sys.exit()

with serial.Serial(timeout = 5) as ser:
    ser.baudrate = bauds
    ser.port = serialPort
    ser.open()
    ser.flushInput()

    print("-> Writing file " + outFile)
    with open(outFile, 'w') as output:
        output.write( "## logger by patatone ## run started on " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " ##" + "\n")
        output.flush() 

    meas = np.zeros(chanNo)
    measNo = np.zeros(chanNo)
    cnt = 0
    serialOk = 1
    lastTime = dt.datetime.now()

    print("-> Log started on " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

    while True:

        sys.stdout.flush()

        nowTime = time.gmtime()
        timeTagLog = time.strftime(timeTagFormat, nowTime)
        timeTag = "[ " + time.strftime("%Y-%m-%d %H:%M:%S", nowTime) + " ]"

        fromLastTime = dt.datetime.now() - lastTime
        try:
            if ser.isOpen() == False or fromLastTime.seconds > serTimeout :  
                if serialOk == 1:
                    print('\r' + "-> Serial lost " + timeTag, end = '\n')
                serialOk = 0
                ser.close()
                ser.open()
                ser.flushInput()
                serialOk = 1
                print('\r' + "-> Serial restarted " + timeTag, end = '\n')
        except:
            print('\r' + "-> Could not reopen serial " + timeTag, end = '')
            time.sleep(1)

        try:
 
            if serialOk == 1: 
                try:
                    serIn = ser.readline()
                    serParsed = serIn.decode("utf-8")
                    print('\r' + "-> Received [ " + str(serParsed).strip('\n').strip('\r') + "] " + timeTag, end = '')
                    serParsed = serParsed.strip('\n\r').split()
                    for k in range(0, chanNo):
                        try:
                            measTemp =  float(serParsed[k])
                            if measTemp != errorCode and measTemp < tMax and measTemp > tMin :
                                meas[k] += measTemp
                                measNo[k] += 1
                        except:
                            pass
                    cnt += 1
                    lastTime = dt.datetime.now()
                except:
                    print('\r' + "-> Cannot parse serial " + timeTag, end = '')
                    sys.stdout.flush()

            if cnt == avgNo:
                strOut = ""
                with open(outFile, 'a') as output:
                    for k in range(0, chanNo):
                        measTmp = meas[k]
                        measNoTmp = measNo[k]
                        if measNoTmp == 0:
                            strOut += str(errorCode) + separator
                        else:
                            measTmp = np.divide(measTmp, measNoTmp)
                            strOut += precision.format(measTmp) + separator
                    output.write( timeTagLog + separator + strOut[:-1] + '\n')
                    output.flush() 
                meas = np.zeros(chanNo)
                measNo = np.zeros(chanNo)
                cnt = 0

        except:
            output.flush() 
            output.close() 
            ser.close()
            print()
            print("-> Run interrupted " + timeTag)
            break