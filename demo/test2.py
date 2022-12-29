import threading

lock = threading.Lock()

lock.acquire()
print('ok')
lock.acquire()
print('ok')