import json

with open('status.json','r') as f:
	c = json.load(f)
	c['lastrun'] = 0
	f.close()
	with open('status.json','w') as f:
		json.dump(c,f)
