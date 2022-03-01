from datetime import datetime
from flask import abort
from workers.baseClasses import testTableFetch as TF
from flask import request
import json

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

def get_all():
    """
    Function responds to request to api/exmaple/getExample

    Will return all rows in the test table.
    """

    jNew = json.dumps(request.json)
    getExamples = TF.fetchTestTable(jNew)
    aRetVals = getExamples.fetchByPk()
    if aRetVals['errorCode'] < 0:
        abort(404, aRetVals['errorCode'])
    return aRetVals