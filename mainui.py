import sys
import myUI
import time
# 以下两个import会导致PyQt5报错:QWindowsContext: OleInitialize() failed:  "COM error 0xffffffff80010106 RPC_E_CHANGED_MODE (Unknown error 0x080010106)"
# 或pywinauto报错[WinError -2147417850] 无法在设置线程模式后对其加以更改。
# from pywinauto.application import Application 
# 详情: https://blog.csdn.net/nicai_xiaoqinxi/article/details/100657271
from PyQt5 import QtCore, QtGui, QtWidgets
import pyautogui
from win10toast import ToastNotifier
import threading
import logging


played_list = []
cur_time,end_time = 0,0
loglevel = 'debug'
notify = True
n = 0
firstrun = True

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
                logger.warn(time_manager.__name__ + '侦测到计划外的切歌')
                played_list.append(title)
                logger.warn(time_manager.__name__ + '结束当前循环...')
                break
            elif cur_time1 == cur_time2:
                logger.warn(time_manager.__name__ + '侦测到计划外的停止, 再次播放...')
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
            elif cur_time3 == cur_time4:
                logger.warn(time_manager.__name__ + '侦测到计划外的停止, 再次播放...')
                pyautogui.hotkey('ctrl', 'alt', 'p')
            cur_time4,end_time4 = time_monitor()
            time.sleep(2)
#-end------------------主程序---------------------


#-start------------------------UI相关-----------------------
def pushButtonRunfunc():
    global runflag
    logger.debug('运行')
    runflag = True
    if firstrun == True:
        t1.start()

def pushButtonStop():
    global runflag
    logger.debug('暂停')
    runflag = False

def Scountreader():
    n = ui.horizontalSliderCount.value()
    ui.lineEditCount.setText(str(n))
    logger.debug(n)
def Lcountreader():
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
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = myUI.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()


    #日志相关
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()    #输出到控制台

    logger.addHandler(console_handler)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    #

    ui.pushButtonRun.clicked.connect(pushButtonRunfunc)
    ui.pushButtonStop.clicked.connect(pushButtonStop)
    ui.horizontalSliderCount.sliderMoved.connect(Scountreader)
    ui.lineEditCount.editingFinished.connect(Lcountreader)
    ui.comboBoxLoglevel.currentTextChanged.connect(loglevelreader)
    ui.checkBoxIfNotify.clicked.connect(notifyreader)

    
    def threadrun():
        global app
        global dlg
        
        #详见开头段代码
        from pywinauto.application import Application
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
    def locker():
        global runflag
        runflag = True
        while True:
            if runflag == True:
                time.sleep(0.1)
            else:
                lock.acquire()
                logger.info('线程已暂停')
                while runflag == False:
                    time.sleep(0.1)
                lock.release()
                logger.info('线程已恢复')
    
    lock = threading.Lock()
    t1 = threading.Thread(target = threadrun)
    t2 = threading.Thread(target = locker)

    t2.start()
    
    
    print(played_list)
    if notify == True:
        ToastNotifier().show_toast('notification', '程序运行完成', '.\\icon\\py.ico')


    sys.exit(app.exec_())



    