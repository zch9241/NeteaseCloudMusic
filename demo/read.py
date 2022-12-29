import json
def reader():
    with open('status.json','r') as f:
        content = json.load(f)
        f.close()
        content["stat"]["runduration"] = ['1','','','','']
        with open('status.json','w') as f:
            json.dump(content , f,indent=4)
reader()
#{'lastrun': '', 'runnum': 3, 'currentnum': 1, 'stat': {'runtimes': 0}}