#!/usr/bin/env python3
"""
Update the buildPaths of newer builds. Scans newer builds. Updates each volume.
"""
import datetime
import subprocess
import os
import sys
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
        if os.path.exists(Path(batchDir.path,'batch.xml')):
            updateBuildStatusWrapper('prod:~/.drsBatch.config', batchDir.path, dirTime, "success")
    # subprocess.run(['updateBuildStatus', '-d', ])

if __name__ == '__main__':

    ic = 0
    # Do the newprod first
    # for anent in os.scandir(path='/Volumes/DRS_Staging/DRS/prod/batchBuilds'):
    #     doOneDir(anent)
    #     ic = ic + 1
    #     if ic == 3:
    #         break

    ic = 0
    for anent in os.scandir(path='/Volumes/DRS_Staging/DRS/oldprod/batchLinks'):
        doOneDir(anent)
        ic += 1
        if ic == 3:
            break;


