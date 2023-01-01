import win32con
import win32api

def netease_finder():
    sub_key = r'Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store'
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, sub_key, 0, win32con.KEY_READ)
    info = win32api.RegQueryInfoKey(key)
    for i in range(0, info[1]):  
        value = win32api.RegEnumValue(key, i)
        #print(value)
        if value[0].endswith('cloudmusic.exe'):
            return value[0]
print(netease_finder().split('\\')[-1])