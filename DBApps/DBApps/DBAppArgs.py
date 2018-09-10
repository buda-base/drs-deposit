"""

"""
import argparse
import pathlib


class DbArgNamespace:
    """
    Empty arguments, holds output of arg parsing
    """
    pass


class DBAppArgs:
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
        self._parser.add_argument('-d', '--drsDbConfig',
                                  help='specify section:configFileName', required=True)

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


def writableExpandoFile(path: str):
    """
    argparse type for a file in a writable directory
    :param path:
    :return:
    """
    import os
    osPath = os.path.expanduser(path)
    p = pathlib.Path(osPath)
    if os.path.isdir(osPath):
        raise argparse.ArgumentTypeError(f"{osPath} is a directory. A file name is required.")

    # Is the parent writable?
    pDir = p.parent
    if not os.access(str(pDir), os.W_OK):
        raise argparse.ArgumentTypeError(f"{osPath} is in a readonly directory ")

    return path
