#对后台窗口截图
import win32gui, win32ui, win32con
import cv2
import numpy
import ctypes

classname = 'OrpheusBrowserHost'

#获取后台窗口的句柄，注意后台窗口不能最小化
hWnd = win32gui.FindWindow(classname, None)  #窗口的类名可以用Visual Studio的SPY++工具获取
hWnd = win32gui.FindWindowEx(hWnd, 0, None, None)
#获取句柄窗口的大小信息
def get_current_size():
    try:
        f = ctypes.windll.dwmapi.DwmGetWindowAttribute
    except WindowsError:
        f = None
    if f:
        rect = ctypes.wintypes.RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        f(ctypes.wintypes.HWND(hWnd),
          ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
          ctypes.byref(rect),
          ctypes.sizeof(rect)
          )
        size = (rect.right - rect.left, rect.bottom - rect.top)        
        return size
#left, top, right, bot = win32gui.GetWindowRect(hWnd)
#width = right - left
#height = bot - top
size = get_current_size()
width = size[0]
height = size[1]


#返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
hWndDC = win32gui.GetWindowDC(hWnd)
#创建设备描述表
mfcDC = win32ui.CreateDCFromHandle(hWndDC)
#创建内存设备描述表
saveDC = mfcDC.CreateCompatibleDC()
#创建位图对象准备保存图片
saveBitMap = win32ui.CreateBitmap()
#为bitmap开辟存储空间
saveBitMap.CreateCompatibleBitmap(mfcDC,width,height)
#将截图保存到saveBitMap中
saveDC.SelectObject(saveBitMap)
#保存bitmap到内存设备描述表
saveDC.BitBlt((0,0), (width,height), mfcDC, (0, 0), win32con.SRCCOPY)
###获取位图信息
signedIntsArray = saveBitMap.GetBitmapBits(True)
#内存释放
win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hWnd,hWndDC)
#保存到文件
img = numpy.frombuffer(signedIntsArray, dtype = 'uint8')
img.shape = (height, width, 4)
cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
cv2.imwrite("img.jpg",img,[int(cv2.IMWRITE_JPEG_QUALITY), 100]) 
#显示到屏幕
cv2.namedWindow('img') #命名窗口
cv2.imshow("img",img) #显示
cv2.waitKey(0)
cv2.destroyAllWindows()