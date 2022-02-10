import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QApplication, QSplashScreen 
from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore    import QTimer, Qt

import App

class Dialog(QDialog):
    def __init__(self):
        super(Dialog, self).__init__()


        self.splash = QSplashScreen(QPixmap('logo.png'))
        self.splash.setWindowFlags(Qt.FramelessWindowHint)

        # By default, SplashScreen will be in the center of the screen.
        # You can move it to a specific location if you want:
        # self.splash.move(10,10)

        self.splash.show()

        # Close SplashScreen after 2 seconds (2000 ms)
        QTimer.singleShot(2000, self.splash.close)

        self.newWindow = App.Main()
        QTimer.singleShot(2000, self.newWindow.show)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Dialog()
    sys.exit(app.exec_())