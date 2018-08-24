"""

"""
import argparse


class Args:
    """
    Empty arguments, holds output of arg parsing
    """
    pass


class DBAppArgs:
    """
    Base class for database arguments. Provides a config to access
    dbconfigs
    """
    _parser: argparse.ArgumentParser = None

    _args: Args = None

    def __init__(self, description: str, usage: str):
        _parser = argparse.ArgumentParser(description=description,
                                          usage="%(prog)s | -d DBAppSection:DbAppFile " + usage)
        _parser.add_argument('-d', '--drsDbConfig',
                             help='specify section:configFileName', required=True)

    @property
    def parsedArgs(self) -> Args:
        """
        Readonly, calc once
        parses the classes arguments, and returns the namespace
        :return:
        """
        # Enforce once only
        if self._args is None:
            # noinspection oyTypeChecker
            self._parser.parse_args(namespace=self._args)
        return self._args

