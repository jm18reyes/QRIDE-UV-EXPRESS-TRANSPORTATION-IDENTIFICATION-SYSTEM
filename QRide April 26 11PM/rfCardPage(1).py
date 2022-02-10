from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

import numpy as np


#from mfrc522 import SimpleMFRC522
#import RPi.GPIO as GPIO
#from gpiozero import Button, Buzzer

import cv2
import re
import csv
import time

import rfCard

class reader(QtWidgets.QMainWindow, rfCard.Ui_rfCard):
    def __init__(self):
        super(reader, self).__init__()
        self.setupUi(self)

        self.tap_btn.clicked.connect(self.tapCard)

        ID = ""
        text = ""

        #TODO self.reader = SimpleMFRC522()
        #TODO self.buzzer = Buzzer(26)


    def tapCard(self):
        reader.ID = self.id_blank.text()
        reader.text = self.text_blank.text()

    def read(self):
        return reader.ID, reader.text
        
        

    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = reader()
    form.show()
    sys.exit(app.exec_())