import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import Ui_untitled as UI



def loginfunc():
    username = ui.lineEdit.text()
    password = ui.lineEdit_2.text()

    if username == 'zch' and password == '123456':
        print('success')
    else:
        print('failed')

def cancelfunc():
    MainWindow.close()

 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UI.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    ui.login.clicked.connect(loginfunc)
    ui.cancel.clicked.connect(cancelfunc)

    sys.exit(app.exec_())