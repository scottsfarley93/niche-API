__author__ = 'scottsfarley'
import bottle
from bottle import route, run, template, response, request, get, post, delete, put
from bottle import HTTPResponse
import psycopg2
import datetime
import psycopg2.extras


class JSONResponse():
    def __init__(self, data = [], success=True, message = "", status=200, timestamp='auto'):
        self.data = data
        self.sucess = success
        self.message = message
        self.status = status
        if timestamp == 'auto':
            self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.timestamp = timestamp
    def toJSON(self):
        return self.__dict__


def connectToDefaultDatabase():
    hostname = '144.92.235.14'
    db = "paleo"
    pw = 'Alt0Sax!!'
    user = 'paleo'
    conn = psycopg2.connect(host=hostname, user=user, database=db, password=pw)
    return conn


@route("/admin/test-database-connection")
def testConnection():
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT Version()")
    r = JSONResponse()
    for row in cursor.fetchall():
        r['data'].append(row)
    return bottle.HTTPResponse(status=200, body=r)

##Niche Variables
## GET search variables
@get("/variables")
def getVariables():
    variableType = request.query.variableType
    variablePeriod = request.query.variablePeriod
    variablePeriodType = request.query.variablePeriodType
    averagingPeriod = request.query.averagingPeriod
    averagingPeriodType = request.query.averagingPeriodType
    variableUnits = request.query.variableUnits
    if variableType == '':
        variableType = None
    else:
        variableType = variableType.lower()
    if variablePeriod == '':
        variablePeriod = None
    if averagingPeriod == '':
        averagingPeriod = None
    if variablePeriodType == '':
        variablePeriodType = None
    else:
        variablePeriodType = variablePeriodType.lower()
    if averagingPeriodType == '':
        averagingPeriodType = None
    else:
        averagingPeriodType = averagingPeriodType.lower()
    if variableUnits == '':
        variableUnits = None
    else:
        variableUnits = variableUnits.lower()
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
        select variableDescription, variablePeriod, variablePeriodTypes.variablePeriodType, variableUnits.variableUnit,
        variableAveraging, averagingPeriodTypes.averagingPeriodType, variableID, lastUpdate
        from variables
        inner join variableTypes on variables.variableType = variableTypes.variableTypeID
        inner join variableUnits on variables.variableUnits = variableUnits.variableUnitID
        inner join variablePeriodTypes on variables.variablePeriod = variablePeriodTypes.variablePeriodTypeID
        inner join averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID
        WHERE 1 = 1
        AND
            (%(variableType)s is NULL or %(variableType)s LIKE lower(variableTypes.variableTypeAbbreviation) )
            AND  (%(variablePeriod)s is NULL or %(variablePeriod)s = variables.variablePeriod )
             AND (%(variablePeriodType)s is NULL or %(variablePeriodType)s LIKE lower(variablePeriodTypes.variablePeriodType) )
            AND (%(averagingPeriod)s is NULL or %(averagingPeriod)s = variableAveraging )
            AND (%(averagingPeriodType)s is NULL or %(averagingPeriodType)s LIKE lower(averagingPeriodTypes.averagingPeriodType) )
            AND (%(variableUnits)s is NULL or %(variableUnits)s LIKE lower(variableUnits.variableUnitAbbreviation))
        """
    header = ['variableDescription', 'variablePeriod', 'variablePeriodType', 'variableUnits', 'averagingPeriod',
              'averagingPeriodType', 'variableID', 'lastUpdate']
    cursor.execute(query, {'variableType': variableType, 'variablePeriod' : variablePeriod,'variablePeriodType':variablePeriodType,
                           'averagingPeriod' : averagingPeriod, 'averagingPeriodType' : averagingPeriodType, 'variableUnits' : variableUnits})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        d['lastUpdate'] = d['lastUpdate'].strftime("%Y-%m-%d %H:%M:%S")
        out.append(d)
    r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
    return r.toJSON()

## Add a variable
@post("/variables")
def addVariable():
    variableType = request.query.variableType
    variablePeriod = request.query.variablePeriod
    variablePeriodType = request.query.variablePeriodType
    averagingPeriod = request.query.averagingPeriod
    averagingPeriodType = request.query.averagingPeriodType
    variableUnits = request.query.variableUnits
    description = request.query.description

    if variableType == '' or variablePeriod == '' or variablePeriodType == '' or averagingPeriod == '' or averagingPeriodType == '' or variableUnits == '' or description == '':
        r = JSONResponse(data = [], success=False, message = "Not all parameters were specified.  Required parameters: VariableType, variablePeriod: variablePeriodType, averagingPeriod, averagingPeriodType, variableUnits, description", status=400)
        return r.toJSON()
    variableType = variableType.lower()
    variablePeriodType = variablePeriodType.lower()
    averagingPeriodType = averagingPeriodType.lower()
    variableUnits = variableUnits.lower()
    conn = connectToDefaultDatabase()
    print variableType
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
        SELECT variableTypeID FROM variableTypes where lower(variableTypeAbbreviation) = %(variableType)s OR lower(variableType) = %(variableType)s LIMIT 1;
        """
    cursor.execute(query, {'variableType': variableType})
    varTypeID = cursor.fetchone()
    if varTypeID != None:
        varTypeID = varTypeID[0]
    query = '''
        SELECT variablePeriodTypeID from variablePeriodTypes WHERE variablePeriodType=%(variablePeriodType)s LIMIT 1;
        '''
    cursor.execute(query, {'variablePeriodType' : variablePeriodType})
    varPeriodTypeID = cursor.fetchone()
    if varPeriodTypeID is not None:
        varPeriodTypeID = varPeriodTypeID[0]

    query = '''SELECT averagingPeriodTypeID from averagingPeriodTypes where lower(averagingPeriodType)=%(averagingPeriodType)s LIMIT 1;'''
    cursor.execute(query, {'averagingPeriodType': averagingPeriodType})
    averagingTypeID = cursor.fetchone()
    if averagingTypeID is not None:
        averagingTypeID = averagingTypeID[0]

    query = '''SELECT variableUnitID from variableUnits where lower(variableUnitAbbreviation)=%(variableUnit)s OR lower(variableUnit) = %(variableUnit)s LIMIT 1;'''
    cursor.execute(query, {'variableUnit': variableUnits})
    unitID = cursor.fetchone()
    if unitID is not None:
        unitID = unitID[0]

    sql = '''INSERT INTO Variables VALUES (DEFAULT, %(varTypeID)s, %(unitID)s, %(varPeriod)s, %(varPeriodTypeID)s, %(averagingPeriod)s, %(averagingTypeID)s, %(description)s, current_timestamp);'''
    cursor.execute(sql, {'varTypeID':varTypeID, 'unitID':unitID, 'varPeriod':variablePeriod, 'varPeriodTypeID':varPeriodTypeID, 'averagingPeriod':averagingPeriod,
                         'averagingTypeID':averagingTypeID, 'description' : description})
    r = JSONResponse(data=[], success=True, message = cursor.statusmessage, status=201, timestamp='auto')
    conn.commit()
    return bottle.HTTPResponse(status=201, body=r.toJSON())

