class whereClause:

    def __init__(self):
        self.__myWhereClause = 'a'
        self.__myWhereCount = 0

    def __buildWhereClause(self, myVal, myKey):

        bCryptString = False
        inString = ''

        count = 0

        if isinstance(myVal, list):
            for val in myVal:
                if isinstance(val, str):
                    if val.isnumeric():
                        sep = ""
                    elif val[:5] == "CRYPT":
                        bCryptString = True
                        val = val[5:]
                        sep = "'"
                    else:
                        sep = "'"
                else:
                    sep = ""

                if isinstance(val, str):
                    useVal = val
                else:
                    useVal = f'{val}'

                if not count:
                    inString += f"{sep}{useVal}{sep}"
                else:
                    inString += f",{sep}{useVal}{sep}"
                count += 1

            if not self.__myWhereCount:
                if bCryptString:
                    self.__myWhereClause = f"{myKey} = password({sep}{useVal}{sep})"
                else:
                    self.__myWhereClause = f"{myKey} IN ({inString})"
            else:
                if bCryptString:
                    self.__myWhereClause += f" AND {myKey} = password({sep}{useVal}{sep})"
                else:
                    self.__myWhereClause += f" AND {myKey} IN ({inString})"

        else:
            if isinstance(myVal, str):
                if myVal.isnumeric():
                    sep = ""
                elif myVal[:5] == "CRYPT":
                    bCryptString = True
                    myVal = myVal[5:]
                    sep = "'"
                else:
                    sep = "'"

            else:
                sep = ""

            if isinstance(myVal, str):
                useVal = myVal
            else:
                useVal = f'{myVal}'

            if not self.__myWhereCount:
                if bCryptString:
                    self.__myWhereClause = f"{myKey} = password({sep}{useVal}{sep})"
                else:
                    self.__myWhereClause = f"{myKey} = {sep}{useVal}{sep}"
            else:
                if bCryptString:
                    self.__myWhereClause += f" AND {myKey} = password({sep}{useVal}{sep})"
                else:
                    self.__myWhereClause += f" AND {myKey} = {sep}{useVal}{sep}"

        self.__myWhereCount += 1

    def getWhereClause(self, aCriteria):
        '''
        Name: getWhereClause

        Purpose:
        return a where clause based on passed in criteria dictionary

        Params:
        aCriteria - a dict of key-value pairs to search on, where the key is the column name, value is the criteria for that column

        if the value starts with CRYPT it will be treated as a mysql password search

        Returns:
        string containing WHERE clause
        '''

        for myKey, myVal in aCriteria.items():
            self.__buildWhereClause(myVal, myKey)

        return self.__myWhereClause
