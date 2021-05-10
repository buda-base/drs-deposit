import unittest
from DBApps.DbApp import  DbApp, DBConfig

class MyTestCase(unittest.TestCase):
    def test_CallLogMigrationExists(self):
        testing_app:DbApp = DbApp('prod:~/.drsBatch.config')
        rc: int = -1
        sproc_rc = testing_app.CallAnySproc("migrate.LogMigrationExists", "arg1","arg2","arg3")


if __name__ == '__main__':
    unittest.main()
