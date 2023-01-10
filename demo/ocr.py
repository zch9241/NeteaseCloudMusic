#修改了python目录Lib\site-packages\pytesseract\pytesseract.py中tesseract_cmd变量的值

import sys
import time
import pytesseract
import win32con
import win32gui
from PIL import Image
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication

classname = 'OrpheusBrowserHost'
hwnd = win32gui.FindWindow(classname, None)

win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)



app = QApplication(sys.argv)
screen = QApplication.primaryScreen()
screen.grabWindow(hwnd).toImage().save("screenshot.jpg")
#1920*1020
box = (1425,0,1500,75)
img = Image.open('screenshot.jpg')

rect = img.crop(box)

result_image = Image.new('RGB', (75,75), (0,0,0,0)) #mode, result size, color
result_image.paste(rect, (0,0), mask=0)
result_image.save('test.jpg')
time.sleep(1)
text = pytesseract.image_to_string(Image.open('C:\\Users\\Lenovo\\Desktop\\__MyCode\\NeteaseCloudMusic\\v1.3.1\\test.jpg'),lang="chi_sim")  
print(text)
