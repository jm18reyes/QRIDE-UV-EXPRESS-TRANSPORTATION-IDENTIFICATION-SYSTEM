from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import csv 
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os

import time
from datetime import date

import home

import newQRPage

from gpiozero import LED, Button, Buzzer
from mfrc522 import SimpleMFRC522

import serial
import re

class Main(QtWidgets.QMainWindow, home.Ui_MainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)

        self.buzzer = Buzzer(26)
        self.led = LED(19)

        self.pushButton.clicked.connect(self.addNewPassengerPage)

        self.Worker1 = qrThread()     #Creates an object of qrThread class named Worker1

        self.Worker1.start()            #Starts the Worker1 to simultaneously run with Main class
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)    #When Worker1 receives ImageUpdate signal from qrThread, starts ImageUpdateSlot function
        self.Worker1.buzzSound.connect(self.ringBuzzer)
        self.Worker1.switchLED.connect(self.toggleLED)


        self.Worker2 = rfidThread()   #Creates an object of rfidThread class named Worker2
        self.Worker2.start()            #Starts the Worker2 to simultaneously run with Main class and Worker1
        self.Worker2.rfidSuccess.connect(self.updateRFLbl)   #When Worker2 receives rfidSuccess signal from rfidThread, starts updateRFLbl
        self.Worker2.buzzSound.connect(self.ringBuzzer)
        self.Worker2.switchLED.connect(self.toggleLED)


    
        self.timer = QTimer()           #creates object timer from QTimer class. 
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)   #This is utilized to update time in the gui per second

    #This function updates rfStat_lbl whenever it detects an rfid Card
    def updateRFLbl(self,stat,name):
        self.rfStat_lbl.setText(" ")
        if(stat == 1):
            self.rfStat_lbl.setText("DRIVER: "+str(name)+" - LOGGED IN!")
            
        else:
            self.rfStat_lbl.setText(name)
            QTimer.singleShot(2000,self.resetRFLbl)   #Waits 2 seconds before it restores the original text


    

    def resetRFLbl(self):
        self.rfStat_lbl.setText("DRIVER? SCAN your RFID BELOW")


    #Shows the UI for the create QR
    def addNewPassengerPage(self):
        #self.newWin = newQRPage.Qr_Generator()
        self.Worker1.stop()
        self.Worker2.stop()
        Main.close(self)
        #self.newWin.show()
        os.system("sudo python3.7 /home/pi/Desktop/QRide-v5/newQRPage.py")

    #This function continously updates the camera_lbl by using the Image signal from qrThread.
    #This function also shows if the qr is detected 
    def ImageUpdateSlot(self, Image, state,tempState):
        if(state == "None"):
            self.camera_lbl.setPixmap(QPixmap.fromImage(Image))
        else:
            self.camera_lbl.setText(str("Hi! "+state)+"-LOGGED IN\n"+str(tempState))

            

    #This function is used to stops the qrThread Thread
    def CancelFeed(self):
        self.Worker1.stop()


    #This function updates the time_lbl and date_lbl in the main menu
    def updateTime(self):
        self.currentTime = QTime.currentTime()
        self.now = QDate.currentDate()
        self.strNow = self.now.toString(Qt.ISODate)
        self.strTime = self.currentTime.toString("hh:mm")
        self.time_lbl.setText(self.strTime)
        self.date_lbl.setText(self.strNow)

    #This function is called when closing the program
    def closeEvent(self,event):
        print("Program Ended")
        self.Worker1.stop()
        self.Worker2.stop()

    def forceClose(self):
        self.Worker1.stop()
        self.Worker2.stop()
        self.close()

    def ringBuzzer(self,onTime,offTime,num):
        self.buzzer.beep(onTime,offTime,num)

    def toggleLED(self,state):
        if(state):
            self.led.toggle()

