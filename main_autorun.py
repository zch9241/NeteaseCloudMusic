# Author: zch9241 <github.com/zch9241><zch2426936965@gmail.com>。保留所有权利。
# 
# 版权声明：该软件（MeteaseCloudMusic）为「zch」所有，转载请附上本声明。
# Apache 2.0
# 
# version: 1.4
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
# 
#



import argparse
import json
import logging
import os
import threading
import time
import requests

from PIL import Image
import win32ui
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
    while taskA.is_alive():
        call_exe(name = 'check.exe')
        time.sleep(1)

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
            logger.warning("[call_netease] 未能找到窗口句柄...请检查'cloudmusic.exe'是否运行或重启本程序")
            time.sleep(1)
            logger.info('[call_netease] 重试...')


    def exit_netease(self):
        '''
        结束相关程序
        '''
        command0 = 'taskkill -f -im check.exe'
        os.popen(command0)
        time.sleep(1)
        command1 = 'taskkill -f -im cloudmusic.exe & taskkill -f -im cloudmusic_reporter.exe'
        os.popen(command1)
        logger.info('[exit_netease] 相关程序已结束运行')

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

class OCR(object):
    def __init__(self):
        self.apikey = ''    #你的api_key
        self.sacle = 1.25     #屏幕缩放比125%
        self.errorcode = 0

    def screenshot(self):
        hwnd = win32gui.FindWindow('OrpheusBrowserHost', None)
        # 激活窗口
        win32gui.SetForegroundWindow(hwnd)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
        time.sleep(5)
        # 截图整个桌面
        # 获取桌面
        hdesktop = win32gui.GetDesktopWindow()
        # 分辨率适应
        width = int(win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN) * self.sacle)
        height = int(win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN) * self.sacle)
        left = int(win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN) * self.sacle)
        top = int(win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN) * self.sacle)
        # 创建设备描述表
        desktop_dc = win32gui.GetWindowDC(hdesktop)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)
        # 创建一个内存设备描述表
        mem_dc = img_dc.CreateCompatibleDC()
        # 创建位图对象
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)
        # 截图至内存设备描述表
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (0, 0), win32con.SRCCOPY)
        # 将截图保存到文件中
        screenshot.SaveBitmapFile(mem_dc, 'screenshot.bmp')
        # 内存释放
        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

        box = (1425,0,1500,75)

        img = Image.open('screenshot.bmp')

        rect = img.crop(box)

        result_image = Image.new('RGB', (75,75), (0,0,0,0)) #mode, result size, color
        result_image.paste(rect, (0,0), mask=0)
        result_image.save('username.jpg')

    def ocr_space_file(self, filename, overlay=False, language='eng'):
        """ OCR.space API request with local file.
            Python3.5 - not tested on 2.7
        :param filename: Your file path & name.
        :param overlay: Is OCR.space overlay required in your response.
                        Defaults to False.
        :param api_key: OCR.space API key.
                        Defaults to 'helloworld'.
        :param language: Language code to be used in OCR.
                        List of available language codes can be found on https://ocr.space/OCRAPI
                            Defaults to 'en'.
        :return: Result in JSON format.
        """

        payload = {'isOverlayRequired': overlay,
                'apikey': self.apikey,
                'language': language,
                'OCREngine': 5
                }
        with open(filename, 'rb') as f:
            r = requests.post('https://api.ocr.space/parse/image',
                            files={filename: f},
                            data=payload,
                            )
        return r.content.decode()

    def main(self, language = 'eng'):
        '''
        实现账户登录状况判断
        '''
        OCR().screenshot()
        logger.info('[OCR(main)] 截图完成')
        while True:
            logger.info('[OCR(main)] 上传截图至 ocr.space')
            res0 = json.loads(OCR().ocr_space_file(filename = 'username.jpg', language = 'chs'))
            if res0["IsErroredOnProcessing"] == True:
                logger.warning('[OCR(main)] 请求失败 %s' % (res0["ErrorMessage"]))
                time.sleep(1)
                logger.info('[OCR(main)] 重试...')
                continue
            else:
                try:
                    username = res0["ParsedResults"][0]["TextOverlay"]["Lines"][0]["LineText"]
                    logger.info('[OCR(info)] OCR成功 用户名: %s' % username)
                    break
                except IndexError:
                    res1 = json.loads(OCR().ocr_space_file(filename = 'username.jpg', language = language))
                    if res0["ParsedResults"][0]["TextOverlay"]["Lines"] == [] and res1["ParsedResults"][0]["TextOverlay"]["Lines"] == []:
                        self.errorcode = 1
                        username = ''
                    elif res0["ParsedResults"][0]["TextOverlay"]["Lines"] == []:
                        username = res1["ParsedResults"][0]["TextOverlay"]["Lines"]
                        logger.info('[OCR(info)] OCR成功 用户名: %s' % username)
                    break

        if username == r'未登录':
            self.errorcode = 2
            logger.warning('[OCR(main)] 请检查登录状态 (errorcode: %d)' % self.errorcode)
            ToastNotifier().show_toast('notification', '未登录，请检查登录状态', '.\\icon\\py.ico')
        elif username == '':
            logger.critical('[OCR(main)] 无法识别图像中的文字，请检查截图是否正确 (errorcode: %d)' % self.errorcode)
            ToastNotifier().show_toast('notification', '无法识别图像中的文字，请检查截图是否正确', '.\\icon\\py.ico')
        return self.errorcode

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
    parse.add_argument('ocr',type = bool, help = '是否启用OCR判断登录状态')
    args = parse.parse_args()
    #

    number = int(args.n)
    ocr = args.ocr

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
        
        if ocr == True:
            time.sleep(2)
            e = OCR().main()
            if e != 0:
                logger.info('[main] 遇到错误，程序即将退出 (errorcode: %d)' % e)
                exit()
        
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
        taskA.start()
        taskB.start()
        time.sleep(0.1)
        taskC.start()
        taskA.join()
        pausebreak()
        #

        NeteaseHelper().exit_netease()

        logger.info('------end------')

    elif run_done == True:
        pass
    ToastNotifier().show_toast('notification', '程序运行完成', '.\\icon\\py.ico')





# 使用win10toast时遇到的错误

# 
# Python WNDPROC handler failed
# Traceback (most recent call last):
#   File "C:\Users\Lenovo\AppData\Local\Programs\Python\Python310\lib\site-packages\win10toast\__init__.py", line 153, in on_destroy
#     Shell_NotifyIcon(NIM_DELETE, nid)
# pywintypes.error: (-2147467259, 'Shell_NotifyIcon', '未指定的错误')
# 

# 
# WNDPROC return value cannot be converted to LRESULT
# TypeError: WPARAM is simple, so must be an int object (got NoneType)
# 