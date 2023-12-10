import sys
import typing

from PyQt5.QtCore import QObject
#设置单线程模式，防止qt5与pyautogui冲突
sys.coinit_flags = 2
import Ui_qt5design
import time
# 以下两个import会导致PyQt5报错:QWindowsContext: OleInitialize() failed:  "COM error 0xffffffff80010106 RPC_E_CHANGED_MODE (Unknown error 0x080010106)"
# 或pywinauto报错[WinError -2147417850] 无法在设置线程模式后对其加以更改。
from pywinauto.application import Application 
# 详情: https://blog.csdn.net/nicai_xiaoqinxi/article/details/100657271
import pyautogui
from win10toast import ToastNotifier
import threading
import logging
from io import StringIO
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic


played_list = []

cur_time,end_time = 0,0
loglevel = 'debug'
notify = True
n = 0
firstrun = True
echoflag = True



#-start----------------------主程序-----------------------
def executing_time(func):
    def inner():
        start = time.time()
        a,b = func()
        end = time.time()
        last = end-start
        logger.debug(executing_time.__name__ + str(func) + '执行时间: ' + str(round(last, 3)) + 's')
        return a,b
    return inner


@executing_time
def time_monitor():
    text = dlg['Document']     #目标控件(只要是print_control_identifiers()方法输出的控件就可直接访问)
    t = str(text.texts())      #控件文本

    middle_var = t.split(' ')
    end_time = middle_var[-26]
    cur_time = middle_var[-35]
    
    return cur_time,end_time

def time_manager():
    cur_time2,cur_time4 = 0,0

    cur_time0,end_time0 = time_monitor()        #独立变量防干扰
    minute = int(end_time0.split(':')[0])
    title = dlg.texts()                         #原曲名

    logger.info(time_manager.__name__ + '当前曲目:' + str(title)[2:-2].replace(r'\xa0', ' ') + '总时长: ' + end_time0)
    logger.info(time_manager.__name__ + '计数:' + str(len(played_list)))

    if minute >= 1:                                                 #时间超过一分钟，需要检测时间来切歌
        logger.info(time_manager.__name__ + '时长超过1min, 启用监测')
        while True:
            cur_time1,end_time1 = time_monitor()
            title1 = dlg.texts()                                    #当前曲名
            logger.debug(time_manager.__name__ + '当前时间: %s' % cur_time1)


            if title1 != title:
                logger.warning(time_manager.__name__ + '侦测到计划外的切歌')
                played_list.append(title)
                logger.warning(time_manager.__name__ + '结束当前循环...')
                break
            elif cur_time1 == cur_time2 and playflag == True:
                logger.warning(time_manager.__name__ + '侦测到计划外的停止, 再次播放...')
                pyautogui.hotkey('ctrl', 'alt', 'p')
            elif int(cur_time1.split(':')[0]) >= 1:
                played_list.append(title)
                logger.debug(time_manager.__name__ + '切歌...')
                pyautogui.hotkey('ctrl', 'alt', 'right')
                break
            cur_time2,end_time2 = time_monitor()
    else:
        logger.info(time_manager.__name__ + '时长不足1min, 禁用监测')
        while True:
            cur_time3,end_time3 = time_monitor()
            title2 = dlg.texts()
            if title2 != title:
                played_list.append(title)
                logger.debug(time_manager.__name__ + '较短的歌曲已播放结束, 结束当前循环...')
                break
            elif cur_time3 == cur_time4 and playflag == True:
                logger.warning(time_manager.__name__ + '侦测到计划外的停止, 再次播放...')
                pyautogui.hotkey('ctrl', 'alt', 'p')
            cur_time4,end_time4 = time_monitor()
            time.sleep(2)
#-end------------------主程序---------------------


#-start------------------------UI相关-----------------------
def pushButtonRunfunc():
    global runflag, firstrun
    logger.debug('恢复')
    runflag = True
    if firstrun == True:
        logger.info(pushButtonRunfunc.__name__ + ' 启动程序')
        run()
        firstrun = False
    ui.pushButtonRun.setDisabled(True)
    ui.pushButtonStop.setEnabled(True)
def pushButtonStop():
    global runflag
    logger.info(pushButtonStop.__name__ + ' 暂停程序')
    runflag = False
    ui.pushButtonStop.setDisabled(True)
    ui.pushButtonRun.setEnabled(True)
def Scountreader():
    global n
    ui.pushButtonRun.setEnabled(True)
    n = ui.horizontalSliderCount.value()
    ui.lineEditCount.setText(str(n))
    logger.debug(n)
def Lcountreader():
    global n
    ui.pushButtonRun.setEnabled(True)
    n = int(ui.lineEditCount.text())
    ui.horizontalSliderCount.setValue(n)
    logger.debug(n)
def loglevelreader():
    global loglevel
    loglevel = ui.comboBoxLoglevel.currentText()
    logger.debug(loglevel)
def notifyreader():
    global notify
    notify = ui.checkBoxIfNotify.isChecked()
    logger.debug(notify)

#-end------------------------UI相关-----------------------

 
if __name__ == '__main__':
    # 日志相关
    # 创建一个日志记录器
    logger = logging.getLogger(' ' + __name__ + ' ')
    logger.setLevel(logging.DEBUG)
    # 创建一个输出到字符串的处理器
    output = StringIO()
    handler = logging.StreamHandler(output)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # output_text = output.getvalue()
    #


    def run():
        global app
        global dlg
        #创建进程实例
        app = Application('uia').start(r'D:\Program Files\Netease\CloudMusic\cloudmusic.exe')
        logger.debug('进程实例已创建: %s' % app)
        #创建窗口实例
        dlg = app['Dialog']     
        time.sleep(5)           #等待窗口加载完成
        #dlg.print_control_identifiers()

        pyautogui.hotkey('ctrl', 'alt', 'p')

        for i in range(n):
            time_manager()

        pyautogui.hotkey('ctrl', 'alt', 'p')

        print(played_list)
        if notify == True:
            ToastNotifier().show_toast('notification', '程序运行完成', '.\\icon\\py.ico')

    def pause():
        global runflag, playflag, echoflag
        runflag = True
        while True:
            if runflag == True:
                time.sleep(0.1)
            else:
                playflag = False
                echoflag = False
                logger.info(pause.__name__ + ' 已暂停')

                pyautogui.hotkey('ctrl', 'alt', 'p')
                while runflag == False:
                    time.sleep(0.1)
                
                playflag = True
                echoflag = True
                logger.info(pause.__name__ + ' 已恢复')

                pyautogui.hotkey('ctrl', 'alt', 'p')
    
    thread1  =threading.Thread(target=pause)
    thread1.start()

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_qt5design.Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.pushButtonRun.setDisabled(True)
    ui.pushButtonStop.setDisabled(True)
    MainWindow.show()


    #绑定槽函数
    ui.pushButtonRun.clicked.connect(pushButtonRunfunc)
    ui.pushButtonStop.clicked.connect(pushButtonStop)
    ui.horizontalSliderCount.sliderMoved.connect(Scountreader)
    ui.lineEditCount.editingFinished.connect(Lcountreader)
    ui.comboBoxLoglevel.currentTextChanged.connect(loglevelreader)
    ui.checkBoxIfNotify.clicked.connect(notifyreader)

    app.exec_()
    thread1.join()