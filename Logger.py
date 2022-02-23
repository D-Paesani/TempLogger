
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

print()
print()
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
        output.write( "## DS18B20 logger ## run started on " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " ##" + "\n")
        output.flush() 

    meas = np.zeros(chanNo)
    measNo = np.zeros(chanNo)
    cnt = 0
    serialOk = 1
    lastTime = dt.datetime.now()
    nowTime = ""
    samplesfromstart = 0
    
    def printMsg(msg = "", msgEnd = ""):
        print("\r" + "".join([" "]*80), end="")
        timeTag = "[ " + time.strftime("%Y-%m-%d %H:%M:%S", nowTime) + " ]"
        print('\r' + timeTag + " -> " + msg, end = msgEnd)

    def handleStop(exc):
        if exc == KeyboardInterrupt:
            printMsg("Run interrupted by user", '\n')
            sys.exit(-1)

    print("-> Log started on " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    print()
    
    ser.flushInput()
    
    while True:

        fromLastTime = dt.datetime.now() - lastTime
        try:
            if ser.isOpen() == False or fromLastTime.seconds > serTimeout :  
                if serialOk == 1:
                    printMsg("Serial lost ", '\n')
                    time.sleep(0.5)
                serialOk = 0
                ser.close()
                ser.open()
                ser.flushInput()
                serialOk = 1
                samplesfromstart = 0
                printMsg( "Serial restarted", '\n')
        except Exception as exc:
            handleStop(exc)
            printMsg("Could not reopen serial: " + str(exc))
            time.sleep(0.5)

        try:
            nowTime = time.gmtime()

            if serialOk == 1: 
                try:
                    serIn = ser.readline()
                    serParsed = serIn.decode("utf-8")
                    printMsg("Received [ " + str(serParsed).strip('\n').strip('\r') + "] ")
                    serParsed = serParsed.strip('\n\r').split()
                    for k in range(0, chanNo):
                        try:
                            measTemp =  float(serParsed[k])
                            if measTemp != errorCode and measTemp < tMax and measTemp > tMin :
                                meas[k] += measTemp
                                measNo[k] += 1
                        except Exception as exc:
                            handleStop(exc)
                            printMsg("Could not parse channel [" + str(k) + "]: " + str(exc))
                            pass
                    cnt += 1
                    lastTime = dt.datetime.now()
                except Exception as exc:
                    handleStop(exc)
                    printMsg("Could not parse serial: " + str(exc))

            if cnt == avgNo:
                #samplesfromstart += 1
                if samplesfromstart > samplesToDiscard:
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
                        timeTagLog = time.strftime(timeTagFormat, nowTime)
                        output.write( timeTagLog + separator + strOut[:-1] + '\n')
                else:
                    ser.flushInput()
                    samplesfromstart += 1
                meas = np.zeros(chanNo)
                measNo = np.zeros(chanNo)
                cnt = 0

        except Exception as exc:
            handleStop(exc)
            print()
            printMsg("-> Run interrupted: " +  str(exc))
            sys.exit(-1)



