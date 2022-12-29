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
    #使用py.exe时
    #exe_path = project_path + '\bin//' + name
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

    cond.wait()    #等待切换曲目
    print('wait结束')


def checktext(text_now, text_compare = None):
    global cond
    global text
    global number
    global time_
    while True:
        time.sleep(5)
        time_ = time_ + 5
        print(time_)

        if time_ >= 10:
            time_ = 0
            cond.notify()    #当时间达到预期时，切换曲目
            time.sleep(1)
            cond.release()
            return True
            
        elif text_now != text:
            print('[main(warn)]: 曲目时间小于预期值，进行应对...(当前曲目: %s)' % text_now)
            #重设text变量
            text = text_now
            #此时不能调用notify()，可能造成时间浪费
            number = number - 1 
            break
        elif text_now == text:
            break    #正常情况(time_小于70s，曲目时长大于70s)

def worker():
    '''
    工作者
    '''
    global number
    if number > 0:
        cond.acquire()
        run()
        number = number - 1
        print('请求锁')
        cond.acquire()
        print('完成')
    else:
        print('[main(info)]: 程序运行完成! 共切换曲目 %d 次' % task_count)

def supervisor():
    '''
    监督者
    '''
    time.sleep(2)
    while True:
        cond.acquire()
        text_now = win32gui.GetWindowText(hwnd)
        Bool = checktext(text_now = text_now)
        if Bool == None:
            cond.release()
        elif Bool == True:
            pass


if __name__ =='__main__':
    pausebreak()
    lock = threading.Lock()
    cond = threading.Condition(lock = lock)
    taskA = threading.Thread(target = worker)
    taskB = threading.Thread(target = supervisor)
    taskC = threading.Thread(target = isexist)
    taskC.start()
    taskA.start()
    taskB.start()
    taskA.join()




