from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

import os

from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
from gpiozero import Button, Buzzer

import cv2
import re
import csv
import time

import newRFWin

import App

class Main(QtWidgets.QMainWindow, newRFWin.Ui_rfWin):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)

        self.writeRF_btn.clicked.connect(self.writeToCard)
        self.pushButton.clicked.connect(self.backToMain)

      

        self.reader = SimpleMFRC522()
        self.buzzer = Buzzer(18)

    def writeToCard(self):
        if(self.nameRF_blank.text() is not "" and self.plateRF_blank.text() is not "" and self.codRF_blank.text() is not "" and self.contactRF_blank.text() is not ""):

            self.driverInfo = str(self.nameRF_blank.text())+","+str(self.contactRF_blank.text())+","+str(self.plateRF_blank.text())+","+str(self.codRF_blank.text())

            print(self.driverInfo)

            


            self.reader.write(self.driverInfo)
            self.buzzer.beep(0.1, 0.1, 1)

            print("Written")
        else:
            self.statusRF_lbl.setText("All Fields are Required!!!")
    
    def backToMain(self):
        #self.newWin = App.Main()
        #self.newWin.show()
        Main.close(self)
        os.system("sudo python3.7 /home/pi/Desktop/QRide-v5/App.py")

    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = Main()
    form.show()
    sys.exit(app.exec_())