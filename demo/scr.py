# 截图整个桌面
import win32gui
import win32ui
import win32con
import win32api

# 获取桌面
hdesktop = win32gui.GetDesktopWindow()
# 分辨率适应
#width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
#height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
#left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
#top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
width = 1920
height = 1020
left = 0
top = 0
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