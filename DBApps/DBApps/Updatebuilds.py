#!/usr/bin/env python3
"""
Update the buildPaths of newer builds. Scans newer builds. Updates each volume.
"""
import datetime
import subprocess
import os
import sys
import time
from pathlib import Path

from DBApps.getReadyWorks import updateBuildStatusWrapper

def doOneDir(batchDir: os.DirEntry):

    # These always false
    # if batchDir.is_dir():
    #     print('dir')
    # if batchDir.is_symlink():
    #     print('sl')
    #
    #

    # These dont work as advertised on BSD/MacOS
    #  if batchDir.name.startswith('batchW') and batchDir.is_dir(follow_symlinks=True):
    if batchDir.name.startswith('batchW') and os.path.isdir(batchDir.path):

        # This gets the time the link was created
        dStat = os.stat(batchDir.path)
        dirTime = datetime.datetime.fromtimestamp(dStat.st_ctime)
        print(f"Path {batchDir.path} time {dirTime}")
        result =  "success"  if os.path.exists(Path(batchDir.path,'batch.xml')) else "FAIL"
        updateBuildStatusWrapper('qa:~/.drsBatch.config', batchDir.path, dirTime, result)
    # subprocess.run(['updateBuildStatus', '-d', ])

if __name__ == '__main__':

    # Do the newprod first
    # for anent in os.scandir(path='/Volumes/DRS_Staging/DRS/prod/batchBuilds'):
    #     doOneDir(anent)
    #     ic = ic + 1
    #     if ic == 3:
    #         break

    calls = 0
    monitor_interval = 15
    etnow = time.perf_counter()

    for anent in os.scandir(path='/Volumes/DRS_Staging/DRS/oldprod/batchLinks'):

        doOneDir(anent)

        calls += 1
        if calls % monitor_interval == 0:
            y = time.perf_counter()
            print(" %d calls   Rate: %5.2f /sec"
                  % (calls,  monitor_interval / (y - etnow)))
            etnow = y


