from workers.accessClasses import CRUDClass as CRUD
import json


class fetchTestTable:
    """Obj to use a read connection and the setDQueryRows to fetch data from the test table"""

    def __init__(self, API_DATA):

        self.API_DATA = API_DATA
        self.crud = CRUD.CRUD()

    def getAPI_DATA(self):
        return self.API_DATA

    def setAPI_DATA(self, new_data):
        self.API_DATA = new_data

    def fetchByPk(self):
        """Method which parses the api data and fetches based on the PK given"""

        try:
            PARSED_DATA = json.loads(self.API_DATA)
        except json.decoder.JSONDecodeError as e:
            raise e

        pk_to_fetch = PARSED_DATA['PersonID']

        sQuery = f"""SELECT * FROM test_table WHERE PersonID = {pk_to_fetch}"""

        row_count = self.crud.setDQueryRows(sQuery)
        row_dict = self.crud.dQueryRows

        data_dict = row_dict[0]

        output_dict = {
            "testTable": data_dict,
            "rowCount": row_count
        }

        return output_dict
