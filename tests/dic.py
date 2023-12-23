varibles = {'var1': 1, 'var2': 2}
status = {'th1': True, 'th2': False}

s = 0
m = 0

for varname in varibles:
            s+=1
            for key in status:
                m+=1
                if s == m:
                    print(varname)
                    print('varibles[varname].setText(0, key)', key)
                    print('varibles[varname].setText(1, status[key])', status[key])
                    m = 0
                    break
