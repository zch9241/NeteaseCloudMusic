# -*- coding: utf-8 -*-
# <NeteaseCloudMusic> Copyright (C) <2023>  <zch9241>
# 
# Author: zch9241 <github.com/zch9241><zch2426936965@gmail.com>
# 
# GNU GENERAL PUBLIC LICENSE Version 3
# 
# version: 1.6
# 
# 版本更新说明：
# v1.0 程序首个版本
# v1.1 优化使用体验（不激活窗口）
# v1.2 程序自动化，便于使用任务计划程序。须在命令行下使用autorun_main.py + 运行次数 方可使用
# v1.3 优化使用体验：1.多次登录时任务照常进行；2.status.json中增加了运行统计；3.任务完成后自动关闭云音乐
#      增加了log的一些细节并更改了log保存位置
# v1.3.1 修改了程序运行次数判定，增加程序运行结束时的通知
# v1.4 增加了登录判断功能（可选）:1.使用OCR, 访问ocr.space获取apikey；
#                               2.屏幕缩放比
#                               填写至<class> OCR <func>__init__函数中相应位置
#      运行参数调整: autorun_main.py [num] [ocr]
#              （example: autorun.py 310 True   #循环310次，使用OCR）
# v1.5.alpha 程序的重构版本（基于pywinauto），减少冗余代码、功能和外部程序调用
#            更改ln102你的cloudmusic程序路径和ln112循环次数即可使用
# v1.6 增加UI功能
# 
# 


# 该module会导致报错，忽略即可
# WNDPROC return value cannot be converted to LRESULT
# TypeError: WPARAM is simple, so must be an int object (got NoneType)
from win10toast import ToastNotifier
# 

# 以下两个import会导致PyQt5报错:QWindowsContext: OleInitialize() failed:  "COM error 0xffffffff80010106 RPC_E_CHANGED_MODE (Unknown error 0x080010106)"
# 或pywinauto报错[WinError -2147417850] 无法在设置线程模式后对其加以更改。
# 详情: https://www.cnpython.com/qa/628847
#设置单线程(STA)模式，防止pyqt5与pywinauto冲突
import sys
sys.coinit_flags = 2
import pywinauto
from pywinauto.application import Application
# 

from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt5.QtWidgets import *

import time
import logging
import pyautogui
from io import StringIO
from functools import wraps


import Ui_qt5design



class Threadstatus(QThread):
    status = pyqtSignal(list)
    def __init__(self, thread_: QThread):
        super().__init__()
        self.thread_ = thread_
    def run(self):
        while True:
            lst = [self.thread_.objectName, self.thread_.isRunning()]
            self.status.emit(lst)
            time.sleep(0.1)



