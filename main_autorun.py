# Author: zch9241 <github.com/zch9241><zch2426936965@gmail.com>。保留所有权利。
# 
# 版权声明：该软件（MeteaseCloudMusic）为「zch」所有，转载请附上本声明。
# Apache 2.0
# 
# version: 1.3.1
# 
# 版本更新说明：
# v1.0 程序首个版本
# v1.1 优化使用体验（不激活窗口）
# v1.2 程序自动化，便于使用任务计划程序。须在命令行下使用autorun_main.py + 运行次数 方可使用
# v1.3 优化使用体验：1.多次登录时任务照常进行；2.status.json中增加了运行统计；3.任务完成后自动关闭云音乐
#      增加了log的一些细节并更改了log保存位置
# v1.3.1 修改了程序运行次数判定，增加程序运行结束时的通知
# 


import argparse
import json
import logging
import os
import threading
import time

import win32api
import win32con
import win32gui
from win10toast import ToastNotifier

task_count = 0  #任务计数
text = ''
time_ = 0
classname = 'OrpheusBrowserHost'
hwnd = ''
number = 0
#number = int(input('[main(input)]: 输入循环次数: '))
#number = int(310)

#主程序
def call_exe(name, pathprint = None):
    '''
    # call_exe
    - name: 应用程序名
    '''
    project_path = os.getcwd()
    #注释start
    #path = project_path + r'\Mycode\NeteaseCloudMusic\bin'
    #exe_path = path + '//' + str(name)
    #注释end
    #使用vs code运行时，请注意打开的文件夹路径即为os.getcwd()函数返回值 | 使用py.exe时，注释上两行，去掉下一行 # 注释
    exe_path = project_path + '//bin//' + name
    
    if pathprint == True:
        logger.info('[call_exe] 调用: ' + name)
        logger.info('[call_exe] 路径: ' + exe_path)
	
    os.system(exe_path)

def task_finished():
    '''
    # task_finished
    简易计数器
    '''
    global task_count

    task_count = task_count + 1

    writer(currentnum = task_count)

    return int(task_count)

def pausebreak():
    call_exe(name = 'pausebreak.exe', pathprint = True)

def run():
    global text
    global cond

    call_exe(name = 'switch.exe', pathprint = True)
    time.sleep(1)

    text = win32gui.GetWindowText(hwnd)
    count = task_finished()
    logger.info('[run] 当前曲目: ' + text)
    logger.info('[run] 计数: ' + str(count))

    logger.debug('[run] wait开始')
    cond.wait()    #等待切换曲目
    logger.debug('[run] wait结束')


def checktext(text_now, text_compare = None):
    global cond
    global number
    global text
    global time_
    global task_count

    while True:
        time.sleep(5)
        time_ = time_ + 5
        logger.debug('[checktext] 当前等待时间 %d s' % time_)

        if time_ >= 70:
            time_ = 0
            cond.notify()    #当时间达到预期时，切换曲目
            cond.release()      #释放锁
            return True
            
        elif text_now != text:
            logger.warning('[checktext] 曲目时间小于预期值，进行应对...(当前曲目: %s)' % text_now)
            #重设text变量
            text = text_now
            #此时不能调用notify()，可能造成时间浪费
            number = number - 1
            time_ = 0
            task_count = task_count + 1
            return False
        elif text_now == text:
            break    #正常情况(time_小于70s，曲目时长大于70s)

def isexist():
    '''
    # isexist
    确保窗口存在
    '''
    while True:
        call_exe(name = 'check.exe')

def worker():
    '''
    工作者
    '''
    global number

    cond.acquire()
    flag = 0
    while True:
        if number > 0 and flag == 0:
            run()
            number = number - 1
            flag = flag + 1

            cond.release()
            continue
        elif number > 0 and flag != 0:
            cond.acquire()
            run()
            number = number - 1

            cond.release()
            continue
        else:
            logger.info('[worker] 程序运行完成! 共切换曲目 %d 次' % task_count)
            break

def supervisor():
    '''
    监督者
    '''
    time.sleep(2)
    flag = 0
    while True:
        if flag == 0:
            cond.acquire()
        else:
            flag = 0

        text_now = win32gui.GetWindowText(hwnd)
        Bool = checktext(text_now = text_now)
        if Bool == False:
            flag = flag + 1
            time.sleep(2)
            continue
        elif Bool == True:
            time.sleep(2)
            continue
        else:
            flag = flag + 1
            continue
#

