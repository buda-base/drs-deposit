from unittest import TestCase
from GenShell.SourceProcessors import WebAdminResults


class TestWebAdminResults(TestCase):

    def test_WebAdminResults_empty_parm(self):

        hadbarf = False
        try:
            w = WebAdminResults.results()
        except:
            hadbarf = True
        self.assertTrue(hadbarf)

    def test_WebAdminResults_emptyList(self):
        hadbarf = False
        try:
            elist = []
            w = WebAdminResults.results("", elist)
        except:
            hadbarf = True
        self.assertTrue(hadbarf)

    def test_WebAdminResults_empty_list_value(self):
        hadbarf = False
        try:
            elist = [""]
            w = WebAdminResults.results("", elist)
        except:
            hadbarf = True
        self.assertTrue(hadbarf, 'expected empty list value to fail')

    def test_find_columns_Empty(self):
        """
        Expect success when there is one entry, which matches the input
        :return:
        """
        w = WebAdminResults.results("_", ["s1"])
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
        ss = ["s1"]
        w = WebAdminResults.results("_", ss)
        self.assertRaises(ValueError, w.find_columns, "s2") # , "Expected to throw when s1 not found.")

    def test_find_columns_some(self):
        """
        Expect exception when one entry doesnt match
        :return:
        """
        w = WebAdminResults.results("_", ["s1"])
        self.assertRaises(ValueError, w.find_columns,"s2") # "Expected to throw when s1 not found.")

    def test_find_columns_all(self):
        """
        Expect success when there all entries match, which matches the input
        :return:
        """
        w = WebAdminResults.results("_", ["s1", "s2", "s3"])
        w.find_columns("s2_s1_s3")

    def test_find_columns_ColsNoCommas(self):
        """
        Should fail test of Some columns, no commas
        :return:
        """
        w = WebAdminResults.results(",", ["s1", "s2"])
        self.assertRaises(ValueError, w.find_columns, "object_id_num_object_huldrsadmin_ownerSuppliedName_string") # , 'Should have thrown')