class RunThread(QThread):
    #设置信号
    output_ = pyqtSignal(str)
    terminate_ = pyqtSignal(bool)
    def __init__(self) -> None:        
        super().__init__()
    

    def output_emit_util(self):
        ## 每次调用都重置output
        # 创建一个输出到字符串的处理器
        global output_t1, handler_t1, formatter_t1, logger
        output_t1 = StringIO()
        handler_t1 = logging.StreamHandler(output_t1)
        handler_t1.setLevel(logging.DEBUG)
        formatter_t1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler_t1.setFormatter(formatter_t1)
        #
        logger.addHandler(handler_t1)

    def output_emit(self):
        '''
        将RunThread的log输出至窗口
        '''
        output_text_t1 = output_t1.getvalue()
        self.output_.emit(output_text_t1)

    #覆写run方法
    def run(self):
        #创建进程实例
        global app_t1, dlg_t1, n, played_list
        played_list = []
        app_t1 = Application('uia').start(r'D:\Program Files\Netease\CloudMusic\cloudmusic.exe')
        self.output_emit_util()
        logger.debug('进程实例已创建: %s' % app_t1)
        self.output_emit()
        #创建窗口实例
        dlg_t1 = app_t1['Dialog']     
        time.sleep(5)           #等待窗口加载完成
        #dlg.print_control_identifiers()

        pyautogui.hotkey('ctrl', 'alt', 'p')

        for i in range(n):
            self.time_manager()

        pyautogui.hotkey('ctrl', 'alt', 'p')

        #print(played_list)
        if notifyflag == True:
            ToastNotifier().show_toast('notification', '程序运行完成', '.\\icon\\py.ico')



    def executing_time(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            start = time.time()
            a,b = func(self, *args, **kwargs)
            end = time.time()
            last = end-start
            self.output_emit_util()
            logger.debug(
                self.executing_time.__name__ + str(func) 
                + '执行时间: ' + str(round(last, 3)) + 's'
                )
            self.output_emit()
            return a,b
        return inner


    @executing_time
    def time_monitor(self):
        global text, dlg_t1
        text = dlg_t1['Document']     #目标控件(只要是print_control_identifiers()方法输出的控件就可直接访问)
        try:
            t = str(text.texts())      #控件文本
            middle_var = t.split(' ')
            end_time = middle_var[-26]
            cur_time = middle_var[-35]
            return cur_time, end_time
        except pywinauto.findwindows.ElementNotFoundError as e:
            self.output_emit_util()
            logger.fatal(self.time_monitor.__name__ + ' ' + str(e))
            self.output_emit()
            
            self.output_emit_util()
            logger.info(self.time_monitor.__name__ + ' 请重新运行本程序')
            self.output_emit()

            self.terminate_.emit(True)

            ToastNotifier().show_toast('出现了错误', '请重新运行本程序 \n' + e, '.\\icon\\py.ico')



    def time_manager(self):
        global cur_time0, cur_time1, cur_time2, cur_time3, cur_time4
        global end_time0, end_time1, end_time2, end_time3, end_time4
        global played_list, title_t1, playflag
        cur_time2,cur_time4 = 0,0

        cur_time0,end_time0 = self.time_monitor()        #独立变量防干扰
        minute = int(end_time0.split(':')[0])
        title_t1 = dlg_t1.texts()                         #原曲名

        self.output_emit_util()
        logger.info(self.time_manager.__name__ +
                         ' 当前曲目:' + str(title_t1)[2:-2].replace(r'\xa0', ' ') + 
                         ' 总时长: ' + end_time0)
        self.output_emit()
        
        self.output_emit_util()
        logger.info(self.time_manager.__name__ + 
                         ' 计数:' + str(len(played_list)))
        self.output_emit()

        if minute >= 1:                                                 #时间超过一分钟，需要检测时间来切歌
            self.output_emit_util()
            logger.info(self.time_manager.__name__ + ' 时长超过1min, 启用监测')
            self.output_emit()
            while True:
                cur_time1,end_time1 = self.time_monitor()
                title1 = dlg_t1.texts()                                    #当前曲名
                
                self.output_emit_util()
                logger.debug(self.time_manager.__name__ + ' 当前时间: %s' % cur_time1)
                self.output_emit()


                if title1 != title_t1:
                    self.output_emit_util()
                    logger.warning(self.time_manager.__name__ + ' 侦测到计划外的切歌')
                    self.output_emit()

                    played_list.append(title_t1)
                    
                    self.output_emit_util()
                    logger.warning(self.time_manager.__name__ + ' 结束当前循环...')
                    self.output_emit()
                    
                    break
                elif cur_time1 == cur_time2 and playflag == True:
                    self.output_emit_util()
                    logger.warning(self.time_manager.__name__ + ' 侦测到计划外的停止, 再次播放...')
                    self.output_emit()
                    
                    pyautogui.hotkey('ctrl', 'alt', 'p')
                elif int(cur_time1.split(':')[0]) >= 1:
                    played_list.append(title_t1)
                    
                    self.output_emit_util()
                    logger.debug(self.time_manager.__name__ + ' 切歌...')
                    self.output_emit()
                    
                    pyautogui.hotkey('ctrl', 'alt', 'right')
                    break
                cur_time2,end_time2 = self.time_monitor()
        else:
            self.output_emit_util()
            logger.info(self.time_manager.__name__ + ' 时长不足1min, 禁用监测')
            self.output_emit()
            
            while True:
                cur_time3,end_time3 = self.time_monitor()
                title2 = dlg_t1.texts()
                if title2 != title_t1:
                    played_list.append(title_t1)
                    
                    self.output_emit_util()
                    logger.debug(self.time_manager.__name__ + ' 较短的歌曲已播放结束, 结束当前循环...')
                    self.output_emit()
                    
                    break
                elif cur_time3 == cur_time4 and playflag == True:
                    self.output_emit_util()
                    logger.warning(self.time_manager.__name__ + ' 侦测到计划外的停止, 再次播放...')
                    self.output_emit()
                    
                    pyautogui.hotkey('ctrl', 'alt', 'p')
                cur_time4,end_time4 = self.time_monitor()
                time.sleep(2)



class MainWin(QWidget):
    def __init__(self):
        super().__init__()
        self.init_var()
        self.init_logger()
        self.init_ui()
    
    def init_var(self):
        global cur_time, end_time, n, firstrun, playflag, echoflag, notifyflag, played_list
        cur_time, end_time = 0,0
        n = 0
        firstrun = True
        playflag = True
        echoflag = True
        notifyflag = True
        played_list = []

    
    def init_logger(self):
        '''
        日志相关
        '''
        global logger, formatter
        # 创建一个日志记录器
        logger = logging.getLogger(' ' + __name__ + ' ')
        logger.setLevel(logging.DEBUG)
        #
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler_ = logging.StreamHandler()
        handler_.setFormatter(formatter)
        
        logger.addHandler(handler_)

    def init_ui(self):
        '''
        UI初始化设置
        '''
        global ui, window
        ui = Ui_qt5design.Ui_MainWindow()
        window = QMainWindow()
        ui.setupUi(window)

        #信号绑定槽函数
        ui.pushButtonRun.clicked.connect(self.pushButtonRun)
        ui.pushButtonStop.clicked.connect(self.pushButtonStop)
        ui.horizontalSliderCount.sliderMoved.connect(self.Scountreader)
        ui.lineEditCount.editingFinished.connect(self.Lcountreader)
        ui.checkBoxIfNotify.clicked.connect(self.CheckboxNotifyreader)
        



    def output_to_window(self, text):
        '''
        打印输出(更新窗口文本)
        '''
        if echoflag == True:
            originaltext = ui.textBrowserLogger.toPlainText()

            ui.textBrowserLogger.setText(originaltext + text)
    
    
    def outputter_util(self):
        '''
        先调用util创建handler,执行完.log()语句后再调用outputter---可用装饰器，但太麻烦
        '''
        ## 每次调用都重置output
        # 创建一个输出到字符串的处理器
        global output, logger, formatter
        output = StringIO()
        handler_ = logging.StreamHandler(output)
        handler_.setFormatter(formatter)
        logger.addHandler(handler_)
    def outputter(self):
        '''
        将MainWin的log输出至窗口
        '''
        output_text = output.getvalue()
        self.output_to_window(output_text)
    
    def outputter2(self, text):
        '''
        接受RunThread的singal(output_)并将其log输出至窗口
        '''
        self.output_to_window(text)
    
    def outputter3(self, status:list):
        '''
        接受Threadstatus的singal并将其输出至窗口
        '''
        ui.threadradioButton.setChecked(status[1])
        ui.threadradioButton.setText(str(status[0]).split(' ')[4])

    #--------------------------------------RunThread()相关--------
    def run_thread(self):
        '''
        RunThread子线程启动入口
        '''
        self.thread = RunThread()
        #启动线程
        logger.info(self.run_thread.__name__, ' 启动子线程...')
        self.thread.start()
        self.thread.setObjectName('RunThread')

        #绑定子线程类中的信号
        self.thread.output_.connect(self.outputter2)
        self.thread.terminate_.connect(self.terminate_)

    def pause(self):
        global cur_time, end_time, n, firstrun, playflag, runflag, echoflag, played_list
        runflag = True
        while True:
            if runflag == True:
                time.sleep(0.1)
            else:
                playflag = False
                
                self.outputter_util()
                logger.info(self.pause.__name__ + ' 已暂停 \n')
                self.outputter()

                pyautogui.hotkey('ctrl', 'alt', 'p')
                while runflag == False:
                    time.sleep(0.1)
                
                playflag = True
                echoflag = True
                
                self.outputter_util()
                logger.info(self.pause.__name__ + ' 已恢复 \n')
                self.outputter()

                pyautogui.hotkey('ctrl', 'alt', 'p')

    def terminate_(self, flag):
        if flag == True:
            self.thread.terminate()
    #--------------------------------------RunThread()相关--------
    
    def thread_status(self, threadname):
        '''
        Threadstatus子线程启动入口
        '''
        self.thread1 = Threadstatus(thread_ = self.thread)
        self.thread1.start()

        self.thread1.status.connect(self.outputter3)


    #---------------------------槽函数----
    def pushButtonRun(self):
        global runflag, firstrun

        runflag = True
        if firstrun == True:
            logger.info(self.pushButtonRun.__name__ + ' 启动程序 \n')
            self.run_thread()
            self.thread_status(threadname = 'RunThread')
            firstrun = False
        else:
            self.outputter_util()
            logger.debug('恢复...')
            self.outputter()
        
        ui.pushButtonRun.setDisabled(True)
        ui.pushButtonStop.setEnabled(True)
    def pushButtonStop(self):
        global runflag
        self.outputter_util()
        logger.info(self.pushButtonStop.__name__ + ' 暂停程序 \n')
        self.outputter()

        runflag = False
        ui.pushButtonStop.setDisabled(True)
        ui.pushButtonRun.setEnabled(True)
    def Scountreader(self):
        global n
        ui.pushButtonRun.setEnabled(True)
        n = ui.horizontalSliderCount.value()
        ui.lineEditCount.setText(str(n))
        
        self.outputter_util()
        logger.debug(n)
        self.outputter()
    def Lcountreader(self):
        global n
        ui.pushButtonRun.setEnabled(True)
        try:
            n = int(ui.lineEditCount.text())
            ui.horizontalSliderCount.setValue(n)
            self.outputter_util()
            logger.debug(n)
            self.outputter()
        except ValueError:
            self.outputter_util()
            logger.warn(self.Lcountreader.__name__, " 输入的值有误 value = " + ui.lineEditCount.text())
            self.outputter()
    def CheckboxNotifyreader(self):
        global notifyflag
        notifyflag = ui.checkBoxIfNotify.isChecked()
        self.outputter_util()
        logger.debug('notify = ' + str(notifyflag))

    #---------------------------槽函数----


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwin = MainWin()
    #window: global var from MainWin().init_ui()
    window.show()
    sys.exit(app.exec_())

    