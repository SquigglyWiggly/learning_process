try:
    from mysql.connector import Error
    from workers.accessClasses.databaseClass import Database, NoConfigException
except ImportError as er:
    raise er



class CRUD:
    """A Class which will create database connection object and allow CRUD operations to be done"""
    def __init__(self):
        
        # we'll assume that the config will be the same for the db throughout
        self.db = Database('../workers/common/config.ini')
        
        self.__post__init__()
        
    def __post__init__(self):
        """function to be called by the constructor to perform post-initialisaton tasks"""

        # a dict with numbered keys, each value being a database row - if empty then no rows fetched
        self.dQueryRows = {}

        # an attribute to hold any sql statements
        self.sQuery = ''

        # private variables

        # an integer count of the number of rows currently in the dQueryRows dict
        self.__iRowCount = 0

        # a string and integer for the last error which occured
        self.__sLastError = ''
        self.__iLastError = 0
        
    def getReadConnection(self):
        return self.db.read_conn()
    
    def getWriteConnection(self):
        return self.db.write_conn()

    def setLastErrorInt(self, iError):
        self.__iLastError = iError

    def getLastErrorInt(self):
        return self.__iLastError

    def setLastErrorStr(self, sError):
        self.__sLastError = sError

    def getLastErrorStr(self):
        return self.__sLastError

    def setRowCount(self, iRowCount):
        self.__iRowCount = iRowCount

    def getRowCount(self):
        return self.__iRowCount
    
    def iSelect(self, key=False):
        """A Method to execute a SELECT statment"""

        # if there are currently rows clear them
        if self.getRowCount():
            self.dQueryRows = {}

        self.setLastErrorInt(0)

        # execute query
        try:
            my_read = self.getReadConnection()
            my_cursor = my_read.cursor(dictionary=True)
            my_cursor.execute(self.sQuery)

            self.dTableRows = my_cursor.fetchall()
            iRecordCount = my_cursor.rowcount
            self.setLastErrorInt(iRecordCount)
            my_cursor.close()
            my_read.close()
        except Exception as e:
            self.setLastErrorStr(e)
            return -1

        if not iRecordCount:
            # if there is no records
            self.setRowCount(0)
            return 0
        
        iCount = 0
        for row in self.dTableRows:
            if not key:
                iIndex = iCount
            else:
                iIndex = row[key]
            
            # index the rows in the query rows dict
            self.dQueryRows[iIndex] = row
            iCount += 1

        # if there is an issue where the number of rows indexed is not the same as the number of rows returned then return an error code
        if not (iCount == iRecordCount):
            self.setLastErrorInt(-1)
            self.setLastErrorStr("fetch mismatch")
            return -1
        
        # otherwise set the row count and return it
        self.setRowCount(iRecordCount)
        return iRecordCount

    def setDQueryRows(self, sQuery: str, sKey=None):
        """Method to call the iSelect method on a given sql """
        
        if "SELECT" not in sQuery.upper():
            return "Not a valid select statement"

        # build the query
        self.sQuery = sQuery

        # execute query
        iReturnVal = self.iSelect(sKey)
        return iReturnVal

    def iUpdate(self, sQuery: str):
        """A Method to perform an update from a given sql statement"""

        # check if the update query contains the term update
        if not "UPDATE" in sQuery.upper():
            return "not a valid update statement"

        # assuming the rest of the statement is alright we can execute it

        try:
            my_write = self.getWriteConnection()
            my_cursor = my_write.cursor(dictionary=True)
            my_cursor.execute(sQuery)
            my_write.commit()
            my_cursor.close()
            my_write.close()
            if my_cursor.rowcount == -1:
                return 0
            return my_cursor.rowcount
        except Exception as e:
            my_write.rollback()
            self.setLastErrorStr(e)
            print(f"""Query: {sQuery}, 
            Error String: {self.getLastErrorStr()}
            """)
            return -5

    def iDelete(self, sQuery: str):
        """A Method to take a delete query and execute it
        Returning appropriate error should any occur"""

        # check if the statement begins valid
        if "DELETE FROM" not in sQuery.upper():
            return "Not a valid delete statement - delete statements must contain DELETE FROM at the start"

        # assuming the rest of the statement is okay
        try:
            my_write = self.getWriteConnection()
            my_cursor = my_write.cursor(dictionary=True)
            my_cursor.execute(sQuery)
            my_write.commit()
            my_cursor.close()
            my_write.close()
            if my_cursor.rowcount == -1:
                return 0
            return my_cursor.rowcount

        except Exception as e:
            my_write.rollback()
            self.setLastErrorStr(e)
            print(f"""Query: {sQuery},
            Error String: {self.getLastErrorStr()}
            """)
            return -10
    
    def iInsert(self, sQuery: str):
        """Method to take a query and execute it"""

        # check if the query has the correct parts
        if "INSERT INTO" not in sQuery:
            return "INSERT INTO not in insert statement"
        elif "VALUES" not in sQuery:
            return "VALUES not after INSERT INTO"
        
        # assuming the rest of the statement is fine execute it
        try:
            my_write = self.getWriteConnection()
            my_cursor = my_write.cursor()
            my_cursor.execute(sQuery)
            my_write.commit()
            my_cursor.close()
            my_write.close()
        except Exception as e:
            my_write.rollback()
            self.setLastErrorStr(e)
            print(f"""Query: {sQuery} 
            Error String: {self.getLastErrorStr()}""")
            raise


        