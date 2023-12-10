import sys
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)
        self.textBrowser = QTextBrowser()
        self.setCentralWidget(self.textBrowser)

class PrintRedirect(object):
    def __init__(self, textBrowser):
        self.textBrowser = textBrowser

    def write(self, str):
        self.textBrowser.moveCursor(QTextCursor.End)
        self.textBrowser.insertPlainText(str)
        self.textBrowser.moveCursor(QTextCursor.End)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.stdout = PrintRedirect(main_window.textBrowser)
    main_window.show()
    print('123')
    sys.exit(app.exec_())