class rfidThread(QThread):
    rfidSuccess = pyqtSignal(int,str)
    buzzSound = pyqtSignal(float,float,int)
    switchLED = pyqtSignal(int)
    state = True

    
    #Whenever Worker2 starts, run function is first to be called
    def run(self):
        self.ThreadActive = True
        text = ""  #kunwari may naread na rfid

        temp = ""

        self.reader = SimpleMFRC522()

        while self.ThreadActive:

            ID, text = self.reader.read()

            #TODO rfidThread.buzzer.beep(0.1, 0.1, 1)

            self.buzzSound.emit(0.1,0.1,1)

            if text is not "" and text is not None:
                textList = text.split(",")
                if(len(textList) == 4):
                    print(textList)
                    self.rfidSuccess.emit(1,str(textList[0])) #Produces a signal in which the Main class will receive an Int Value example: (1)
                    QThread.sleep(1)
                    self.rfidSuccess.emit(2,"Scanning Temperature..")
                    
                    temp = self.scanTemp()
                    QThread.sleep(1)
                    self.rfidSuccess.emit(2,str("Temperature: "+temp))
                    textList.append(temp)
                    self.saveToCsv(textList)
                    QThread.sleep(2)



    def saveToCsv(self,Info):
        

        self.current_time = time.strftime("%H:%M:%S")
        self.today = date.today()


        #TODO rfidThread.buzzer.beep(0.1, 0.1, 2)
        self.buzzSound.emit(0.1,0.1,2)

        with open('Driver.csv', 'a') as csvfile:
            fieldNames = ['NAME', 'CONTACT NUMBER', 'PLATE NUMBER', 'CODING DAY' , 'TIME', 'DATE', 'TEMPERATURE']
            writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
            writer.writerow({'NAME': Info[0],'CONTACT NUMBER': Info[1], 'PLATE NUMBER': Info[2], 'CODING DAY': Info[3], 'TIME': self.current_time, 'DATE': self.today, 'TEMPERATURE': Info[4]})


    def scanTemp(self):
        print("Nandito na")
        port = "/dev/ttyUSB0"
        #port = '/dev/ttyUSB0'
        baud = 115200

        ser = serial.Serial(port, baud, timeout=1)
        ser.flushInput()

        tryScanning = True
        count = 0

        while(tryScanning):
            line = ser.readline()
            line = line.decode('UTF-8','ignore')
            split_line = line.splitlines()

            try:
                for item in split_line:
                    if("T body" in item):
                        count += 1
                        if(count == 2):
                            temp = item.split(" ")


                            temp = str(temp[3])
                            print("Temperature: "+temp)
                            tryScanning = False
            except:
                print("Waiting")

            
        print("Paexit na")
        return temp

    #This function deactivate the Thread
    def stop(self):
        self.ThreadActive = False
        self.quit()

    


class qrThread(QThread):
    ImageUpdate = pyqtSignal(QImage,str,str)
    buzzSound = pyqtSignal(float,float,int)
    switchLED = pyqtSignal(int)
    userScanned = False
    oldData = ""
    newData = ""

    #Whenever Worker1 starts, run function is first to be called
    def run(self):
        self.ThreadActive = True

        port = "/dev/ttyUSB0"
        baud = 115200

        Capture = cv2.VideoCapture("/dev/video0")
        detector = cv2.QRCodeDetector()
        serVar = serial.Serial(port, baud, timeout=1)
        serVar.flushInput()
        item = ""

        while self.ThreadActive:
            #TODO qrThread.led.toggle()

            self.switchLED.emit(1)
            ret, frame = Capture.read()
            if ret:
            	data, bbox, _ = detector.detectAndDecode(frame)
            	print(data)
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(460, 280, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic,"None","None")     #Produces a signal in which the Main class will receive and Image and an Int Value example: (Pic,0)
                if bbox is not None:
                    for i in range(len(bbox)):
                        cv2.line(frame, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,0, 0), thickness=2)
                        #cv2.putText(frame, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    if data:
                        self.buzzSound.emit(0.1, 0.1, 1)
                        dataList = data.split(",")



                               #save to csv
                        self.ImageUpdate.emit(Pic,str(dataList[0]),"\n \nScanning Temperature..") #Produces a signal in which the Main class will receive and Image and an Int Value example: (Pic,1)
                        temperature = self.scanTemp()

                        dataList.append(temperature)
                            
                        self.saveToCSV(dataList) 
                        self.ImageUpdate.emit(Pic,str(dataList[0]),str("\nTemperature: "+temperature))
                        Capture.release()
                        QThread.sleep(3)
                        Capture = cv2.VideoCapture(0)



                            
    
    
    def saveToCSV(self,Info):
        self.current_time = time.strftime("%H:%M:%S")
        self.today = date.today()
        #TODO qrThread.buzzer.beep(0.1, 0.1, 2)

        self.buzzSound.emit(0.1, 0.1, 2)
        with open('Passenger.csv', 'a') as csvfile:
            fieldNames = ['NAME', 'AGE', 'ADDRESS' , 'CONTACT NUMBER' , 'TIME', 'DATE','TEMPERATURE']
            writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
            writer.writerow({'NAME': Info[0], 'AGE': Info[1], 'ADDRESS': Info[2], 'CONTACT NUMBER': Info[3], 'TIME': self.current_time, 'DATE': self.today, 'TEMPERATURE': Info[4]})
        #TODO qrThread.led.toggle()

        self.switchLED.emit(1)

    def scanTemp(self):
        port = "/dev/ttyUSB0"
        #port = '/dev/ttyUSB0'
        baud = 115200

        ser = serial.Serial(port, baud, timeout=1)
        ser.flushInput()

        tryScanning = True
        count = 0

        while(tryScanning):
            line = ser.readline()
            line = line.decode('UTF-8','ignore')
            split_line = line.splitlines()

            try:
                for item in split_line:
                    if("T body" in item):
                        count += 1
                        if(count == 2):
                            temp = item.split(" ")


                temp = str(temp[3])
                print("Temperature: "+temp)
                tryScanning = False
            except:
                print("Waiting")

            

        return temp



    def stop(self):
        self.ThreadActive = False
        cv2.destroyAllWindows()
        self.quit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = Main()
    form.show()
    sys.exit(app.exec_())