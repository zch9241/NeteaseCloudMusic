import json
import time

with open('status.json','r') as f:
	content = json.load(f)
	if content['lastrun'] == time.strftime('%j', time.localtime()):
		run_done = True
		f.close()
		print('[main(INFO)]: 今日已运行过此程序，程序即将退出...')
	else:
		run_done = False
		content['lastrun'] = time.strftime('%j', time.localtime())

if run_done == False:
	with open('status.json','w') as f:
		json.dump(content, f, indent = 4)
		f.close()




