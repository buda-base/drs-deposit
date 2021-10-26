import unittest

from DBApps.DbApp import DbApp


class MyTestCase(unittest.TestCase):
    def test_CallLogMigrationExists(self):
        testing_app: DbApp = DbApp('qa:~/.drsBatch.config')
        sproc_rc = testing_app.CallAnySproc("migrate.LogMigrationExists", "arg1", "arg2", "arg3")

        self.assertEqual(len(sproc_rc[0]), 0)

    def test_CallDIPActivityUsingQA(self):
        testing_app: DbApp = DbApp('qa:~/.config/bdrc/db_apps.config')
        sproc_return: [] = testing_app.CallAnySproc("GetDIPActivityCandidates", "SINGLE_ARCHIVE_REMOVED")

        # You have to go into the DRSQA DB and
        # Update DIP_config set DIP_CONFIG_VALUE = 2 where idDIP_CONFIG = 'PRUNE_ACT_LIMIT'
        self.assertEqual(len(sproc_return[0]), 2)

    def test_query(self):
        """
        Tests that a query runs and returns a row
        """
        testing_app: DbApp = DbApp('qa:~/.config/bdrc/db_apps.config')
        sdt = testing_app.ExecQuery("Select * from dip_activity  order by update_time desc limit 5")
        self.assertEqual(len(sdt[0]), 5)


if __name__ == '__main__':
    unittest.main()
