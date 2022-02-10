from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import os

import numpy as np

import qrcode
from resizeimage import resizeimage

import cv2
import re
import csv
import time

import newQRWin
import newRFPage
import App

import cups

class Qr_Generator(QtWidgets.QMainWindow, newQRWin.Ui_AddNewPassenger):

    imgPath =""

    def __init__(self):
        super(Qr_Generator, self).__init__()
        self.setupUi(self)

        self.btn_driver.clicked.connect(self.showDriverPage) #Calls the function showDriverPage when btn_driver is clicked
        self.back_btn.clicked.connect(self.backToMain)          #Calls the function backToMain when back_btn is clicked
        self.btn_print.clicked.connect(self.print)              #Calls the function print when btn_print is clicked
        self.btn_clear.clicked.connect(self.clearFields)        #Calls the function clearFields when btn_clear is clicked
        self.btn_generate.clicked.connect(self.generateQR)      #Calls the function generateQR when btn_generate is clicked


    def showDriverPage(self):
        self.newWin = newRFPage.Main()
        self.newWin.show()
        self.close()


    def generateQR(self):
        if(self.txt_name_code.text()=='' or self.txt_age.text()=='' or self.txt_number.text()=='' or self.txt_address.text()==''):
            self.msg='All Fields are Required!!!'
            self.lbl_msg.setText(str(self.msg))
        else:
            qr_data=(f"{self.txt_name_code.text()}, {self.txt_age.text()}, {self.txt_number.text()}, {self.txt_address.text()}")
            qr_code=qrcode.make(qr_data)
            qr_code=resizeimage.resize_cover(qr_code,[180,180])
            Qr_Generator.imgPath = "Passenger_QR/Pas_"+str(self.txt_name_code.text())+'.png'
            qr_code.save(Qr_Generator.imgPath)
            Pic = QPixmap(str(os.getcwd()+"/"+str(Qr_Generator.imgPath))) #Get current working directory plus the path of the img file
            self.qr_code_img.setPixmap(Pic)                  #Gets the generated png 
            self.qr_code_img.setScaledContents(True)        #shows it on the qr_code_img label on ui
            self.msg='QR Generated Successfully!!!'
            self.lbl_msg.setText(str(self.msg))

    def clearFields(self):
        self.txt_name_code.setText("")
        self.txt_age.setText("")
        self.txt_number.setText("")
        self.txt_address.setText("")
        self.lbl_msg.setText("")
        self.blank = QPixmap(str(os.getcwd()+"/"+"blank.png"))
        self.qr_code_img.setPixmap(self.blank)              #Gets the blank.png 
        self.qr_code_img.setScaledContents(True)            #shows it on the qr_code_img label on ui
        
    def print(self):
        file_path = (str(os.getcwd())+"/"+str(Qr_Generator.imgPath))
        conn = cups.Connection()
        #printers = conn.getPrinters()
        #print(printers)
        #printer_name = printers.keys()[0]
        conn.printFile('EPSON-L120-Series',file_path,"",{})

    def backToMain(self):
        #self.newWin = App.Main()
        #self.newWin.show()
        self.close()    #Just closes this window
        os.system("sudo python3.7 /home/pi/Desktop/QRide-v5/App.py")
        
        

    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = Qr_Generator()
    form.show()
    sys.exit(app.exec_())