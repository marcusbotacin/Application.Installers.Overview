#!/usr/bin/python
# -*- coding: utf-8 -*-

# Giovanni Bertao
# UNICAMP 2019
# Auto-It Behemot plUGin
# Deploy auto-install software plugin after behemot upload analysis finishes

import wmi
import autoit
import time
import subprocess
import getopt
import sys
import os

USE = """Auto-It Behemot plUGin

Usage: AIBug.py -s <path> [--sleep <seconds>]

path = autoit compiled script path
seconds = seconds to wait before behemot deployed, default is 180 seconds

"""

# Argument parsing
pathScript = None
delay = "180"

if len(sys.argv) < 3:
    print(USE)
    sys.exit(2)

try:
    optsArgs, trash = getopt.getopt(sys.argv[1:],"s:",["sleep="])
except getopt.GetOptError as err:
    print(err)
    print(USE)
    sys.exit(2)

for opt, arg in optsArgs:
    if opt == "-s":
        pathScript = arg
    elif opt == "--sleep":
        delay = arg
    else:
        print(USE)
        sys.exit(2)

# Arg validation

# Path validation
if pathScript == None or not os.path.exists(pathScript):
    print("Missing Autoit executable(compilled) script")
    print(USE)
    sys.exit(2)

# Sleep time
if not delay.isdigit():
    print("Incorrect time")
    print(USE)
    sys.exit(2)


# Delay
time.sleep(float(delay))


# Acquire PID from malware.exe process

# Initialize connection to local machine
c = wmi.WMI()

malware = None
# Iterate over process list
for proc in c.Win32_Process():
    if proc.Name == "malware.exe":
        malware = proc
        break

# Process validadion
if not malware:
    print("Process not found")
    sys.exit(1)

# Deploy autoit script
pathSS = os.path.dirname(os.path.abspath(malware.ExecutablePath))
pid = malware.ProcessID
if pid > 0:
    subprocess.call([str(pathScript),str(pid),str(pathSS)])
