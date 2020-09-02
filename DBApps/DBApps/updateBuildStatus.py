"""
@author: jimk
Updates build status
"""

from DBApps.BuildStatusUpdater import UpdateBuildParser, BuildStatusUpdater
from DBApps.DbAppParser import DbArgNamespace


def setup_parse() -> object:
    p = UpdateBuildParser(description='Updates the build status of a work',
                          usage=" buildPath result [buildDate]")
    return p.parsedArgs


def update_build_status():
    """
    Entry point for getting works
    :return:
    """

    ub_args: DbArgNamespace = setup_parse()
    updater = BuildStatusUpdater(ub_args)

    if ub_args.delete and str(ub_args.result).upper() != 'FAIL':
        print(f" No update performed. You specified build result {ub_args.result} and --delete. Will only delete when result is \'fail\' (or \'FAIL\')")

    updater.do_update()


if __name__ == '__main__':
    update_build_status()
