import time
import os

def log_helper():
    path = os.getcwd()
    try:
        curmonth = time.strftime('%B', time.localtime())
        folder = path + '\\logs\\' + curmonth
        os.mkdir(folder)
    except FileExistsError:
        print('exist')

    curtime = time.strftime('%c', time.localtime()).replace(':', '-')
    filename = folder + '\\' + curtime + '.log'
    with open(file = filename,mode = 'w', newline='\n') as f:
        f.write('logfile from %s \n\n\n' % time.strftime('%c', time.localtime()))
log_helper()