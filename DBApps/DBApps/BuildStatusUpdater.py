"""
Update Build Status class
"""

# sys
import sys
import datetime
import os
# usr
from pathlib import Path
from typing import Tuple, Any, Union

from DBAppParser import DbArgNamespace, str2date, DbAppParser, mustExistDirectory
from DBApps.DbApp import DbApp


class UpdateBuildParser(DbAppParser):
    """
    Parser for the Get Ready Related class
    Returns a structure containing fields:
    .drsDbConfig: str (from base class DBAppArgs
    .outline: bool
    .printmaster: bool
    .numResults: int
    .results: str (which will have to resolve to a pathlib.Path
    """

    def __init__(self, description: str, usage: str):
        """
        Constructor. Sets up the arguments
        """
        super().__init__(description, usage)
        self._parser.add_argument("-D", "--delete", action="store_true")
        self._parser.add_argument("buildPath", help='Folder containing batch.xml and objects', type=mustExistDirectory)
        self._parser.add_argument("result", help='String representing the result')
        self._parser.add_argument("buildDate", nargs='?', help='build date. Defaults to time this call was made.',
                                  default=datetime.datetime.now(), type=str2date)


def volumes_for_batch(batch_folder: str) -> list:
    """
    The folders in a batch build project represent the BDRC Volumes in the
    batch build.
    :param batch_folder:
    :return: list of the folders in a batch build project
    """
    for root, dirs, folders in os.walk(batch_folder):
        return dirs


# noinspection PyBroadException
class BuildStatusUpdater(DbApp):
    """
    Sets up build status updating
    """

    def __init__(self, options: DbArgNamespace) -> None:
        """
        :param: self
        :param: options
        :rtype: object
        """
        # drsDbConfig is required
        try:
            super().__init__(options.drsDbConfig)
        except AttributeError:
            print("argument parsing error: drsDbConfig not found in args")
            sys.exit(1)

        self._options = options

    # noinspection PyBroadException
    def do_update(self) -> None:
        """
        Update each volume in the options' build_path
        """
        self.start_connect()
        conn = self.connection

        u_cursor = conn.cursor()
        had_barf = False
        err_vol_persist = ""
        try:
            build_path = self._options.buildPath
            if self._options.delete:
                u_cursor.callproc('DeleteBatchBuild', ( build_path,))
            else:
                # Add or replace the build path
                build_dir: str = os.path.basename(build_path)
                u_cursor.execute(f'insert ignore BuildPaths ( `BuildPath`,`build_dir`) values ("{build_path}","{build_dir}") ;')
                conn.commit()

                # Update each volume
                for volDir in volumes_for_batch(build_path):
                    err_vol_persist = volDir
                    full_build_path = str(Path(build_path).resolve())
                    vol_path: Path = Path(full_build_path, volDir)
                    vol_files, vol_size = self.get_tree_values(str(vol_path))

                    print(f"{volDir}, {build_path}, {self._options.buildDate}, {self._options.result}, {vol_files}, {vol_size}")
                    u_cursor.callproc('UpdateBatchBuild', (
                        volDir, build_path, self._options.buildDate, self._options.result, vol_files, vol_size))
        except Exception:
            import sys
            exc = sys.exc_info()
            print("unexpected error for volume, ", err_vol_persist, exc[0], exc[1], file=sys.stderr)
            conn.rollback()
            had_barf = True
        finally:
            u_cursor.close()
            if not had_barf:
                conn.commit()
            conn.close()

    def get_tree_values(self, path: str) -> Tuple[Union[int, Any], Union[int, Any]]:
        """
        Get file counts on directory and subdirectories.
        :param path: path containing files and folders to be counted
        :returns: total size of files and file count
        :rtype: tuple(int int)
        """

        total: int = 0
        file_count: int = 0

        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                sub_count, sub_total = self.get_tree_values(entry.path)
            else:
                sub_total = entry.stat(follow_symlinks=False).st_size
                sub_count = 1
            total += sub_total
            file_count += sub_count
        return file_count, total