## Get search variable by ID
@get("/variables/<variableID>")
def getVariableByID(variableID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        select variableDescription, variablePeriod, variablePeriodTypes.variablePeriodType, variableUnits.variableUnit,
        variableAveraging, averagingPeriodTypes.averagingPeriodType, variableID, lastUpdate
        from variables
        inner join variableTypes on variables.variableType = variableTypes.variableTypeID
        inner join variableUnits on variables.variableUnits = variableUnits.variableUnitID
        inner join variablePeriodTypes on variables.variablePeriod = variablePeriodTypes.variablePeriodTypeID
        inner join averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID
        WHERE variables.variableID = %(variableID)s
        """
    header = ['variableDescription', 'variablePeriod', 'variablePeriodType', 'variableUnits', 'averagingPeriod',
              'averagingPeriodType', 'variableID', 'lastUpdate']
    cursor.execute(query, {'variableID': variableID})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    if len(out) == 0:
        r = JSONResponse(data=out, success=False, message = "Variable does not exist.  You can POST a new one to the /variables resource.", status=404, timestamp='auto')
        code = 404
    else:
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
        code = 200
    return bottle.HTTPResponse(status=code, body=r.toJSON())

## PUT an update to a variable
@put("/variables/<variableID>")
def updateVariableByID(variableID):
    variableType = request.query.variableType
    variablePeriod = request.query.variablePeriod
    variablePeriodType = request.query.variablePeriodType
    averagingPeriod = request.query.averagingPeriod
    averagingPeriodType = request.query.averagingPeriodType
    variableUnits = request.query.variableUnits
    description = request.query.description
    ## convert to lower case
    variableType = variableType.lower()
    variablePeriodType = variablePeriodType.lower()
    averagingPeriodType = averagingPeriodType.lower()
    variableUnits = variableUnits.lower()
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if variableType is not None:
        query = """
            SELECT variableTypeID FROM variableTypes where lower(variableTypeAbbreviation) = %(variableType)s OR lower(variableType) = %(variableType)s LIMIT 1;
            """
        cursor.execute(query, {'variableType': variableType})
        varTypeID = cursor.fetchone()
        if varTypeID != None:
            varTypeID = varTypeID[0]
    if variablePeriodType is not None:
        query = '''
            SELECT variablePeriodTypeID from variablePeriodTypes WHERE variablePeriodType=%(variablePeriodType)s LIMIT 1;
            '''
        cursor.execute(query, {'variablePeriodType' : variablePeriodType})
        varPeriodTypeID = cursor.fetchone()
        if varPeriodTypeID is not None:
            varPeriodTypeID = varPeriodTypeID[0]

    if averagingPeriodType is not None:
        query = '''SELECT averagingPeriodTypeID from averagingPeriodTypes where lower(averagingPeriodType)=%(averagingPeriodType)s LIMIT 1;'''
        cursor.execute(query, {'averagingPeriodType': averagingPeriodType})
        averagingTypeID = cursor.fetchone()
        if averagingTypeID is not None:
            averagingTypeID = averagingTypeID[0]

    if variableUnits is not None:
        query = '''SELECT variableUnitID from variableUnits where lower(variableUnitAbbreviation)=%(variableUnit)s OR lower(variableUnit) = %(variableUnit)s LIMIT 1;'''
        cursor.execute(query, {'variableUnit': variableUnits})
        unitID = cursor.fetchone()
        if unitID is not None:
            unitID = unitID[0]

    r = JSONResponse(data = [], message="<<RESOURCE NOT IMPLEMENTED>>", status=501, timestamp='auto')
    return bottle.HTTPResponse(status=501, body=r.toJSON())

## Delete a variable by its id
@delete("/variables/<variableID>")
def deleteVariableByID(variableID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        DELETE FROM variables where
        WHERE variables.variableID = %(variableID)s
        """
    cursor.execute(query, {'variableID': variableID})
    r = JSONResponse(data=[], success=True, message = template("Deleted variable {{variableID}}", variableID=variableID), status=204, timestamp='auto')
    code = 204
    return bottle.HTTPResponse(status=code, body=r.toJSON())



### GET search for variable Types
@get("/variables/variableTypes")
def getVariableTypes():
    abbreviation = request.query.abbreviation
    fullName = request.query.variableName
    if abbreviation == '':
        abbreviation = None
    else:
        abbreviation = abbreviation.lower()
    if fullName == '':
        fullName = None
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
        select variableTypeID, variableType, variableTypeAbbreviation
        from variableTypes
        WHERE 1 = 1
        AND
            (%(abbreviation)s is NULL or %(abbreviation)s LIKE lower(variableTypes.variableTypeAbbreviation) )
            AND  (%(fullName)s is NULL or %(fullName)s = variableTypes.variableType )
        """
    header = ['variableTypeID', 'variableTypeName', 'variableTypeAbbreviation']
    cursor.execute(query, {'fullName': fullName, 'abbreviation' : abbreviation})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
    return bottle.HTTPResponse(status=200, body=r.toJSON())

## Add a new variable Type
@post("/variables/variableTypes")
def addVariableType():
    abbreviation = request.query.abbreviation
    fullName = request.query.variableName
    if abbreviation == '':
        abbreviation = None
    else:
        abbreviation = abbreviation.lower()
    if fullName == '':
        fullName = None
    if fullName is None or abbreviation is None:
        r = JSONResponse(data = [], success=False, message = "Not all parameters were specified.  Required parameters: variableName, abbreviation", status=400)
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''
        INSERT INTO variableTypes VALUES (DEFAULT,%(variableType)s, %(abbreviation)s) RETURNING variableTypeID;
    '''
    cursor.execute(query, {'variableType': fullName, 'abbreviation':abbreviation})
    conn.commit()
    returned = cursor.fetchone()
    returnedID = returned[0]
    r = JSONResponse(data=[], success=True, message = template("Added variables {{variableID}} to the database.", variableID=returnedID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())




## GET search variabletype by variableTypeID
@get("/variables/variableTypes/<variableTypeID>")
def getVariableTypeByID(variableTypeID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        select variableTypeID, variableType, variableTypeAbbreviation
        from variableTypes
        WHERE 1 = 1
        AND
        variableTypeID = %(variableTypeID)s;
        """
    header = ['variableTypeID', 'variableTypeName', 'variableTypeAbbreviation']
    cursor.execute(query, {'variableTypeID': variableTypeID})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    if len(out) == 0:
        r = JSONResponse(data=out, success=False, message = "Variable type does not exist.  You can POST a new one to the /variables/variabletypes resource.", status=404, timestamp='auto')
        code = 404
    else:
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
        code = 200
    return bottle.HTTPResponse(status=code, body=r.toJSON())

## DELETE a variable type
@delete("/variables/variableTypes/<variableTypeID>")
def deleteVariableTypeByID(variableTypeID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        DELETE
        variableTypes
        WHERE 1 = 1
        AND
        variableTypeID = %(variableTypeID)s;
        """
    cursor.execute(query, {'variableTypeID': variableTypeID})
    r = JSONResponse(data=[], success=True, message = template("Deleted variable {{variableTypeID}}", variableTypeID=variableTypeID), status=204, timestamp='auto')
    return bottle.HTTPResponse(status=204, body=r.toJSON())

@put("/variables/variableTypes/<variableTypeID>")
def updateVariableTypeByID(variableTypeID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    abbreviation = request.query.abbreviation
    fullName = request.query.variableName
    if abbreviation == '':
        abbreviation = None
    else:
        abbreviation = abbreviation.lower()
    if fullName == '':
        fullName = None
    query = """
        UPDATE
        variableTypes
        SET variableTypeAbbreviation = %(abbreviation)s,
        variableType = %(variableType)s
        WHERE 1 = 1
        AND
        variableTypeID = %(variableTypeID)s;
        """
    cursor.execute(query, {'variableTypeID': variableTypeID, 'variableType' : fullName, 'abbreviation':abbreviation})
    ## also return details about this item to prove we updated it
    query = '''SELECT * FROM variableTypes WHERE 1=1 AND variableTypeID = %(variableTypeID)s'''
    header = ['variableTypeID', 'variableTypeName', 'variableTypeAbbreviation']
    cursor.execute(query, {'variableTypeID': variableTypeID})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    r = JSONResponse(data=[], success=True, message = template("Updated variable {{variableTypeID}}", variableTypeID=variableTypeID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())



## GET variable units
@get("/variables/variableUnits")
def getVariableUnits():
    abbreviation = request.query.abbreviation
    fullName = request.query.unitName
    if abbreviation == '':
        abbreviation = None
    else:
        abbreviation = abbreviation.lower()
    if fullName == '':
        fullName = None
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
        select variableUnitID, variableUnit, variableUnitAbbreviation
        from variableUnits
        WHERE 1 = 1
        AND
            (%(abbreviation)s is NULL or %(abbreviation)s = lower(variableUnits.variableUnitAbbreviation) )
            AND  (%(fullName)s is NULL or %(fullName)s = variableUnits.variableUnit )
        """
    header = ['variableUnitID', 'variableUnit', 'variableUnitAbbreviation']
    cursor.execute(query, {'fullName': fullName, 'abbreviation' : abbreviation})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
    cursor.close()
    return bottle.HTTPResponse(status=200, body=r.toJSON())

## Add a new variable unit
@post("/variables/variableUnits")
def addVariableUnit():
    abbreviation = request.query.abbreviation
    fullName = request.query.name
    if abbreviation == '':
        abbreviation = None
    else:
        abbreviation = abbreviation.lower()
    if fullName == '':
        fullName = None
    if fullName is None or abbreviation is None:
        r = JSONResponse(data = [], success=False, message = "Not all parameters were specified.  Required parameters: name, abbreviation", status=400)
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''
        INSERT INTO variableUnits VALUES (DEFAULT, %(variableType)s, %(abbreviation)s) RETURNING variableUnitID;
    '''
    cursor.execute(query, {'variableType': fullName, 'abbreviation':abbreviation})
    conn.commit()
    returned = cursor.fetchone()
    returnedID = returned[0]
    r = JSONResponse(data=[], success=True, message = template("Added variable unit {{variableID}} to the database.", variableID=returnedID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())


### GET variable unit by id
@get("/variables/variableUnits/<variableUnitID>")
def getVariableUnitByID(variableUnitID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        select variableUnitID, variableUnit, variableUnitAbbreviation
        from variableUnits
        WHERE 1 = 1
        AND
        variableUnitID = %(variableUnitID)s;
        """
    header = ['variableTypeID', 'variableTypeName', 'variableTypeAbbreviation']
    cursor.execute(query, {'variableUnitID': variableUnitID})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    if len(out) == 0:
        r = JSONResponse(data=out, success=False, message = "Variable unit does not exist.  You can POST a new one to the /variables/variabletypes resource.", status=404, timestamp='auto')
    else:
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
    return bottle.HTTPResponse(status=200, body=r.toJSON())

## DELETE a variable unit
@delete("/variables/variableUnits/<variableUnitID>")
def deleteVariableUnitByID(variableUnitID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        DELETE
        variableUnits
        WHERE 1 = 1
        AND
        variableUnitID = %(variableUnitID)s;
        """
    cursor.execute(query, {'variableUnitID': variableUnitID})
    r = JSONResponse(data=[], success=True, message = template("Deleted variable {{variableUnitID}}", variableUnitID=variableUnitID), status=204, timestamp='auto')
    return bottle.HTTPResponse(status=204, body=r.toJSON())


## Update a variable units entry
@put("/variables/variableTypes/<variableUnitID>")
def updateVariableUnitByID(variableUnitID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    abbreviation = request.query.abbreviation
    fullName = request.query.variableName
    if abbreviation == '':
        abbreviation = None
    else:
        abbreviation = abbreviation.lower()
    if fullName == '':
        fullName = None
    query = """
        UPDATE
        variableTypes
        SET variableUnitAbbreviation = %(abbreviation)s,
        variableUnit = %(variableUnit)s
        WHERE 1 = 1
        AND
        variableUnitID = %(variableUnitID)s;
        """
    cursor.execute(query, {'variableUnitID': variableUnitID, 'variableUnit' : fullName, 'abbreviation':abbreviation})
    ## also return details about this item to prove we updated it
    query = """
        select variableUnitID, variableUnit, variableUnitAbbreviation
        from variableUnits
        WHERE 1 = 1
        variableUnitID = %(variableUnitID)s;
        """
    header = ['variableUnitID', 'variableUnit', 'variableUnitAbbreviation']
    cursor.execute(query, {'variableUnitID': variableUnitID})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    r = JSONResponse(data=out, success=True, message = template("Updated variable unit {{variableUnit}}.", variableUnit=variableUnitID), status=201, timestamp='auto')
    cursor.close()
    return bottle.HTTPResponse(status=201, body=r.toJSON())


## GET Niche Variable Periods
@get("/variables/variablePeriodTypes")
def getVariablePeriodTypes():
    fullName = request.query.name
    if fullName == '':
        fullName = None
    else:
        fullName = fullName.lower()
    print fullName
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
        select *
        from variablePeriodTypes
        WHERE 1 = 1
            AND  (%(fullName)s is NULL or %(fullName)s = variablePeriodtypes.variablePeriodType )
        """
    header = ['variablePeriodID', 'variablePeriodName']
    cursor.execute(query, {'fullName': fullName})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
    return bottle.HTTPResponse(status=200, body=r.toJSON())

## Add a new variable period
@post("/variables/variablePeriodTypes")
def addVariablePeriod():
    abbreviation = request.query.abbreviation
    fullName = request.query.name
    if fullName == '':
        fullName = None
    if fullName is None:
        r = JSONResponse(data = [], success=False, message = "Not all parameters were specified.  Required parameters: name", status=400)
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''
        INSERT INTO variablePeriodTypes VALUES (DEFAULT, %(variablePeriod)s) RETURNING variablePeriodID;
    '''
    cursor.execute(query, {'variablePeriod': fullName})
    conn.commit()
    returned = cursor.fetchone()
    returnedID = returned[0]
    r = JSONResponse(data=[], success=True, message = template("Added variable period {{variableID}} to the database.", variableID=returnedID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())


## GET variable period by ID
@get("/variables/variablePeriodTypes/<variablePeriodID>")
def getVariablePeriodByID(variablePeriodID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        select *
        from variablePeriodTypes
        WHERE 1 = 1
        AND
        variablePeriodTypeID = %(variablePeriodTypeID)s;
        """
    header = ['variablePeriodTypeID', 'variablePeriodType']
    cursor.execute(query, {'variablePeriodTypeID': variablePeriodID})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    if len(out) == 0:
        r = JSONResponse(data=out, success=False, message = "Variable period does not exist.  You can POST a new one to the /variables/variabletypes resource.", status=404, timestamp='auto')
    else:
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
    return r.toJSON()

## DELETE variable period by ID
@delete("/variables/variablePeriodTypes/<variablePeriodID>")
def deleteVariablePeriodByID(variablePeriodID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        delete
        from variablePeriodTypes
        WHERE 1 = 1
        AND
        variablePeriodTypeID = %(variablePeriodTypeID)s;
        """
    header = ['variablePeriodTypeID', 'variablePeriodType']
    cursor.execute(query, {'variablePeriodTypeID': variablePeriodID})
    r = JSONResponse(data=[], success=True, message = "", status=200, timestamp='auto')
    return r.toJSON()

## Update a variable period
@put("/variables/variablePeriodTypes/<variablePeriodID>")
def updateVariablePeriodByID(variablePeriodID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    fullName = request.query.name
    if fullName == '':
        fullName = None
    query = """
        UPDATE
        variablePeriodTypes
        variablePeriodType = %(variablePeriod)s
        WHERE 1 = 1
        AND
        variablePeriodTypeID = %(variablePeriodID)s;
        """
    cursor.execute(query, {'variablePeriodID': variablePeriodID, 'variablePeriod':fullName})
    ## also return details about this item to prove we updated it
    query = """
        select variablePeriodTypeID, variablePeriodType
        from variablePeriodTypes
        WHERE 1 = 1
        variablePeriodTypeID = %(variablePeriodID)s;
        """
    header = ['variablePeriodTypeID', 'variablePeriodType']
    cursor.execute(query, {'variablePeriodID', variablePeriodID})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    r = JSONResponse(data=out, success=True, message = template("Updated variable period {{variablePeriodID}}.", variablePeriodID=variablePeriodID), status=201, timestamp='auto')
    cursor.close()
    return bottle.HTTPResponse(status=201, body=r.toJSON())

## GET Averaging Periods
@get("/variables/averagingTypes")
def getVariablePeriodTypes():
    fullName = request.query.name
    if fullName == '':
        fullName = None
    else:
        fullName = fullName.lower()
    print fullName
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
        select *
        from averagingPeriodTypes
        WHERE 1 = 1
            AND  (%(fullName)s is NULL or %(fullName)s = lower(averagingPeriodTypes.averagingPeriodType) )
        """
    header = ['averagingPeriodID', 'averagingPeriodType', 'averagingPeriodDays']
    cursor.execute(query, {'fullName': fullName})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
    return r.toJSON()

## POST a new averaging type

## Add a new variable period
@post("/variables/averagingTypes")
def addAveragingType():
    numDays = request.query.days
    fullName = request.query.name
    if fullName == '':
        fullName = None
    if numDays == '':
        numDays = None
    if fullName is None or numDays is None:
        r = JSONResponse(data = [], success=False, message = "Not all parameters were specified.  Required parameters: name, days", status=400)
        return bottle.HTTPResponse(status=400, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''
        INSERT INTO averagingPeriodTypes VALUES (DEFAULT, %(periodTypeName)s, %(numDays)s) RETURNING averagingPeriodTypeID;
    '''
    cursor.execute(query, {'periodTypeName': fullName, 'numDays':numDays})
    conn.commit()
    returned = cursor.fetchone()
    returnedID = returned[0]
    r = JSONResponse(data=[], success=True, message = template("Added averaging period {{variableID}} to the database", variableID=returnedID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())

## GET averaging type by ID
@get("/variables/averagingTypes/<averagingTypeID>")
def getAveragingTypeByID(averagingPeriodTypeID):
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        select *
        from averagingPeriodType
        WHERE 1 = 1
        AND
        averagingPeriodTypeID = %(averagingPeriodTypeID)s;
        """
    header = ['averagingPeriodID', 'averagingPeriodType', 'averagingPeriodDays']
    cursor.execute(query, {'averagingPeriodTypeID': averagingPeriodTypeID})
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    if len(out) == 0:
        r = JSONResponse(data=out, success=False, message = "Variable period does not exist.  You can POST a new one to the /variables/variabletypes resource.", status=404, timestamp='auto')
    else:
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
    return r.toJSON()

## DELETE an averaging period type from the database





run(host='localhost', port=8000, debug=True)
