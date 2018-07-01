from unittest import TestCase
from DBApps.SourceProcessors import WebAdminResults


# noinspection PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException
class TestWebAdminResults(TestCase):

    def test_WebAdminResults_empty_parm(self):

        hadbarf = False
        try:
            w = WebAdminResults.WebAdminResults("")
        except:
            hadbarf = True
        self.assertTrue(hadbarf)

    def test_WebAdminResults_emptyList(self):
        hadbarf = False
        try:
            elist = []
            w = WebAdminResults.WebAdminResults("")
        except:
            hadbarf = True
        self.assertTrue(hadbarf)

    def test_WebAdminResults_empty_list_value(self):
        hadbarf = False
        try:
            elist = [""]
            w = WebAdminResults.WebAdminResults("")
        except:
            hadbarf = True
        self.assertTrue(hadbarf, 'expected empty list value to fail')

    def test_find_columns_Empty(self):
        """
        Expect success when there is one entry, which matches the input
        :return:
        """
        w = WebAdminResults.WebAdminResults("_")
        hadbarf = False
        try:
            w.find_columns("")
        except:
            hadbarf = True
        self.assertTrue(hadbarf,"empty test string should fail")

    def test_find_columns_one(self):
        """
        Expect exception when one entry doesnt match
        :return:
        """
        ss = [("s1","p1")]
        w = WebAdminResults.WebAdminResults("_")
        self.assertRaises(ValueError, w.find_columns, "s2")

    def test_find_columns_some(self):
        """
        Expect exception when one entry doesnt match
        :return:
        """
        w = WebAdminResults.WebAdminResults("_")
        self.assertRaises(ValueError, w.find_columns, "s2")

    def test_find_columns_all(self):
        """
        Expect success when there all entries match, which matches the input
        :return:
        """
        w = WebAdminResults.WebAdminResults("_")
        w.find_columns("s2_s1_s3")

    def test_find_columns_ColsNoCommas(self):
        """
        Should fail test of Some columns, no commas
        :return:
        """
        w = WebAdminResults.WebAdminResults(",")
        self.assertRaises(ValueError, w.find_columns, "object_id_num_object_huldrsadmin_ownerSuppliedName_string") # , 'Should have thrown')

    def test_extract(self):
        w = WebAdminResults.WebAdminResults(",")
        w.find_columns("s6,s1,s7,s2")
        cmd_bead = w.extract_data("heemalator, ImanS1, freemalator, ImanS2")
        print(cmd_bead)
