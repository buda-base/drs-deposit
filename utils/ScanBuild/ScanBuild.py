#!/usr/bin/env python
import argparse
from datetime import datetime
import os;
import pathlib
import sys


class ScanBuildArgs:
    """
    Holds command line arguments
    """
    pass


def parseArgs() -> str:
    """
    wrapper for argument parsing
    :return:
    """
    args = ScanBuildArgs()
    _parser = argparse.ArgumentParser(
        description='Looks for Issue 66(https://github.com/BuddhistDigitalResourceCenter/drs-deposit/issues/66)'
                    ' (file name doesnt contain OSN) '
                    '', usage="%(prog)s rootPath ")
    _parser.add_argument("rootPath", help='Directory containing batch build results')

    _parser.parse_args(namespace=args)
    return args.rootPath


def scanBuild():
    """
    scan the buld  Directories looking for directories whose contents do not match a certain pattern
    :param root:
    :return:
    """

    root = parseArgs()

    # top level is the batches]
    folders = [f for f in os.scandir(root) if (f.is_dir() & f.name.startswith('batchW'))]
    print(len(folders))
    for batchFolder in folders:

        vols = [v for v in os.scandir(batchFolder) if v.is_dir()]
        for vol in vols:
            volBreak = False
            volBeads = vol.name.split('-')
            if len(volBeads) != 2:
                print("Not a conformant image directory " + batchFolder.name + " " + vol.name)
                continue
            volName = volBeads[1]
            # name is workName-volumeName. All the files in this 
            # volume have to have the pattern ('*--volName*')
            volNamePattern = "*--" + volName + "*"
            imageFilesGlob = vol.path + os.sep + "image" + os.sep + volNamePattern
            # just look for an iterator. We dont need the results
            import glob
            foundFiles = glob.glob(imageFilesGlob)

            filesAreFound = False
            for img in glob.iglob(imageFilesGlob):
                filesAreFound = True
                break

            if not filesAreFound:
                # If there are no files matching the expression, this is one of the bad directories
                gg = vol.stat()
                modDate = datetime.fromtimestamp(vol.stat().st_ctime).strftime("%B %d, %Y")  # 'January 29, 2017'
                print(batchFolder.name + os.sep + vol.name + os.sep + "image/ from " + modDate + " did not have " + volName)
                volBreak = True

            # No need to process further volumes. One is bad enough
            if volBreak:
                break


if __name__ == "__main__":
    print(sys.version)
    scanBuild()
