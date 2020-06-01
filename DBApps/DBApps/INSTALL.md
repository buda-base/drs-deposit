# Installing and running  DBApps 
on a new machine:
1. Install Python 3.6 or 3.7
1. Install venv. (`python3 venv someFolder`) 
1. Put a `. ~/venv/activate`  call into your shell profile. You have to do this, to find 
the virtual environment in your path.
1. Pip install pymysql
1. Copy from an existing shell directory:
    * ~/.drsBatch.Config
    * my.cnf
    * `ln -s ~/my.cnf ~/drs.cnf` (That’s ell-n, as in link)

1. There are two ways to install DBApps.
   1. Install DBApps from pip3 (`python3 -m pip show DBApps` will give you the pyPI information.
   For details on how DBApps builds this, see `drs-deposit/DBApps/setup.py` This is the preferred approach, because it 
   installs a known version.
   1. Fetch the source code from the drs-deposit 
```
$ cd ~/drs-deposit/DBApps
$ python setup.py install
```
And then run the utilities from the command line. This is only for developers.
