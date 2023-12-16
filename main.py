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

import time
from win10toast import ToastNotifier
import logging
import pyautogui
from io import StringIO
from functools import wraps

# 以下两个import会导致PyQt5报错:QWindowsContext: OleInitialize() failed:  "COM error 0xffffffff80010106 RPC_E_CHANGED_MODE (Unknown error 0x080010106)"
# 或pywinauto报错[WinError -2147417850] 无法在设置线程模式后对其加以更改。
# 详情: https://www.cnpython.com/qa/628847
#设置单线程(STA)模式，防止pyqt5与pywinauto冲突
import sys
sys.coinit_flags = 2
from pywinauto.application import Application 
# 

from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow

import Ui_qt5design






class RunThread(QThread):
    #设置信号
    output_ = pyqtSignal(str)
    
    def __init__(self, logger: logging.Logger,
                  cur_time , end_time, 
                  n, firstrun, played_list, 
                  playflag
                    ) -> None:
        
        #获取父类的变量
        self.logger = logger
        self.cur_time, self.end_time = cur_time,end_time
        self.n = n
        self.firstrun = firstrun
        self.playflag = playflag
        #
        self.played_list = played_list
        
        super().__init__()
    

    def output_emit_util(self):
        ## 每次调用都重置output
        # 创建一个输出到字符串的处理器
        self.output = StringIO()
        self.handler = logging.StreamHandler(self.output)
        self.handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

    def output_emit(self):
        '''
        将RunThread的log输出至窗口
        '''
        output_text = self.output.getvalue()
        self.output_.emit(output_text)

    #覆写run方法
    def run(self):
        #创建进程实例
        self.app = Application('uia').start(r'D:\Program Files\Netease\CloudMusic\cloudmusic.exe')
        self.output_emit_util()
        self.logger.debug('进程实例已创建: %s' % self.app)
        self.output_emit()
        #创建窗口实例
        self.dlg = self.app['Dialog']     
        time.sleep(5)           #等待窗口加载完成
        #dlg.print_control_identifiers()

        pyautogui.hotkey('ctrl', 'alt', 'p')

        for i in range(self.n):
            self.time_manager()

        pyautogui.hotkey('ctrl', 'alt', 'p')

        #print(played_list)

        ToastNotifier().show_toast('notification', '程序运行完成', '.\\icon\\py.ico')



    def executing_time(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            start = time.time()
            a,b = func(self, *args, **kwargs)
            end = time.time()
            last = end-start
            self.output_emit_util()
            self.logger.debug(
                self.executing_time.__name__ + str(func) 
                + '执行时间: ' + str(round(last, 3)) + 's'
                )
            self.output_emit()
            return a,b
        return inner


    @executing_time
    def time_monitor(self):
        self.text = self.dlg['Document']     #目标控件(只要是print_control_identifiers()方法输出的控件就可直接访问)
        self.t = str(self.text.texts())      #控件文本

        self.middle_var = self.t.split(' ')
        self.end_time = self.middle_var[-26]
        self.cur_time = self.middle_var[-35]

        return self.cur_time,self.end_time

    def time_manager(self):
        self.cur_time2,self.cur_time4 = 0,0

        self.cur_time0,self.end_time0 = self.time_monitor()        #独立变量防干扰
        self.minute = int(self.end_time0.split(':')[0])
        self.title = self.dlg.texts()                         #原曲名

        self.output_emit_util()
        self.logger.info(self.time_manager.__name__ +
                         '当前曲目:' + str(self.title)[2:-2].replace(r'\xa0', ' ') + 
                         '总时长: ' + self.end_time0)
        self.output_emit()
        
        self.output_emit_util()
        self.logger.info(self.time_manager.__name__ + 
                         '计数:' + str(len(self.played_list)))
        self.output_emit()

        if self.minute >= 1:                                                 #时间超过一分钟，需要检测时间来切歌
            self.output_emit_util()
            self.logger.info(self.time_manager.__name__ + '时长超过1min, 启用监测')
            self.output_emit()
            while True:
                self.cur_time1,self.end_time1 = self.time_monitor()
                self.title1 = self.dlg.texts()                                    #当前曲名
                
                self.output_emit_util()
                self.logger.debug(self.time_manager.__name__ + '当前时间: %s' % self.cur_time1)
                self.output_emit()


                if self.title1 != self.title:
                    self.output_emit_util()
                    self.logger.warning(self.time_manager.__name__ + '侦测到计划外的切歌')
                    self.output_emit()

                    self.played_list.append(self.title)
                    
                    self.output_emit_util()
                    self.logger.warning(self.time_manager.__name__ + '结束当前循环...')
                    self.output_emit()
                    
                    break
                elif self.cur_time1 == self.cur_time2 and self.playflag == True:
                    self.output_emit_util()
                    self.logger.warning(self.time_manager.__name__ + '侦测到计划外的停止, 再次播放...')
                    self.output_emit()
                    
                    pyautogui.hotkey('ctrl', 'alt', 'p')
                elif int(self.cur_time1.split(':')[0]) >= 1:
                    self.played_list.append(self.title)
                    
                    self.output_emit_util()
                    self.logger.debug(self.time_manager.__name__ + '切歌...')
                    self.output_emit()
                    
                    pyautogui.hotkey('ctrl', 'alt', 'right')
                    break
                self.cur_time2,self.end_time2 = self.time_monitor()
        else:
            self.output_emit_util()
            self.logger.info(self.time_manager.__name__ + '时长不足1min, 禁用监测')
            self.output_emit()
            
            while True:
                self.cur_time3,self.end_time3 = self.time_monitor()
                self.title2 = self.dlg.texts()
                if self.title2 != self.title:
                    self.played_list.append(self.title)
                    
                    self.output_emit_util()
                    self.logger.debug(self.time_manager.__name__ + '较短的歌曲已播放结束, 结束当前循环...')
                    self.output_emit()
                    
                    break
                elif self.cur_time3 == self.cur_time4 and self.playflag == True:
                    self.output_emit_util()
                    self.logger.warning(self.time_manager.__name__ + '侦测到计划外的停止, 再次播放...')
                    self.output_emit()
                    
                    pyautogui.hotkey('ctrl', 'alt', 'p')
                self.cur_time4,self.end_time4 = self.time_monitor()
                time.sleep(2)



class MainWin(QWidget):
    def __init__(self):
        self.cur_time, self.end_time = 0,0
        self.n = 0
        self.firstrun = True
        self.playflag = True
        self.played_list = []

        super().__init__()
        self.init_logger()
        self.init_ui()
    
    def init_logger(self):
        '''
        日志相关
        '''
        # 创建一个日志记录器
        self.logger = logging.getLogger(' ' + __name__ + ' ')
        self.logger.setLevel(logging.DEBUG)
        #
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.handler_ = logging.StreamHandler()
        self.handler_.setFormatter(self.formatter)
        
        self.logger.addHandler(self.handler_)

    def init_ui(self):
        '''
        UI初始化设置
        '''
        self.ui = Ui_qt5design.Ui_MainWindow()
        self.window = QMainWindow()
        self.ui.setupUi(self.window)

        #信号绑定槽函数
        self.ui.pushButtonRun.clicked.connect(self.pushButtonRunfunc)
        self.ui.pushButtonStop.clicked.connect(self.pushButtonStop)
        self.ui.horizontalSliderCount.sliderMoved.connect(self.Scountreader)
        self.ui.lineEditCount.editingFinished.connect(self.Lcountreader)



    def output_to_window(self, text):
        '''
        打印输出(更新窗口文本)
        '''
        originaltext = self.ui.textBrowserLogger.toPlainText()

        self.ui.textBrowserLogger.setText(originaltext + text)
    
    
    def outputter_util(self):
        '''
        先调用util创建handler,执行完.log()语句后再调用outputter---可用装饰器，但太麻烦
        '''
        ## 每次调用都重置output
        # 创建一个输出到字符串的处理器
        self.output = StringIO()
        self.handler_ = logging.StreamHandler(self.output)
        self.handler_.setFormatter(self.formatter)
        self.logger.addHandler(self.handler_)
    def outputter(self):
        '''
        将MainWin的log输出至窗口
        '''
        self.output_text = self.output.getvalue()
        self.output_to_window(self.output_text)
    
    def outputter2(self, text):
        '''
        接受RunThread的singal(output_)并将其log输出至窗口
        '''
        self.output_to_window(text)

    def run_thread(self):
        '''
        子线程启动入口
        '''
        self.thread = RunThread(self.logger, self.cur_time, self.end_time,
                                self.n, self.firstrun, self.played_list, 
                                self.playflag)
        #启动线程
        self.thread.start()
        self.thread.output_.connect(self.outputter2)



    def pause(self):
        self.runflag = True
        while True:
            if self.runflag == True:
                time.sleep(0.1)
            else:
                self.playflag = False
                
                self.outputter_util()
                self.logger.info(self.pause.__name__ + ' 已暂停 \n')
                self.outputter()

                pyautogui.hotkey('ctrl', 'alt', 'p')
                while self.runflag == False:
                    time.sleep(0.1)
                
                self.playflag = True
                self.echoflag = True
                
                self.outputter_util()
                self.logger.info(self.pause.__name__ + ' 已恢复 \n')
                self.outputter()

                pyautogui.hotkey('ctrl', 'alt', 'p')


    #---------------------------槽函数----
    def pushButtonRunfunc(self):
        self.outputter_util()
        self.logger.debug('恢复')
        self.outputter()
        self.runflag = True
        if self.firstrun == True:
            self.logger.info(self.pushButtonRunfunc.__name__ + ' 启动程序 \n')
            self.run_thread()
            self.firstrun = False
        self.ui.pushButtonRun.setDisabled(True)
        self.ui.pushButtonStop.setEnabled(True)
    def pushButtonStop(self):
        self.outputter_util()
        self.logger.info(self.pushButtonStop.__name__ + ' 暂停程序 \n')
        self.outputter()
       
        self.runflag = False
        self.ui.pushButtonStop.setDisabled(True)
        self.ui.pushButtonRun.setEnabled(True)
    def Scountreader(self):
        self.ui.pushButtonRun.setEnabled(True)
        self.n = self.ui.horizontalSliderCount.value()
        self.ui.lineEditCount.setText(str(self.n))
        
        self.outputter_util()
        self.logger.debug(self.n)
        self.outputter()
    def Lcountreader(self):
        self.ui.pushButtonRun.setEnabled(True)
        try:
            self.n = int(self.ui.lineEditCount.text())
            self.ui.horizontalSliderCount.setValue(self.n)
            self.outputter_util()
            self.logger.debug(self.n)
            self.outputter()
        except ValueError:
            self.outputter_util()
            self.logger.warn(self.Lcountreader.__name__, " 输入的值有误 value = '%s'" % self.ui.lineEditCount.text())
            self.outputter()
    #---------------------------槽函数----



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwin = MainWin()
    mainwin.window.show()
    sys.exit(app.exec_())

    