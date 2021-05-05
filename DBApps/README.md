# bdrc-DBApps
Package which runs various DB apps in the BDRC HUL DRS environment.
Except for its daring, unique, and confusing way of cloaking MySql connections,
nothing major to see here.

# Installing and running  DBApps 
## Installing non-data files
Copy from an existing shell directory:
    * ~/.drsBatch.Config
    * drs.cnf

## Packaged Installation
This is the recommended installation to get a released version. Python 3.7 or later is a pre-requisite (the installation
checks).
You can either install this for yourself or all users (the user level `pip install` command is a little confusing, because
it writes the application libraries globally, but hides the console scripts in your local directory)
`pip install bdrc-DBApps`
or 
`sudo pip install bdrc-DBApps`
to install for global users.

Detailed information is at [pyPI.org bdrc-DBApps project page](https://pypi.org/project/bdrc-DBApps/)
## Source Installation
on a new machine:
1. Install Python 3.7 - 3.9
1. Install venv. (`python3 venv someFolder`) 
1. Create a virtual environment
1. Add an `activate` statement for that environment, 
1. Download the source code from [Github](https://github.com/buda-base/drs-deposit.git)
1. Then GIT Fetch the latest ~/drs-output/DBApps, and:
```
$ cd ~/drs-deposit/DBApps
$ python setup.py install
```
And then run the utilities from the command line. 
