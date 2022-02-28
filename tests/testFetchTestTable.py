from workers.baseClasses.testTableFetch import fetchTestTable
import json
import unittest


class testFetchTestTable(unittest.TestCase):

    def testFetchByPK(self):

        td = '''{
            "PersonID": 0
            }'''

        prsn_id = json.loads(td)['PersonID']
        fetch_obj = fetchTestTable(td)
        check = fetch_obj.fetchByPk()


        if check['testTable']['PersonID'] != prsn_id:
            self.fail(msg="a record other than the one asked for was fetched")
        elif check['rowCount'] > 1 or check['rowCount'] < 1:
            self.fail(msg="incorrect record count returned")
