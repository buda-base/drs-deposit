#!/usr/bin/env python3
"""
Update the buildPaths of newer builds
"""

import subprocess
import os

from DBApps.getReadyWorks import updateBuildStatus

if __name__ == '__main__':
    for anent in os.scandir(path='/Volumes/DRS_Staging/DRS/prod/batchBuilds'):
        if not anent.name.startswith('.') and anent.is_dir():
            subprocess.run(['updateBuildStatus', '-d', 'prod:~/.drsBatch.config', anent.path, "success"])
