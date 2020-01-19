import os
import subprocess
import time

seedSource = open("./test_seeds.txt", "r")

print("Spawning endpoint.")
sPort = int(os.getenv("SERVER_PORT", "50123"))
sICTestApp = os.getenv("IC20_LOCATION", "./ic20_windows.exe")
runCount = 0
proc = subprocess.Popen(["/usr/bin/env", "python3", "./main.py"])
time.sleep(2)

nullPipe = open(os.devnull, "w")

while True:
    currentSeed: str = seedSource.readline()
    currentSeed = currentSeed.strip('\n\r ')
    if not currentSeed or not currentSeed.strip():
        break

    runCount += 1
    print(f'Run {runCount} with seed {currentSeed} against port {sPort}')
    icProc = subprocess.Popen(
        args=[sICTestApp, '-s', currentSeed, '-u', "http://localhost:" + str(sPort) + "/"],
        stdout=nullPipe
    )
    icProc.wait()
    if icProc.returncode != 0:
        print(f'Execution failed.')
        proc.kill()
        exit(1)

proc.kill()
nullPipe.close()
