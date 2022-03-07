from workers.accessClasses.databaseClass import Database
from workers.common import whereClause as WC
from mysql.connector import Error

class tableRead:
    def __init__(self, iTableRef=0, bFetchDefaults=False):
        
        # database
        self.db = Database("./workers/common/config.ini")

        # public
        self.dTableRows = {}
        self.dTableRefs = {}

        # protected
        self.iTableRef = 0
        self.sQuery = ''
        self.bFetchDefaults = bFetchDefaults

        # private
        self.__iTableCount = 0
        self.__sLastError = ''
        self.__iLastError = 0

        if iTableRef == None:
            return
        
        self.setITableRef(iTableRef)
        
        # set the dict with the values for this ref
        self.setIntLastError(self.setTableRow())

    def __str__(self):
        return f"Table {self.iTableRef}"

    def setIntLastError(self, iErrorRef):
        self.__iLastError = iErrorRef
    
    def getIntLastError(self):
        return self.__iLastError

    def setStrLastError(self, sError):
        self.__sLastError = sError

    def getStrLastError(self):
        return f'{self.__sLastError}'

    def setRowCount(self, iRowCount):
        self.__iTableCount = iRowCount

    def getRowCount(self):
        return self.__iTableCount

    def setITableRef(self, iTableRef):

        if not isinstance(iTableRef, int):
            self.setIntLastError(400)
            lastStr = f"""The passed in PK was not an integer value - {int(iTableRef)}"""
            return "Error Code: 400 Bad Input"

        self.iTableRef = iTableRef
        return self.iTableRef

    def iSelect(self, key=False):

        # clear any existing publics
        if self.getRowCount():
            self.dTableRefs = {}
            self.dTableRows = {}

        self.setIntLastError(0)

        # execute the query
        try:
            myRead = self.db.read_conn()
            myCursor = myRead.cursor(dictionary=True)
            myCursor.execute(self.sQuery)

            self.dTableRows = myCursor.fetchall()
            self.__iTableCount = myCursor.rowcount
            self.setIntLastError(self.__iTableCount)
            myCursor.close()
            myRead.close()
        except Exception as e:
            self.setStrLastError(e)
            raise

        if not self.__iTableCount:
            return "no rows found"
        else:
            iCount = 0
            for row in self.dTableRows:
                if not key:
                    iIndex = iCount
                else:
                    iIndex = row[key]
                
                self.aTableRows[iIndex] = row
                if row['tableRef']:
                    self.dTableRefs[iIndex] = row['tableRef']
                iCount += 1

        if iCount == self.__iTableCount:
            self.setRowCount(iCount)
            return self.__iTableCount
        else:
            self.setIntLastError(100)
            self.setStrLastError("Fetch mismatched")
            return "Fetch mismatch"

    def setTableRows(self, dCriteria, sKey=None, sOrderBy='', iMaxRows=0):

        # clear existing publics if filled
        if self.getRowCount():
            self.dTableRefs = {}
            self.dTableRows = {}

        # build query from passed in criteria
        if not dCriteria:
            self.setIntLastError(400)
            self.setStrLastError("Invalid criteria dict")
            return "Invalid where clause criteria"

        myWhereClause = WC.whereClause()
        sWhereClause = myWhereClause.getWhereClause(dCriteria)
        if self.bFetchDefaults == False:
            sWhereClause = f'tableRef > 1000 AND {sWhereClause}'

        self.sQuery = f"SELECT * FROM table WHERE {sWhereClause}"
        if sOrderBy:
            self.sQuery += f" {sOrderBy}"
        if iMaxRows:
            self.sQuery += f" LIMIT {iMaxRows}"
        
        # execute query

        iRetVal = self.iSelect(sKey)

        return iRetVal

    def setTableRow(self):
        
        self.sQuery = f"""SELECT * FROM table WHERE tableRef = {self.iTableRef}"""
        iNumRows = self.iSelect()
        if iNumRows == 1:
            iRetVal = self.dTableRows[0]["tableRef"]
        elif iNumRows == 0:
            iRetVal = 0
            self.setIntLastError(0)
            self.setStrLastError(f"No matching rows found for iTableRef = {self.iTableRef}")
        else:
            iRetVal = iNumRows

        return iRetVal
    
    def setTableRowsFree(self, sCriteria, sKey=None):
        
        # clear publics
        if self.getRowCount():
            self.dTableRows = {}
            self.dTableRefs = {}

        # build the query
        self.sQuery = f"SELECT * FROM table WHERE {sCriteria}"

        iRetVal = self.iSelect(sKey)

        return iRetVal

