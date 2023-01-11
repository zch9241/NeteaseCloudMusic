#修改了python目录Lib\site-packages\pytesseract\pytesseract.py中tesseract_cmd变量的值

import time

import requests
import win32api
import win32con
import win32gui
import win32ui
from PIL import Image

api_key = ''     #ocr.space的apikey
language0 = 'chs'
language1 = 'eng'
sacle = 1.25     #屏幕缩放125%

def screenshot():
    hwnd = win32gui.FindWindow('OrpheusBrowserHost', None)
    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
    time.sleep(1)
    # 截图整个桌面
    # 获取桌面
    hdesktop = win32gui.GetDesktopWindow()
    # 分辨率适应
    width = int(win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN) * sacle)
    height = int(win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN) * sacle)
    left = int(win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN) * sacle)
    top = int(win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN) * sacle)
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

def ocr_space_file(filename, api_key, overlay=False, language='eng'):
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
               'apikey': api_key,
               'language': language,
               'OCREngine': 5
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.content.decode()

def main():
    screenshot()
    test_file = ocr_space_file(api_key = api_key, filename = 'username.jpg', language = 'eng')
    print(test_file)