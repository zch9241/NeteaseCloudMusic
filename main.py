# Author: zch9241 <github.com/zch9241><zch2426936965@gmail.com>。保留所有权利。
# 
# 版权声明：该软件（NeteaseCloudMusic）为「zch」所有，转载请附上本声明。
# Apache 2.0
# 
# version: 1.5.alpha
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
#

from pywinauto.application import Application
import time
import pyautogui
from win10toast import ToastNotifier

played_list = []
cur_time,end_time = 0,0

def executing_time(func):
    def inner():
        start = time.time()
        a,b = func()
        end = time.time()
        last = end-start
        print(executing_time.__name__, func,'执行时间: ', last, 's')
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

    print(time_manager.__name__, '当前曲目:', str(title)[2:-2].replace(r'\xa0', ' '), '总时长: ', end_time0)
    print(time_manager.__name__, '计数:', len(played_list))
    
    if minute >= 1:                                                 #时间超过一分钟，需要检测时间来切歌
        print(time_manager.__name__, '时长超过1min, 启用监测')
        while True:
            cur_time1,end_time1 = time_monitor()
            title1 = dlg.texts()                                    #当前曲名
            print(time_manager.__name__, '当前时间: %s' % cur_time1)

            if title1 != title:
                print(time_manager.__name__, '侦测到计划外的切歌')
                played_list.append(title)
                print(time_manager.__name__, '结束当前循环...')
                break
            elif cur_time1 == cur_time2:
                print(time_manager.__name__, '侦测到计划外的停止, 再次播放...')
                pyautogui.hotkey('ctrl', 'alt', 'p')
            elif int(cur_time1.split(':')[0]) >= 1:
                played_list.append(title)
                print(time_manager.__name__, '切歌...')
                pyautogui.hotkey('ctrl', 'alt', 'right')
                break
            cur_time2,end_time2 = time_monitor()
    else:
        print(time_manager.__name__, '时长不足1min, 禁用监测')
        while True:
            cur_time3,end_time3 = time_monitor()
            title2 = dlg.texts()
            if title2 != title:
                played_list.append(title)
                print(time_manager.__name__, '较短的歌曲已播放结束, 结束当前循环...')
                break
            elif cur_time3 == cur_time4:
                print(time_manager.__name__, '侦测到计划外的停止, 再次播放...')
                pyautogui.hotkey('ctrl', 'alt', 'p')
            cur_time4,end_time4 = time_monitor()
            time.sleep(2)


#创建进程实例
app = Application('uia').start(r'D:\Program Files\Netease\CloudMusic\cloudmusic.exe')
print('进程实例已创建: %s' % app)

#创建窗口实例
dlg = app['Dialog']     
time.sleep(5)           #等待窗口加载完成
#dlg.print_control_identifiers()

pyautogui.hotkey('ctrl', 'alt', 'p')

for i in range(10):
    time_manager()

pyautogui.hotkey('ctrl', 'alt', 'p')
#print(played_list)
ToastNotifier().show_toast('notification', '程序运行完成', '.\\icon\\py.ico')