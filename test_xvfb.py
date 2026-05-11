import subprocess
import time

try:
    p = subprocess.Popen(["xvfb-run", "-a", "python3", "Flasher/Linux/InsaneFlasher.py"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    time.sleep(3)
    p.terminate()
    stdout, stderr = p.communicate()
    print("STDOUT:", stdout.decode())
    print("STDERR:", stderr.decode())
    print("Return code:", p.returncode)
except Exception as e:
    print(e)
