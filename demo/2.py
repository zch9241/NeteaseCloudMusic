import subprocess
 
cmd = ['tasklist']
process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
for stdout_line in iter(process.stdout.readline, b""):
    print(stdout_line)
process.stdout.close()
return_code = process.wait()
