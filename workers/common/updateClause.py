class updateClause:

    def __init__(self):

        self.__myUpdateClause = "a"
        self.__myUpdateCount = 0

    def __buildUpdateClause(self, myVal, myKey):
        """Function to build SQL UPDATE clause from a passed in dictionary of criteria
        """

        if isinstance(myVal, str):
            if myVal.isnumeric():
                sep = ""
            else:
                sep = "'"
        else:
            sep = ""

        if isinstance(myVal, str):
            useVal = myVal
        else:
            useVal = f'{myVal}'

        if not self.__myUpdateCount:
            self.__myUpdateClause = f"{myKey} = {sep}{useVal}{sep}"
        else:
            self.__myUpdateClause += f" , {myKey} = {sep}{useVal}{sep}"

        self.__myUpdateCount += 1

    def getUpdateClause(self, aCriteria):
        """Return an update clause based on the passed in criteria dict

        Args:
            aCriteria Dict: dict of key-value pairs to search on, key being column name and value being the criteria for that column
        """

        for myKey, myVal in aCriteria.items():
            self.__buildUpdateClause(myVal, myKey)

        return self.__myUpdateClause
