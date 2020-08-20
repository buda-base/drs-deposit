"""
@author: jimk
Updates build status
"""

from DBApps.BuildStatusUpdater import UpdateBuildParser, BuildStatusUpdater
from DBApps.DbAppParser import DbArgNamespace


def SetupParse() -> object:
    p = UpdateBuildParser(description='Updates the build status of a work',
                          usage=" buildPath result [buildDate]")
    return p.parsedArgs


def updateBuildStatus():
    """
    Entry point for getting works
    :return:
    """
    ubArgs: DbArgNamespace = SetupParse()
    updater = BuildStatusUpdater(ubArgs)
    updater.do_update()


if __name__ == '__main__':
    updateBuildStatus()
