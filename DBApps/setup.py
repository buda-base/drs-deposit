from setuptools import setup

setup(
    name='DBApps',
    version='0.42',
    packages=['', 'DBApp', 'DBApp.Tests', 'GenShell', 'GenShell.Writers', 'GenShell.GenShellTests',
              'GenShell.SourceProcessors'],
    package_dir={'': 'src'},
    url='',
    license='ToKill',
    author='jimk',
    author_email='jimk@tbrc.org',
    description='Utilities for DB Access'
)
