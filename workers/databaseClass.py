try:
    from mysql.connector import MySQLConnection, Error
    import configparser
except ImportError as impEr:
    raise impEr


class NoConfigException(Exception):
    """A Custom Execption class to be raised if there is no db config file given to create a db connection"""

class Database:
    """Class meant to be generalised to create a db connection from a given config and perform CRUD operations"""
    def __init__(self, config_file: str = ''):

        self.config_file = config_file

        if not self.config_file:
            raise NoConfigException("No Config File Given")

        self.__post__init__()


    def __post__init__(self) -> None:
        """function to be called by the constructor to perform post-initialisaton tasks"""

        # a dict with numbered keys, each value being a database row - if empty then no rows fetched
        self.dQueryRows: dict = {}

        # an attribute to hold any sql statements
        self.sQuery: str = ''

        # private variables

        # an integer count of the number of rows currently in the dQueryRows dict
        self.__iRowCount: int = 0

        # a string and integer for the last error which occured
        self.__sLastError: str = ''
        self.__iLastError: int = 0

    def __str__(self) -> str:
        return "Database object allowing read and write functions"

    def setLastErrorInt(self, iError: int) -> None:
        self.__iLastError = iError

    def getLastErrorInt(self) -> int:
        return self.__iLastError

    def setLastErrorStr(self, sError: str) -> None:
        self.__sLastError = sError

    def getLastErrorStr(self) -> str:
        return self.__sLastError

    def setRowCount(self, iRowCount: int) -> None:
        self.__iRowCount = iRowCount

    def getRowCount(self) -> int:
        return self.__iRowCount
     
    
    def parse_config(self, section: str = ''):
        """Method to be called which will parse the config file given and return a dict with appropriate db connection information"""

        # creating a parser obj and parsing config
        parser = configparser.ConfigParser()
        parser.read(self.config_file)

        try:
            db = {}
            # if there is a section in our config matching the given section it will be extracted and looped through
            if parser.has_section(section):
                items = parser.items(section)
                for item in items:
                    # this unpacks the tuple into a k/v pair in a dict
                    db[item[0]] = item[1]
            
        except:
            raise Exception(f"{section} is not found in {self.config_file}")

        # return the db dict if no exception raised
        return db 


             
    def read_conn(self):
        """Method to call parse_config method with the section being myRead"""

        db_config = self.parse_config(section="myRead")

        # create a null variable to represent the connection

        conn = None

        try:
            # try creating a connection using a dict as the arg
            conn = MySQLConnection(**db_config)

            if not conn.is_connected():
                print("\n i couldn't connect to the database \n")

        except Error as e:
            raise e

        finally:
            if conn is not None and conn.is_connected():
                return conn

    def write_conn(self):
        """Creates a connection with a user having write permissions"""

        db_config = self.parse_config(section="myWrite")
        conn = None
        try:
            conn = MySQLConnection(**db_config)
            if not conn.is_connected():
                print("\n i couldn't connect to the database")
        except Error as e:
            raise e
        finally:
            if conn is not None and conn.is_connected():
                return conn

    def iSelect(self, key=False):
        """A Method to execute a SELECT statment"""

        # if there are currently rows clear them
        if self.getRowCount():
            self.dQueryRows = {}

        self.setLastErrorInt(0)

        # execute query
        try:
            my_read = self.read_conn()
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

    def setDQueryRows(self, sQuery: str = '', sKey=None) -> int:
        """Method to call the iSelect method on a given sql """
        
        if not "SELECT" in sQuery.upper():
            return "Not a valid select statement"

        # build the query
        self.sQuery = sQuery

        # execute query
        iReturnVal = self.iSelect(sKey)
        return iReturnVal

    def iUpdate(self, sQuery: str = '') -> int:
        """A Method to perform an update from a given sql statement"""

        # check if the update query contains the term update
        if not "UPDATE" in sQuery.upper():
            return "not a valid update statement"

        # assuming the rest of the statement is alright we can execute it

        try:
            my_write = self.write_conn()
            my_cursor = my_write.cursor(dictionary=True)
            my_cursor.execute(sQuery)
            my_write.commit()
            my_cursor.close()
            my_write.close()
            if my_cursor.rowcount == -1:
                return 0
            return my_cursor.rowcount
        except Exception as e:
            self.setLastErrorStr(e)
            print(f"""Query: {sQuery}, 
            Error String: {self.getLastErrorStr()}
            """)
            return -5

    def iDelete(self, sQuery: str = '') -> int:
        """A Method to take a delete query and execute it
        Returning appropriate error should any occur"""

        # check if the statement begins valid
        if "DELETE FROM" not in sQuery.upper():
            return "Not a valid delete statement - delete statements must contain DELETE FROM at the start"

        # assuming the rest of the statement is okay
        try:
            my_write = self.write_conn()
            my_cursor = my_write.cursor(dictionary=True)
            my_cursor.execute(sQuery)
            my_write.commit()
            my_cursor.close()
            my_write.close()
            if my_cursor.rowcount == -1:
                return 0
            return my_cursor.rowcount

        except Exception as e:
            self.setLastErrorStr(e)
            print(f"""Query: {sQuery},
            Error String: {self.getLastErrorStr()}
            """)
            return -10