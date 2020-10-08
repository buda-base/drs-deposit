# bdrc-DBApps
Package which runs various DB apps in the BDRC HUL DRS environment.
Except for its daring, unique, and confusing way of cloaking MySql connections,
nothing major to see here.

# Installing and running  DBApps 
on a new machine:
1. Install Python 3.7 or 3.8
1. Install venv. (`python3 venv someFolder`) 
1. Put a `. ~/venv/activate`  call into your shell profile. You have to do this, to find 
the virtual environment in your path.
1. Pip install bdrc-DBApps (will install prerequisites)
1. Copy from an existing shell directory:
    * ~/.drsBatch.Config
    * my.cnf
    * `ln -s ~/my.cnf ~/drs.cnf` (That’s ell-n, as in link)
1. Then GIT Fetch the latest ~/drs-output/DBApps, and:
```
$ cd ~/drs-deposit/DBApps
$ python setup.py install
```
And then run the utilities from the command line. 