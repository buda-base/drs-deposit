"""
Base class for all parsers for Db Applications
"""
import argparse
import pathlib
import datetime
import os


class DbArgNamespace:
    """
    Empty arguments, holds output of arg parsing
    """
    pass


class DbAppParser:
    """
    Base class for database arguments. When a subclass calls
    argparse.parseArguments, this class returns a structure containing
    a member drsDbConfig: str
    """
    _parser: argparse.ArgumentParser = None

    _args: DbArgNamespace = None

    def __init__(self, description: str, usage: str):
        self._parser = argparse.ArgumentParser(description=description,
                                               usage="%(prog)s | -d DBAppSection:DbAppFile " + usage)
        self._parser.add_argument('-d', '--drsDbConfig', help='specify section:configFileName', required=True)

    @property
    def parsedArgs(self) -> DbArgNamespace:
        """
        Readonly, calc once
        parses the classes arguments, and returns the namespace
        :return:
        """
        # Enforce once only
        if self._args is None:
            self._args = DbArgNamespace()
            # noinspection PyTypeChecker
            self._parser.parse_args(namespace=self._args)
        return self._args


# section parser validations and utilities


def str2date(arg: str) -> datetime.datetime:
    """
    parses date given in yyyy-mm-dd
    """
    return datetime.datetime.strptime(arg, "%Y-%m-%d")


def writableExpandoFile(path: str):
    """
    argparse type for a file in a writable directory
    :param path:
    :return:
    """

    osPath = os.path.expanduser(path)
    p = pathlib.Path(osPath)
    if os.path.isdir(osPath):
        raise argparse.ArgumentTypeError(f"{osPath} is a directory. A file name is required.")

    # Is the parent writable?
    pDir = p.parent
    if not os.access(str(pDir), os.W_OK):
        raise argparse.ArgumentTypeError(f"{osPath} is in a readonly directory ")

    return path


def mustExistDirectory(path: str):
    """
    Argparse type specifying a string which represents
    an existing file path
    :param path:
    :return:
    """
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError
    for root, dirs, files in os.walk(path, True):
        if len(dirs) == 0:
            raise argparse.ArgumentTypeError
        else:
            return path


def mustExistFile(path: str):
    """
    Common utility. Returns
    :param path:
    :return:
    """
    fullPath = os.path.expanduser(path)
    if not os.path.exists(fullPath):
        raise argparse.ArgumentTypeError
    else:
        return fullPath

# endsection parser validations and utilities