#辅助程序
class NeteaseHelper(object):
    def netease_finder(self):
        '''
        # 寻找cloudmusic.exe所在路径
        - return: cloudmusic.exe所在路径
        '''
        sub_key = r'Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store'
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, sub_key, 0, win32con.KEY_READ)
        info = win32api.RegQueryInfoKey(key)
        for i in range(0, info[1]):  
            value = win32api.RegEnumValue(key, i)
            #print(value)
            if value[0].endswith('cloudmusic.exe'):
                return value[0]

    def call_netease(self):
        '''
        运行cloudmusic.exe
        '''
        global hwnd

        path = NeteaseHelper().netease_finder()
        logger.debug('[call_netease] path: ' + path)
        filename = path.split('\\')[-1]
        path = path.replace(filename, '')
        command = 'd: & cd ' + path + ' & ' + filename
        os.popen(command)
        #os.system(command)
        time.sleep(10)

        while hwnd == '':
            hwnd = win32gui.FindWindow(classname, None)    #ClassName,WindowName
            if hwnd != '':
                logger.debug('[call_netease] 已找到窗口句柄: %s' % hwnd)
                break
            logger.warn('[call_netease] 未能找到窗口句柄...请检查 cloudmusic.exe 是否运行或重启本程序')
            time.sleep(1)
            logger.info('[call_netease] 重试...')


    def exit_netease(self):
        '''
        结束cloudmusic.exe
        '''
        command = 'taskkill -f -im cloudmusic.exe'
        os.system(command)

def writer(currentnum):
    '''
    更新status.json
    '''

    with open('status.json','r') as f:
        content = json.load(f)
        content['currentnum'] = currentnum
        f.close()
        with open('status.json','w') as f:
            json.dump(content, f, indent = 4)
            f.close()

def log_helper():
    '''
    # 创建log文件
    - return: log文件路径
    '''
    path = os.getcwd()
    try:
        curmonth = time.strftime('%B', time.localtime())
        folder = path + '\\logs\\' + curmonth
        os.mkdir(folder)
    except FileExistsError:
        logger.debug('DEBUG [log_helper] [FileExistsError] 目录存在: %s' % folder)

    curtime = time.strftime('%c', time.localtime()).replace(':', '-')
    filename = folder + '\\' + curtime + '.log'
    with open(file = filename,mode = 'w', newline='\n') as f:
        f.write('logfile from %s \n\n\n' % time.strftime('%c', time.localtime()))
        f.close()
        print('DEBUG [log_helper] log文件已创建 -- %s' % filename.split('\\')[-1])
    
    return str(filename)
#

if __name__ =='__main__':
    #历史
    #运行次数累加
    with open('status.json','r') as f:
        content = json.load(f)
        f.close()
        content["stat"]["runtimes"] = 1 + int(content["stat"]["runtimes"])
        content["stat"]["songtimes"] = int(content["currentnum"]) + int(content["stat"]["songtimes"])

        with open('status.json','w') as f:
            json.dump(content, f, indent = 4)
            f.close()

    #日志相关
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()    #输出到控制台
    file_handler = logging.FileHandler(filename = log_helper(), encoding = 'UTF-8')    #输出到文件

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    #

    #定义运行参数
    parse = argparse.ArgumentParser()
    parse.add_argument('n', type = int, help = '输入循环次数(int)')
    args = parse.parse_args()
    #

    number = int(args.n)

	#获取程序运行情况，防止重复运行
    with open('status.json','r') as f:
        content = json.load(f)
        if content['lastrun'] == time.strftime('%j', time.localtime()):
            HaveRunNum = int(content["currentnum"])
            PlanNum = int(content['runnum'])
            f.close()

            logger.info('[main] 今日已运行过此程序。')
            logger.info('[main] 运行次数：%d' % HaveRunNum)

            if HaveRunNum < PlanNum and PlanNum == number:    #第二次运行
                number = PlanNum - HaveRunNum    #需执行的次数
                logger.info('[main] 还需运行 %d 次' % number)
                run_done = False
            elif HaveRunNum < PlanNum and PlanNum < number:     #运行次数>=3
                number = PlanNum - HaveRunNum    #需执行的次数
                logger.debug('[main] 今日运行次数超过2次')
                logger.info('[main] 还需运行 %d 次' % number)
                run_done = False
            else:
                number = number
                logger.info('[main] 今日运行次数足够，程序即将退出...')
                run_done = True
        else:
            run_done = False
            number = number
            f.close()

    if run_done == False:
        logger.info('[main] 循环次数: '+ str(number))

        NeteaseHelper().call_netease()

        with open('status.json','r') as f:
            content = json.load(f)
            content['lastrun'] = time.strftime('%j', time.localtime())
            content['runnum'] = number
            f.close()
            with open('status.json','w') as f:
                json.dump(content, f, indent = 4)
                f.close()

        #程序主体
        pausebreak()
        lock = threading.Lock()
        cond = threading.Condition(lock = lock)
        taskA = threading.Thread(target = worker)
        taskB = threading.Thread(target = supervisor, daemon = True)
        taskC = threading.Thread(target = isexist, daemon = True)
        taskC.start()
        taskA.start()
        taskB.start()
        taskA.join()
        pausebreak()
        #

        NeteaseHelper().exit_netease()

        logger.info('------end------')

    elif run_done == True:
        pass
    ToastNotifier().show_toast('notification', '程序运行完成', '.\\icon\\py.ico')