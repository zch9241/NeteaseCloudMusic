import threading
import time
def a():
    for i in range(4):
        print('123')
        time.sleep(1)

def b():
    while ta.is_alive():
        print('正在运行func:b')
        time.sleep(1)

ta = threading.Thread(target = a)
tb = threading.Thread(target = b)
ta.start()
tb.start()

