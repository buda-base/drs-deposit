# DRS Database
## Introduction
The DRS database tracks the status of data entities which are sent to DRS. This
document describes how to access the DRS database. The schema itself is located in the Batches.mwb MySql Workbench Model.
##Prerequisites
### To run DRS transfer programs
A system wishing to use the DRS Database as part of the DRS uploading system needs:
1. `~/drs.cnf` This is a resource file which contains clear text passwords, so is not stored in Git. The DRS system is configured to use credentials contained in this file in this location.
2. Python 3.x. It's highly advised to install the `virtualenv` and `pip` packages, so that project dependent libraries are contained within one system. The DRS packages were developed with python 3.6 Some of the standard connectors MySQLdb, and MySQl's Connector/Python) have compatibility issues [^1]
3. PyMySql plugin. You can find it [here](https://pypi.python.org/pypi/PyMySQL/)

[^1]: MySQLDb has to be built from source on Windows, and the MySQL Connector/Python Python 3.6 support is still a release candidate.

### To administer the Database
If you would like to browse the data, update the schema, update the server (access and permissions), or change a user credentials,  You need everything in the previous item, plus:
1. A Mysql administration utility. The easiest way to acquire this is through MySql Workbench (download it [here](https://dev.mysql.com/downloads/workbench/))
2. (Optional): to perform routine database operations, the MySqlUtilities console is helpful, but not necessary. You can get download information from within MySql workbench Menu Tools | Start Shell for MySqlUtilities  

##Database Functionality
The DRS database provides this information:
1. Which works are ready to be batched?
2. Which works have been batched? When? Did the batch attempt fail?
3. Which volumes are ready to be uploaded?
4. Which volumes are being uploaded?
5. Which volumes have been uploaded? What are their HUL (**H**arvard **U**niversity **L**ibrary) object identifiers?
6. We have a limit on how many files can be uploaded in a day. Have we met that limit?

If a work has related information (references other HUL objects), are those objects uploaded and ready to be linked to?
To support these queries, the database provides these actions:
1. Add an outline
2. Add a work
3. Add a Batch to a volume (links a volume to a work)
4. Update the batch with status (and date and time) and HUL identifier.

## Database maintenance
See [dumpdrs.ps1](bin/win/dumpdrs.ps1) for mysql commands to dump the data separately from the DDL
`dumpdrs.ps1` assumes that you've used `mysql_config_editor` to create a `~/.mylogin.cnf` file.
Its usage is `dumpdrs.ps1 <loginpath> <databasename>` Where `loginpath` is an argument to the `--login-path=<loginPath>` mySql credential.