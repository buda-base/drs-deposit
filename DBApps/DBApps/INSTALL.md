# Installing and running  DBApps 
on a new machine:
1. Install Python 3.6
1. Install venv. (`python3 venv someFolder`) 
1. Put a `. ~/venv/activate`  call into your shell profile. You have to do this, to find 
the virtual environment in your path.
1. Pip install pymysql
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