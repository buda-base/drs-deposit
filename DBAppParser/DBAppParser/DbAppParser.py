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

    _default_config: str = 'prod:~/.config/bdrc/db_apps.config'
    _parser: argparse.ArgumentParser = None

    _args: DbArgNamespace = None

    def __init__(self, description: str, usage: str):
        self._parser = argparse.ArgumentParser(description=description,
                                               usage="%(prog)s | -d DBAppSection:DbAppFile " + usage)
        self._parser.add_argument('-d', '--drsDbConfig', help='specify section:configFileName', required=False,
                                  default=self._default_config, type=mustExistDbConfig)

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


def str2datetime(arg: str) -> datetime.datetime:
    """
    parses date given as in bash  date +"%Y-%m-%d %R:%S",
    or 2021-05-24 5:3.22
    """
    return datetime.datetime.strptime(arg, "%Y-%m-%d %H:%M:%S")


def writableExpandoFile(path: str):
    """
    argparse type for a file in a writable directory
    :param path:
    :return:
    """

    os_path = os.path.expanduser(path)
    p = pathlib.Path(os_path)
    if os.path.isdir(os_path):
        raise argparse.ArgumentTypeError(f"{os_path} is a directory. A file name is required.")

    # Is the parent writable?
    p_dir = p.parent
    if not os.access(str(p_dir), os.W_OK):
        raise argparse.ArgumentTypeError(f"{os_path} is in a readonly directory ")

    return path


def mustExistDirectory(path: str):
    """
    Argparse type specifying a string which represents
    an existing file path
    :param path:
    :return:
    """
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"{path} not found")
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
    full_path = os.path.expanduser(path)
    if not os.path.exists(full_path):
        raise argparse.ArgumentTypeError(f"{full_path} not found")
    else:
        return full_path

def mustExistDbConfig(db_config_arg: str):
    """
    Validates that the file, and the section in the file, exist
    :param db_config_arg:
    :return:
    """
    conf_values = db_config_arg.split(":")
    if len(conf_values) < 2:
        raise argparse.ArgumentTypeError(db_config_arg)
    try:
        mustExistFile(conf_values[1])
    except argparse.ArgumentTypeError:
        raise
    return db_config_arg

# end section parser validations and utilities
