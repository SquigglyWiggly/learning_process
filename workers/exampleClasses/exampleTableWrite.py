from workers.common import updateClause as UC
from workers.common import whereClause as WC
from workers.exampleClasses.exampleTableRead import tableRead
import time

class tableWrite(tableRead):
    def __init__(self, iTableRef=0):
        tableRead.__init__(self, iTableRef=0)

        # public
        self.dInsertFails = {} # dict of rows that failed to insert

        # privates
        self.__iNextInsert = 0 # PK used to insert the next insert row
        self.__iTopSeq = 0 
        self.__iSeqIncrement = 10

        if self.iTableRef == None:
            return
        super().setITableRef(iTableRef)
        super().setIntLastError(super().setTableRow())
    
    def __str__(self):
        return f"""Table {self.iTableRef}"""

    def setNextInsert(self, iNextInsert):
        self.__iNextInsert = iNextInsert
    
    def getNextInsert(self):
        return self.__iNextInsert

    def setTopSeq(self, iTopSeq):
        self.__iTopSeq = iTopSeq

    def getTopSeq(self):
        return self.__iTopSeq

    def iUpdate(self, bUpdateLocal=False):
        
        # Execute Query
        retry = 10
        while True:
            if retry == 0:
                break
            try:
                myWrite = super().db.write_conn()
                myCursor = myWrite.cursor()
                myCursor.execute(self.sQuery)

                self.iUpdates = myCursor.rowcount
                if bUpdateLocal and self.iUpdates:
                    sWhereClause = self.sQuery[super().sQuery.index("WHERE"):]
                    self.sQuery = f"""SELECT * FROM table {sWhereClause}"""
                    self.iUpdates = super().iSelect()
            except Exception as e:
                myWrite.rollback()
                if (e.errno == 1205 and retry > 0):
                    retry -= 1
                    time.sleep(0.125)
                    continue
                else:
                    super().setStrLastError(e)
                    sErrorString = f"\nlastError: {super().getIntLastError()}\nlastCode: {super().getStrLastError()}\n"
                    raise
        
        myCursor.close()
        myWrite.close()

    def updateTable(self, dCriteria, dNewValues, bUpdateLocal=False):

        # build update clause
        # builds clause or uses a passed in one
        if isinstance(dNewValues, dict):
            myUpdate = UC.updateClause()
            sUpdateClause = myUpdate.getUpdateClause(dNewValues)
        else:
            sUpdateClause = dNewValues

        # build where clause
        # builds one or uses passed in one
        if isinstance(dCriteria, dict):
            myWhere = WC.whereClause()
            sWhereClause = myWhere.getWhereClause(dCriteria)
        else:
            sWhereClause = dCriteria

        self.sQuery = f"UPDATE table SET {sUpdateClause} WHERE {sWhereClause}"

        iNumRows = self.iUpdate(bUpdateLocal)

        return iNumRows