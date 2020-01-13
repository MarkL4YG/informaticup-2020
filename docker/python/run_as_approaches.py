import os
import subprocess

seedSource = open("./test_seeds.txt", "r")

print("Spawning endpoint.")
proc = subprocess.Popen(["/usr/bin/env", "python3", "./main.py"])
sPort = int(os.getenv("SERVER_PORT", "50123"))
sICTestApp = os.getenv("IC20_LOCATION", "./ic20_windows.exe")
runCount = 0

while True:
    currentSeed: str = seedSource.readline()
    if not currentSeed or not currentSeed.strip():
        break

    runCount += 1
    print(f'Run {runCount} with seed {currentSeed}')
    icProc = subprocess.Popen([sICTestApp, "--random-seed", currentSeed, "--endpoint-url", f'http://localhost:{sPort}/'])
    icProc.wait()

proc.kill()
