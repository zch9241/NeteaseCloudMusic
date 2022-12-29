# Author: zch9241 <github.com/zch9241><zch2426936965@gmail.com>。保留所有权利。
# 
# 版权声明：该软件（MeteaseCloudMusic）为「zch」所有，转载请附上本声明。
# Apache 2.0
# 
# version: 1.1
# 
# 版本更新说明：
# v1.0 程序首个版本
# 
# 


import os
import time
import threading
import win32gui


task_count = 0  #任务计数
text = ''
time_ = 0
classname = 'OrpheusBrowserHost'

number = int(input('[main(input)]: 输入循环次数: '))
hwnd = win32gui.FindWindow(classname, None)    #ClassName,WindowName
#print(hwnd)


def call_exe(name, pathprint = None):
    '''
    # call_exe
    - name: 应用程序名
    '''
    project_path = os.getcwd()
    path = project_path + r'\NeteaseCloudMusic\bin'
    exe_path = path + '//' + str(name)
    #使用py.exe时，注释上两行 | 使用vs code运行
    #exe_path = project_path + '//bin//' + name
    if pathprint == True:
        print('[main(info)]: 调用', name, '路径:', exe_path)

    os.system(exe_path)

def isexist():
    '''
    # isexist
    确保窗口存在
    '''
    while True:
        call_exe(name = 'check.exe')

def task_finished():
    '''
    # task_finished
    简易计数器
    '''
    global task_count
    task_count = task_count + 1
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
    print('[main(info)]: 当前曲目: ', text, '计数: ', count)

    print('wait开始')
    cond.wait()    #等待切换曲目
    print('wait结束')


def checktext(text_now, text_compare = None):
    global cond
    global text
    global number
    global time_
    global task_count
    while True:
        time.sleep(5)
        time_ = time_ + 5
        print(time_)

        if time_ >= 70:
            time_ = 0
            cond.notify()    #当时间达到预期时，切换曲目
            cond.release()      #释放锁
            return True
            
        elif text_now != text:
            print('[main(warn)]: 曲目时间小于预期值，进行应对...(当前曲目: %s)' % text_now)
            #重设text变量
            text = text_now
            #此时不能调用notify()，可能造成时间浪费
            number = number - 1
            time_ = 0
            task_count = task_count + 1
            return False
        elif text_now == text:
            break    #正常情况(time_小于70s，曲目时长大于70s)

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
            print('完成')
            cond.release()
            continue
        elif number > 0 and flag != 0:
            cond.acquire()
            run()
            number = number - 1
            print('完成')
            cond.release()
            continue
        else:
            print('[main(info)]: 程序运行完成! 共切换曲目 %d 次' % task_count)
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


if __name__ =='__main__':
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


