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

class OCR(object):
    def __init__(self):
        self.apikey = ''
        self.sacle = 1.25     #屏幕缩放125%
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
        print('[OCR(main)] 截图完成')
        while True:
            print('[OCR(main)] 上传截图至 ocr.space')
            res0 = json.loads(OCR().ocr_space_file(filename = 'username.jpg', language = 'chs'))
            if res0["IsErroredOnProcessing"] == True:
                print('[OCR(main)] 请求失败 %s' % (res0["ErrorMessage"]))
                time.sleep(1)
                print('[OCR(main)] 重试...')
                continue
            else:
                try:
                    username = res0["ParsedResults"][0]["TextOverlay"]["Lines"][0]["LineText"]
                    print('[OCR(info)] OCR成功 用户名: %s' % username)
                    break
                except IndexError:
                    res1 = json.loads(OCR().ocr_space_file(filename = 'username.jpg', language = language))
                    if res0["ParsedResults"][0]["TextOverlay"]["Lines"] == [] and res1["ParsedResults"][0]["TextOverlay"]["Lines"] == []:
                        self.errorcode = 1
                        username = ''
                    elif res0["ParsedResults"][0]["TextOverlay"]["Lines"] == []:
                        username = res1["ParsedResults"][0]["TextOverlay"]["Lines"]
                    break

        if username == r'未登录':
            print('[OCR(main)] 请检查登录状态')
            ToastNotifier().show_toast('notification', '未登录，请检查登录状态', '.\\icon\\py.ico')
        elif username == '':
            print('[OCR(main)] 无法识别图像中的文字，请检查截图是否正确')
            ToastNotifier().show_toast('notification', '无法识别图像中的文字，请检查截图是否正确', '.\\icon\\py.ico')
        return self.errorcode

OCR().main()

