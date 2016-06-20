__author__ = 'scottsfarley'

## import the bottle module for request routing
import bottle
from bottle import route, run, template, response, request, get, post, delete, put, hook
import psycopg2 ## database connector
import datetime ## for timestamp formatting
import psycopg2.extras ## for dict cursor, but not really working
import numpy
import math
import json

bottle.BaseRequest.MEMFILE_MAX = 9999999999999

_allow_origin = '*'
_allow_methods = 'PUT, GET, POST, DELETE, OPTIONS'
_allow_headers = 'Authorization, Origin, Accept, Content-Type, X-Requested-With'

@hook('after_request')
def enable_cors():
    '''Add headers to enable CORS'''

    response.headers['Access-Control-Allow-Origin'] = _allow_origin
    response.headers['Access-Control-Allow-Methods'] = _allow_methods
    response.headers['Access-Control-Allow-Headers'] = _allow_headers

class JSONResponse(): ## base response class that returns the json fields I want
    def __init__(self, data = (), success=True, message = "", status=200, timestamp='auto'):
        if data != ():
            self.data = data
        self.sucess = success
        self.message = message
        self.status = status
        if timestamp == 'auto':
            self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.timestamp = timestamp
    def toJSON(self): ## just report the class's fields as a dictionary that will get converted to real json when bottle returns it
        return self.__dict__


def connectToDefaultDatabase():
    '''Connect to the database using the settings configured in conf.txt'''
    ## read from the conf.txt file
    f = open("conf.txt", 'r')
    i = 0
    header = ['hostname', 'password', 'user', 'dbname']
    d = {}
    for line in f:
        fieldname = header[i]
        line = line.replace("\n", "")
        line = line.replace("'", "")
        d[fieldname] = line
        i += 1
    hostname = d['hostname']
    print hostname
    db = d['dbname']
    pw = d['password']
    user =d['user']
    conn = psycopg2.connect(host=hostname, user=user, database=db, password=pw)
    return conn

@route("/admin/test-database-connection")
def testConnection():
    '''Tests the ability to connect to the specified datavase by returning the version of postgres'''
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
    '''v
        Parameters:
            @:param: variableType (string) [optional]
            @:param: variablePeriod (integer) [optional]
            @:param: variablePeriodType (string) [optional]
            @:param: averagingPeriod (intger) [optional]
            @:param: averagingPeriodType (string) [optional]
            @:param: variableUnits (string) [optional]
        Returns:
            HTTP Response
            HTTP Statuses: 200
            Example:
                {
                  "success": true,
                  "status":200,
                  "timestamp": "12/19/2016, 7:00:00 PM",
                  "data": [
                    {
                      "variableDescription": "Decadal Averaged January Mean Temperature",
                    " : 1,
                      "variablePeriodType": "Month",
                      "averagingPeriod":1,
                      "averagingPeriodType":"Decade",
                      "variableUnits" : "C",
                      "variableID" : 1,
                      "lastUpdate" : "12/19/2016, 7:00:00 PM"
                    }
                  ],
                  "message": ""
                }
    '''
    ## pick the variables out from the query request
    variableType = request.query.variableType
    variablePeriod = request.query.variablePeriod
    variablePeriodType = request.query.variablePeriodType
    averagingPeriod = request.query.averagingPeriod
    averagingPeriodType = request.query.averagingPeriodType
    variableUnits = request.query.variableUnits
    ## set them to None if they're not in the request query string
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
    ## make the db query
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
    ## format the response
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
    '''POST a new variable to the database
        Parameters:
            @:param: variableType (string) [required]
            @:param: variablePeriod (integer) [required]
            @:param: variablePeriodType (string) [required]
            @:param: averagingPeriod (intger) [required]
            @:param: averagingPeriodType (string) [required]
            @:param: variableUnits (string) [required]
            @:param: description )string) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 201 (success), 400 (parameters not set), 204 (Resource already exists --  No content)
            Example:
                {
                  "message" : "Added variable 231 to database.",
                  "success" : true,
                  "status" : 201,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : []
                }
    '''
    ## get the variable
    variableType = request.query.variableType
    variablePeriod = request.query.variablePeriod
    variablePeriodType = request.query.variablePeriodType
    averagingPeriod = request.query.averagingPeriod
    averagingPeriodType = request.query.averagingPeriodType
    variableUnits = request.query.variableUnits
    description = request.query.description
    ## all parameters are required, so make sure they are set
    ## If they are not, then return a failure message
    if variableType == '' or variablePeriod == '' or variablePeriodType == '' or averagingPeriod == '' or averagingPeriodType == '' or variableUnits == '' or description == '':
        r = JSONResponse(data = (), success=False, message = "Not all parameters were specified.  Required parameters: VariableType, variablePeriod: variablePeriodType, averagingPeriod, averagingPeriodType, variableUnits, description", status=400)
        return r.toJSON()
    ## match on lower case
    variableType = variableType.lower()
    variablePeriodType = variablePeriodType.lower()
    averagingPeriodType = averagingPeriodType.lower()
    variableUnits = variableUnits.lower()
    conn = connectToDefaultDatabase()
    ## look up the ids for the variable fields from the proper tables
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

    ## check to see if what we are about to insert already exists
    query = """
        select count(*) from variables
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

    row = cursor.fetchone()
    if row[0] == 0:
        ## good to insert, the variable doesn't exist yet
        sql = '''INSERT INTO Variables VALUES (DEFAULT, %(varTypeID)s, %(unitID)s, %(varPeriod)s, %(varPeriodTypeID)s, %(averagingPeriod)s, %(averagingTypeID)s, %(description)s, current_timestamp);'''
        cursor.execute(sql, {'varTypeID':varTypeID, 'unitID':unitID, 'varPeriod':variablePeriod, 'varPeriodTypeID':varPeriodTypeID, 'averagingPeriod':averagingPeriod,
                             'averagingTypeID':averagingTypeID, 'description' : description})
        r = JSONResponse(data=(), success=True, message = cursor.statusmessage, status=201, timestamp='auto')
        conn.commit()
        code = 201
    else:
        ## the variable already exists, so don't add another
        r = JSONResponse(data=(), success=False, message = "Variable already exists.  Request was not completed.", status=204, timestamp='auto')
        code = 204
    return bottle.HTTPResponse(status=code, body=r.toJSON())

## Get search variable by ID
@get("/variables/<variableID>")
def getVariableByID(variableID):
    '''GET details about a specific variable in the database
        Parameters:
            @:param: variableID (integer) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 200 (request successful, resource exists), 404 (request failed, resource does not exist), 400 (required parameters not set)
            Example:
                {
                    "message" : "",
                    "status":200,
                    "success":true,
                    "data" : [
                      {
                        "variableDescription": "Decadal Averaged January Mean Temperature",
                        "variablePeriod" : 1,
                        "variablePeriodType": "Month",
                        "averagingPeriod":1,
                        "averagingPeriodType":"Decade",
                        "variableUnits" : "C",
                        "variableID" : 1,
                        "lastUpdate" : "12/19/2016, 7:00:00 PM"
                      }
                    ]
                }
    '''
    ## make database connection
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    try:
        int(variableID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: variableID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())

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
    ## format the response
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
    '''Update a variable record in the database, returns the newly modified copy of the resource
        Parameters:
            @:param: variableID (integer) [required]
            @:param: variableType (string) [optional]
            @:param: variablePeriod (integer) [optional]
            @:param: variablePeriodType (string) [optional]
            @:param: averagingPeriod (intger) [optional]
            @:param: averagingPeriodType (string) [optional]
            @:param: variableUnits (string) [optional]
        Returns:
            HTTP Response
            HTTP Statuses: 201 (success, resource modified), 404 (request failed, resource does not exist), 400 (required parameters not set)
            Example:
                {
                  "message" : "Updated variable 231 to database.",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                  {
                    "variableDescription": "Decadal Averaged January Mean Temperature",
                    "variablePeriod" : 1,
                    "variablePeriodType": "Month",
                    "averagingPeriod":1,
                    "averagingPeriodType":"Decade",
                    "variableUnits" : "C",
                    "variableID" : 1,
                    "lastUpdate" : "12/19/2016, 7:00:00 PM"
                  }
                  ]
                }
    '''
    ## check to see if variableID is set as a number
    try:
        int(variableID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=(), success=False, message = "Required parameters not set.  Required parameters: variableID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    ## parse the variables in the request query
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
    if variableType == '':
        variableType = None
    if variablePeriod == '':
        variablePeriod = None
    if variablePeriodType == '':
        variablePeriodType = None
    if averagingPeriod == '':
        averagingPeriod =None
    if averagingPeriodType == '':
        averagingPeriodType = None
    if variableUnits == '':
        variableUnits = None
    if description == '':
        description = None
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## check if the resource exists:
    query = '''SELECT count(*) from variables WHERE variableID = %(variableID)s'''
    cursor.execute(query, {'variableID' : variableID})
    row = cursor.fetchone()
    count = row[0]
    if count == 0:
        r = JSONResponse(data=[], success=False, message = "Variable does not exist.  You can POST a new one to the /variables resource.", status=404, timestamp='auto')
        code = 404
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    ## variable exists, so proceed with the update
    if variableType is not None:
        query = """
            SELECT variableTypeID FROM variableTypes where lower(variableTypeAbbreviation) = %(variableType)s OR lower(variableType) = %(variableType)s LIMIT 1;
            """
        cursor.execute(query, {'variableType': variableType})
        varTypeID = cursor.fetchone()
        if varTypeID != None:
            varTypeID = varTypeID[0]
    else:
        varTypeID = None
    if variablePeriodType is not None:
        query = '''
            SELECT variablePeriodTypeID from variablePeriodTypes WHERE variablePeriodType=%(variablePeriodType)s LIMIT 1;
            '''
        cursor.execute(query, {'variablePeriodType' : variablePeriodType})
        varPeriodTypeID = cursor.fetchone()
        if varPeriodTypeID is not None:
            varPeriodTypeID = varPeriodTypeID[0]
    else:
        varPeriodTypeID = None

    if averagingPeriodType is not None:
        query = '''SELECT averagingPeriodTypeID from averagingPeriodTypes where lower(averagingPeriodType)=%(averagingPeriodType)s LIMIT 1;'''
        cursor.execute(query, {'averagingPeriodType': averagingPeriodType})
        averagingTypeID = cursor.fetchone()
        if averagingTypeID is not None:
            averagingTypeID = averagingTypeID[0]
    else:
        averagingTypeID = None

    if variableUnits is not None:
        query = '''SELECT variableUnitID from variableUnits where lower(variableUnitAbbreviation)=%(variableUnit)s OR lower(variableUnit) = %(variableUnit)s LIMIT 1;'''
        cursor.execute(query, {'variableUnit': variableUnits})
        unitID = cursor.fetchone()
        if unitID is not None:
            unitID = unitID[0]
    else:
        unitID = None
    query = '''UPDATE variables SET
            variableType = coalesce(coalesce(%(varTypeID)s, NULL), variableType),
            variablePeriod = coalesce(coalesce(%(variablePeriod)s, NULL), variablePeriod),
            variablePeriodType = coalesce(coalesce(%(varPeriodTypeID)s, NULL), variablePeriodType),
            variableAveraging = coalesce(coalesce(%(averagingPeriod)s, NULL), variableAveraging),
            variableAveragingType = coalesce(coalesce(%(averagingTypeID)s, NULL), variableAveragingType),
            variableDescription = coalesce(coalesce(%(description)s, ''), variableDescription),
            lastUpdate = current_timestamp
        WHERE
            variableID = %(variableID)s;
        '''

    params = {'varTypeID' : varTypeID, 'variablePeriod' : variablePeriod, 'varPeriodTypeID' : varPeriodTypeID,
                           'averagingPeriod' : averagingPeriod, 'averagingTypeID' : averagingTypeID, 'description' : description, 'variableID' :variableID}
    print params
    cursor.execute(query, params)
    ## get the last modified copy
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
    ## format the response
    out = []
    for row in cursor.fetchall():
        d = {}
        i = 0
        while i < len(row):
            fieldname = header[i]
            d[fieldname] = row[i]
            i += 1
        out.append(d)
    r = JSONResponse(data=out, success=True, message = template("Updated variable {{variableID}} ", variableID=variableID), status=201, timestamp='auto')
    code = 201
    return bottle.HTTPResponse(status=code, body=r.toJSON())

## Delete a variable by its id
@delete("/variables/<variableID>")
def deleteVariableByID(variableID):
    '''DELETE a variable from the database
        Parameters:
            @:param: variableID (integer) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 204 (success, resource deleted or does not exist), 400 (required parameters not set)
            Example:
                {
                  "message" : "Deleted variable 231.",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : []
                }
    '''
    ## check to see if variableID is set as a number
    try:
        int(variableID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: variableID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())

    ## Connect to the database
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        DELETE FROM variables
        WHERE variables.variableID = %(variableID)s
        """
    ## return the response
    cursor.execute(query, {'variableID': variableID})
    r = JSONResponse(data=[], success=True, message = template("Deleted variable {{variableID}}", variableID=variableID), status=204, timestamp='auto')
    conn.commit()
    code = 204
    return bottle.HTTPResponse(status=code)



### GET search for variable Types
@get("/variableTypes")
def getVariableTypes():
    '''GET a list of the variable types.
        N.B. Variable types are the type of measurement contained in the variable, e.g., maximum temperature, precipitation
              Variable types must be in this table before they can be specified in variables
        Parameters:
            @:param: abbreviation (string) [optional]
            @:param: variableName (string) [optional]
        Returns:
            HTTP Response
            HTTP Statuses: 200 (request successful)
            Example:
                {
                  "message" : "",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "variableTypeID":89,
                      "variableTypeAbbreviation" : "TMax",
                      "variableTypeName" : "Maximum Temperature"
                    }
                  ]
                }
    '''
    ## parse the query
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
    ## format the response
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
@post("/variableTypes")
def addVariableType():
    '''POST a new variable type to the database
        Parameters:
            @:param: abbreviation (string) [required]
            @:param: variableName (string) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 201 (request successful, resource added), 400 (request failed, parameters not set), 200 (resource already exits, not modifed)
            Example:
                {
                  "message" : "Added variable type 89 to the database.",
                  "success" : true,
                  "status" : 201,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : []
                }
    '''
    ## parse the request
    abbreviation = request.query.abbreviation
    fullName = request.query.variableName
    if abbreviation == '':
        abbreviation = None
    else:
        abbreviation = abbreviation.lower()
    if fullName == '':
        fullName = None
    if fullName is None or abbreviation is None:
        ## required parameters were not set
        r = JSONResponse(data = (), success=False, message = "Not all parameters were specified.  Required parameters: variableName, abbreviation", status=400)
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## check of the variable type exists already
    query = '''SELECT count(*) from variableTypes where variableTypeAbbreviation=%(abbreviation)s OR variableType LIKE %(variableType)s;'''
    cursor.execute(query, {'variableType' : fullName, 'abbreviation' : abbreviation})
    count = cursor.fetchone()[0]
    if count > 0:
        ## resource already exists
        r = JSONResponse(data = (), success=False, message = "Resource already exists.  Not modified.", status=200)
        return bottle.HTTPResponse(status=200, body=r.toJSON())
    ## otherwise, resource doesn't exist, so create it
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
@get("/variableTypes/<variableTypeID>")
def getVariableTypeByID(variableTypeID):
    '''GET details about a variable type
        Parameters:
            @:param: variableTypeID (integer) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 200 (request successful), 404 (request failed, resource does not exist)
            Example:
                {
                  "message" : "",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "variableTypeID":89,
                      "variableTypeAbbreviation" : "TMax",
                      "variableTypeName" : "Maximum Temperature"
                    }
                  ]
                }
    '''
    ## check to see if variableTypeID is set as a number
    try:
        int(variableTypeID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: variableTypeID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    ## open the connection
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
    cursor.execute(query, {'variableTypeID': variableTypeID}) ## do the search
    ## format the response
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
        ## resource does not exist, return 404
        r = JSONResponse(data=out, success=False, message = "Variable type does not exist.  You can POST a new one to the /variables/variabletypes resource.", status=404, timestamp='auto')
        code = 404
    else:
        ## resource exists, return it as status 200
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
        code = 200
    return bottle.HTTPResponse(status=code, body=r.toJSON())

## DELETE a variable type
@delete("/variableTypes/<variableTypeID>")
def deleteVariableTypeByID(variableTypeID):
    '''DELETE a variable type from the database using its variableTypeID
        Parameters:
            @:param: variableTypeID (integer) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 204 (Request successfully deleted or did not exist)
            Example:
               {
                  "message" : "Deleted variable type 89",
                  "success" : true,
                  "status" : 204,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : []
                }
    '''
    ## check to see if variableTypeID is set as a number
    try:
        int(variableTypeID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: variableTypeID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        DELETE from
        variableTypes
        WHERE 1 = 1
        AND
        variableTypeID = %(variableTypeID)s;
        """
    cursor.execute(query, {'variableTypeID': variableTypeID})
    conn.commit()
    r = JSONResponse(data=[], success=True, message = template("Deleted variable {{variableTypeID}}", variableTypeID=variableTypeID), status=204, timestamp='auto')
    return bottle.HTTPResponse(status=204, body=r.toJSON())

@put("/variableTypes/<variableTypeID>")
def updateVariableTypeByID(variableTypeID):
    '''PUT an update to a variableType using its variableTypeID
        Parameters:
            @:param: variableTypeID (integer) [required]
            @:param: abbreviation (string) [optional]
            @:param: variableName (string) [optional]
        Returns:
            HTTP Response
            HTTP Statuses: 201 (success, resource modified), 404 (request failed, resource does not exist)
            Example:
                {
                  "message" : "Updated variable type 89",
                  "success" : true,
                  "status" : 201,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "variableTypeID":89,
                      "variableTypeAbbreviation" : "TMax",
                      "variableTypeName" : "Maximum Temperature"
                    }
                  ]
                }
    '''
    ## check to see if variableTypeID is set as a number
    try:
        int(variableTypeID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: variableTypeID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
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
    ## check to see if the variable exists
    query = '''SELECT count(*) from variableTypes WHERE variableTypeID = %(variableTypeID)s;'''
    cursor.execute(query, {'variableTypeID' : variableTypeID})
    count = cursor.fetchone()[0]
    if count == 0:
        ## resource does not exist, return 404
        r = JSONResponse(data=[], success=False, message = template("Variable {{variableTypeID}} does not exist.  You can POST a new one to the /variables/variableTypes resource", variableTypeID=variableTypeID), status=404, timestamp='auto')
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    ## otherwise, it exists
    query = """
        UPDATE
            variableTypes
        SET
            variableTypeAbbreviation = coalesce(%(abbreviation)s, variableUnitAbbreviation),
            variableType = coalesce(%(variableType)s, variableType )
        WHERE 1 = 1
            AND variableTypeID = %(variableTypeID)s;
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
    r = JSONResponse(data=out, success=True, message = template("Updated variable {{variableTypeID}}", variableTypeID=variableTypeID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())

## GET variable units
@get("/variableUnits")
def getVariableUnits():
    '''GET a list of all variable units in the database
        N.B. A variable unit must be in this list before it can be used in a variable record
        Parameters:
            @:param: unitName (string) [optional]
            @:param: abbreviation (string) [optional]
        Returns:
            HTTP Response
            HTTP Statuses: 200 (request successful)
            Example:
                {
                  "message" : "",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "unitID" : 193,
                      "unitAbbreviation" : "cm",
                      "unitName":"centimeters"
                    }
                  ]
                }
    '''
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
        select
            variableUnitID, variableUnit, variableUnitAbbreviation
        from variableUnits
        WHERE 1 = 1
        AND
            (%(abbreviation)s is NULL or %(abbreviation)s = lower(variableUnits.variableUnitAbbreviation) )
            AND  (%(fullName)s is NULL or %(fullName)s = variableUnits.variableUnit )
        """
    header = ['variableUnitID', 'variableUnit', 'variableUnitAbbreviation']
    cursor.execute(query, {'fullName': fullName, 'abbreviation' : abbreviation})
    ## format the response
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
@post("/variableUnits")
def addVariableUnit():
    '''POST a variable unit type to the database
        Parameters:
            @:param: abbreviation (string) [required]
            @:param: unitName (string) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 201 (request successful, resource created), 400 (request failed, parameters not set), 200 (resource already exists, not modified)
            Example:
                {
                  "message" : "Added variable 190 to the database",
                  "success" : true,
                  "status" : 201,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "unitID" : 190,
                      "unitAbbreviation" : "cm",
                      "unitName" : "centimeters"
                    }
                  ]
                }
    '''
    abbreviation = request.query.abbreviation
    fullName = request.query.unitName
    if abbreviation == '':
        abbreviation = None
    else:
        abbreviation = abbreviation.lower()
    if fullName == '':
        fullName = None
    if fullName is None or abbreviation is None:
        ## required parameters were not set, so return status 400
        r = JSONResponse(data = (), success=False, message = "Not all parameters were specified.  Required parameters: unitName, abbreviation", status=400)
        return bottle.HTTPResponse(status=400, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## check if the resource already exists
    query = '''SELECT COUNT(*) from variableUnits WHERE lower(variableUnitAbbreviation) LIKE %(abbreviation)s OR lower(variableUnit) LIKE %(variableUnit)s;'''
    cursor.execute(query, {'variableUnit': fullName, 'abbreviation':abbreviation})
    count = cursor.fetchone()[0]
    if count == 1:
        ## resource already exists, don't modify it, return 200
        r = JSONResponse(data=[], success=False, message = "Variable unit already exists.  Not modified.", status=200, timestamp='auto')
        return bottle.HTTPResponse(status=200, body=r.toJSON())
    ## otherwise, it doesn't exit, so create it
    query = '''
        INSERT INTO variableUnits VALUES (DEFAULT, %(variableType)s, %(abbreviation)s) RETURNING variableUnitID;
    '''
    cursor.execute(query, {'variableType': fullName, 'abbreviation':abbreviation})
    conn.commit()
    returned = cursor.fetchone()
    returnedID = returned[0]
    r = JSONResponse(data=(), success=True, message = template("Added variable unit {{variableID}} to the database.", variableID=returnedID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())


### GET variable unit by id
@get("/variableUnits/<variableUnitID>")
def getVariableUnitByID(variableUnitID):
    '''GET details about a variable unit by its id
        Parameters:
            @:param: variableUnitID (integer) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 200 (request successful, resource exists), 404 (request failed, resource does not exist)
             Example:
                {
                  "message" : "",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "unitID" : 190,
                      "unitAbbreviation" : "cm",
                      "unitName":"centimeters"
                    }
                  ]
                }
    '''
    ## check to see if variableUnitID is set as a number
    try:
        int(variableUnitID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=(), success=False, message = "Required parameters not set.  Required parameters: variableUnitID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
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
        ## resource doesnt exist, return 404
        r = JSONResponse(data=(), success=False, message = "Variable unit does not exist.  You can POST a new one to the /variables/variableunits resource.", status=404, timestamp='auto')
    else:
        ## resource exists, return 200
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
    return bottle.HTTPResponse(status=200, body=r.toJSON())

## DELETE a variable unit
@delete("/variableUnits/<variableUnitID>")
def deleteVariableUnitByID(variableUnitID):
    '''DELETE a variable unit from the database using its variableUnitID
        Parameters:
            @:param: variableUnitID (integer) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 204 (resource deleted or resource did not exist)
            Example:
                {
                  "message" : "Deleted variable 190",
                  "success" : true,
                  "status" : 201,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : []
                }
    '''
    ## check to see if variableUnitID is set as a number
    try:
        int(variableUnitID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: variableUnitID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        DELETE from
            variableUnits
        WHERE 1 = 1
        AND
            variableUnitID = %(variableUnitID)s;
        """
    cursor.execute(query, {'variableUnitID': variableUnitID})
    r = JSONResponse(data=[], success=True, message = template("Deleted variable {{variableUnitID}}", variableUnitID=variableUnitID), status=204, timestamp='auto')
    return bottle.HTTPResponse(status=204, body=r.toJSON())


## Update a variable units entry
@put("/variableUnits/<variableUnitID>")
def updateVariableUnitByID(variableUnitID):
    """
    PUT an update to a variable unit in the database using its variableUnitID, and return the modified copy
        Parameters:
            @:param: variableUnitID (integer) [required]
            @:param: abbreviation (string) [optional]
            @:param: unitNAme (string) [optional]
        Returns:
            HTTP Response
            HTTP Statuses: 201 (request successful, resource modified), 404 (request failed, resource does not exist)
            Example:
            {
              "message" : "Updated variable 190",
              "success" : true,
              "status" : 201,
              "timestamp" : "12/19/2016, 7:00:00 PM",
              "data" : [
                {
                  "unitID" : 190,
                  "unitAbbreviation" : "cm",
                  "unitName" : "centimeters"
                }
              ]
            }
    """
    ## check to see if variableUnitID is set as a number
    try:
        int(variableUnitID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=(), success=False, message = "Required parameters not set.  Required parameters: variableUnitID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    abbreviation = request.query.abbreviation
    fullName = request.query.unitName
    if abbreviation == '':
        abbreviation = None
    else:
        abbreviation = abbreviation.lower()
    if fullName == '':
        fullName = None
    ## check if the resource exists
    query = '''SELECT count(*) from variableUnits where variableUnitID = %(variableUnitID)s;'''
    cursor.execute(query, {'variableUnitID':variableUnitID})
    count = cursor.fetchone()[0]
    if count == 0:
        ## resource does not exist, return 404
        r = JSONResponse(data=(), success=True, message = template("Variable unit {{variableUnit}} does not exist", variableUnit=variableUnitID), status=404, timestamp='auto')
        cursor.close()
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    ## otherwise it exists, so update
    query = """
        UPDATE
            variableTypes
        SET
            variableUnitAbbreviation = coalesce(%(abbreviation)s, variableUnitAbbreviation),
            variableUnit = coalesce(%(variableUnit)s, variableUnit)
        WHERE 1 = 1
        AND
            variableUnitID = %(variableUnitID)s;
        """
    cursor.execute(query, {'variableUnitID': variableUnitID, 'variableUnit' : fullName, 'abbreviation':abbreviation})
    ## also return details about this item to prove we updated it
    query = """
        select variableUnitID, variableUnit, variableUnitAbbreviation
        from variableUnits
        WHERE
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
@get("/variablePeriodTypes")
def getVariablePeriodTypes():
    """
    GET a list of variable types in the database
        Parameters:
            @:param: name (string) [optional]
        Returns:
            HTTP Response
            HTTP Statuses: 200 (request successful)
            Example:
                {
                  "message" : "",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "variablePeriodID" : 193,
                      "variablePeriodName": "Year"
                    }
                  ]
                }
    """
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
            AND  (%(fullName)s is NULL or %(fullName)s LIKE lower(variablePeriodTypes.variablePeriodType) )
        """
    header = ['variablePeriodID', 'variablePeriodName']
    cursor.execute(query, {'fullName': fullName}) ## do the search
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
@post("/variablePeriodTypes")
def addVariablePeriod():
    """Post a new variable to the database
        Parameters:
            @:param: name (string) [required]
        Returns:
            HTTP Response
            HTTP Statuses: 201 (request successful, resource created), 200 (resource exists, not modified), 400 (parameters not set)
            Example:
                {
                  "message" : "Add variable period 7 to the database",
                  "success" : true,
                  "status" : 201,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "variablePeriodID" : 190,
                      "variablePeriodName": "Year"
                    }
                  ]
                }
    """
    fullName = request.query.name
    if fullName == '':
        fullName = None
    else:
        fullName = fullName.lower()
    if fullName is None:
        ## No required parameters, return 400
        r = JSONResponse(data = (), success=False, message = "Not all parameters were specified.  Required parameters: name", status=400)
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    ## otherwise, continue
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## check if the resource exists
    query = '''SELECT count(*) from variablePeriodTypes WHERE lower(variablePeriodType) LIKE %(variablePeriod)s;'''
    cursor.execute(query, {'variablePeriod':fullName})
    count = cursor.fetchone()[0]
    if count > 0:
        ## resource exists, return 200
        r = JSONResponse(data=(), success=False, message = "Variable period already exists. Not modified.", status=200, timestamp='auto')
        return bottle.HTTPResponse(status=200, body=r.toJSON())
    ## otherwise, create it
    query = '''
        INSERT INTO variablePeriodTypes VALUES (DEFAULT, %(variablePeriod)s) RETURNING variablePeriodTypeID;
    '''
    cursor.execute(query, {'variablePeriod': fullName})
    conn.commit()
    returned = cursor.fetchone()
    returnedID = returned[0]
    r = JSONResponse(data=(), success=True, message = template("Added variable period {{variableID}} to the database.", variableID=returnedID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())


## GET variable period by ID
@get("/variablePeriodTypes/<variablePeriodID>")
def getVariablePeriodByID(variablePeriodID):
    """
        GET details about a variable period by its variablePeriodID
        Parameters:
            @:param: variablePeriodID (integer) [required]
        :returns:
            HTTP Response
            HTTP Statuses: 200 (request successful, resource exists), 404 (request failed, resource does not exist)
            Example:
                {
                  "message" : "",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "variablePeriodID" : 190,
                      "variablePeriodName" : "Year"
                    }
                  ]
                }
    """
    ## check to see if variablePeriodID is set as a number
    try:
        int(variablePeriodID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=(), success=False, message = "Required parameters not set.  Required parameters: variablePeriodID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
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
        ## resource doesn't exist, return 404
        r = JSONResponse(data=(), success=False, message = "Variable period does not exist.  You can POST a new one to the /variables/variablePeriods resource.", status=404, timestamp='auto')
        code = 404
    else:
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
        code = 200
    return bottle.HTTPResponse(status=code, body=r.toJSON())

## DELETE variable period by ID
@delete("/variablePeriodTypes/<variablePeriodID>")
def deleteVariablePeriodByID(variablePeriodID):
    """
    Deletes a variable period by its variablePeriodID
        Parameters:
            @:param: variablePeriodID (integer) [required]
        :returns:
            HTTP Response
            HTTP Statuses: 204 (Resource deleted or did not exist)
            Example:
                {
                  "message" : "Deleted variable period 190",
                  "success" : true,
                  "status" : 204,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : []
                }
    """
    ## check to see if variablePeriodID is set as a number
    try:
        int(variablePeriodID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=(), success=False, message = "Required parameters not set.  Required parameters: variablePeriodID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
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
    r = JSONResponse(data=(), success=True, message = "", status=200, timestamp='auto')
    return bottle.HTTPResponse(status=204, body=r.toJSON())

## Update a variable period
@put("/variablePeriodTypes/<variablePeriodID>")
def updateVariablePeriodByID(variablePeriodID):
    """
    PUT an update to the variable period using its variablePeriodID
        Parameters:
            @:param: variablePeriodID (integer) [required]
        :returns:
            HTTP Response
            HTTP Statuses: 201 (request successful, resource modified), 404 (request failed, ressource does note exist)
            Example:
                {
                  "message" : "Updated variable period 190",
                  "success" : true,
                  "status" : 201,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                    "variablePeriodID" : 190,
                    "variablePeriodName" : "Year"
                    }
                  ]
                }
    """
    ## check to see if variablePeriodID is set as a number
    try:
        int(variablePeriodID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=(), success=False, message = "Required parameters not set.  Required parameters: variablePeriodID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    fullName = request.query.name
    if fullName == '':
        fullName = None
    else:
        fullName = fullName.lower()
    ##check if it exists
    query = '''SELECT count(*) from variablePeriodTypes where variablePeriodTypeID = %(variablePeriodID)s;'''
    cursor.execute(query, {'variablePeriodID' : variablePeriodID})
    count = cursor.fetchone()[0]
    if count == 0:
        ## does not exist, return 404
        r = JSONResponse(data=(), success=False, message = template("Variable Period {{variablePeriodID}} does not exist.", variablePeriodID=variablePeriodID), status=404, timestamp='auto')
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    ## otherwise, it does exist, so update it
    query = """
        UPDATE
        variablePeriodTypes
        SET
        variablePeriodType = coalesce(%(variablePeriod)s, variablePeriodType)
        WHERE 1 = 1
        AND
        variablePeriodTypeID = %(variablePeriodID)s;
        """
    cursor.execute(query, {'variablePeriodID': variablePeriodID, 'variablePeriod':fullName})
    ## also return details about this item to prove we updated it
    query = """
        select variablePeriodTypeID, variablePeriodType
        from variablePeriodTypes
        WHERE 1 = 1 AND
        (variablePeriodTypeID = %(variablePeriodID)s);
        """
    header = ['variablePeriodTypeID', 'variablePeriodType']
    cursor.execute(query, {'variablePeriodID': variablePeriodID})
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
@get("/averagingTypes")
def getVariableAveragingTypes():
    """
    GET a list of variable averaging types from the database
    N.B. : Variable averaging types must be in this list before they can be used in a variable definition
        Parameters:
            @:param: name (string) [optional]
        :returns:
            HTTP Response
            HTTP Statuses: 200 (request successful)
            Example:
                {
                  "message" : "",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                      "averagingPeriodID" : 193,
                      "averagingPeriodName": "Year",
                      "averagingPeriodDays":365
                    }
                  ]
                }
    """
    fullName = request.query.name
    days = request.query.days
    if fullName == '':
        fullName = None
    else:
        fullName = fullName.lower()
    if days == '':
        days= None
    print fullName
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
        select *
        from averagingPeriodTypes
        WHERE 1 = 1
            AND  (%(fullName)s is NULL or %(fullName)s = lower(averagingPeriodTypes.averagingPeriodType) )
            AND  (%(days)s is NULL or %(days)s = averagingPeriodTypes.averagingPeriodDays )
        """
    header = ['averagingPeriodID', 'averagingPeriodType', 'averagingPeriodDays']
    cursor.execute(query, {'fullName': fullName, 'days' : days})
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
@post("/averagingTypes")
def addAveragingType():
    """
    POST a new averaging type to the database
        Parameters:
            @:param: days (integer) [required]
            @:param: name (string) [required]
        :returns:
            HTTP Response
            HTTP Statuses: 201 (request successful, resource created), 400 (parameters not set), 200 (resource exists, not modified)
            Example:
                {
                  "message" : "Added averaging period 193 to the database",
                  "success" : true,
                  "status" : 201,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : []
                }
    """
    numDays = request.query.days
    fullName = request.query.name
    if fullName == '':
        fullName = None
    else:
        fullName = fullName.lower()
    if numDays == '':
        numDays = None
    if fullName is None or numDays is None:
        ## Parameters not set, so return 400
        r = JSONResponse(data = (), success=False, message = "Not all parameters were specified.  Required parameters: name, days", status=400)
        return bottle.HTTPResponse(status=400, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## check to see if it already exists
    query = '''SELECT count(*) from averagingPeriodTypes WHERE lower(averagingPeriodType) LIKE %(averagingPeriodType)s OR averagingPeriodDays = %(numDays)s;'''
    cursor.execute(query, {'averagingPeriodType' : fullName, 'numDays' : numDays})
    count = cursor.fetchone()[0]
    if count > 0:
        ## resource exists, return 200
        r = JSONResponse(data=(), success=False, message = "Resource already exists. Not modified.", status=200, timestamp='auto')
        return bottle.HTTPResponse(status=200, body=r.toJSON())
    ## otherwise, create the new resource
    query = '''
        INSERT INTO averagingPeriodTypes VALUES (DEFAULT, %(periodTypeName)s, %(numDays)s) RETURNING averagingPeriodTypeID;
    '''
    cursor.execute(query, {'periodTypeName': fullName, 'numDays':numDays})
    conn.commit()
    returned = cursor.fetchone()
    returnedID = returned[0]
    r = JSONResponse(data=(), success=True, message = template("Added averaging period {{variableID}} to the database", variableID=returnedID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())

## GET averaging type by ID
@get("/averagingTypes/<averagingTypeID>")
def getAveragingTypeByID(averagingTypeID):
    """Get details about an averaging type by its averagingPeriodTypeID
        Parameters:
            @:param: averagingPeriodTypeID (integer) [required]
        :returns:
            HTTP Response
            HTTP Statuses: 200 (request successful, resource exists), 404 (request failed, resource does not exist)
            Example:
                {
                  "message" : "",
                  "success" : true,
                  "status" : 200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : [
                    {
                    "averagingPeriodID" : 193,
                    "averagingPeriodName": "Year",
                    "averagingPeriodDays":365
                    }
                  ]
                }
    """
    ## check to see if averagingTypeID is set as a number
    try:
        int(averagingTypeID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=(), success=False, message = "Required parameters not set.  Required parameters: averagingTypeID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        select *
        from averagingPeriodTypes
        WHERE 1 = 1
        AND
        averagingPeriodTypeID = %(averagingPeriodTypeID)s;
        """
    header = ['averagingPeriodID', 'averagingPeriodType', 'averagingPeriodDays']
    cursor.execute(query, {'averagingPeriodTypeID': averagingTypeID})
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
        ## doesn't exist, return 404
        r = JSONResponse(data=(), success=False, message = "Variable period does not exist.  You can POST a new one to the /variables/variabletypes resource.", status=404, timestamp='auto')
        code = 404
    else:
        ## does exist, return 200
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
        code = 200
    return bottle.HTTPResponse(status=code, body=r.toJSON())

## DELETE an averaging period type from the database
@delete("/averagingTypes/<averagingTypeID>")
def deleteAveragingTypeByID(averagingTypeID):
    """
    DELETE an existing averagingTypeID from the database
    Parameters:
        @:param: averagingTypeID (integer) [required]
    :returns:
        HTTP Response
        HTTP Statuses: 204 (resource deleted or did not exist)
        Example:
            {
              "message" : "Deleted averaging period 190",
              "success" : true,
              "status" : 204,
              "timestamp" : "12/19/2016, 7:00:00 PM",
              "data" : []
            }
    """
    ## check to see if averagingTypeID is set as a number
    try:
        int(averagingTypeID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=(), success=False, message = "Required parameters not set.  Required parameters: averagingTypeID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        delete
        from averagingPeriodTypes
        WHERE 1 = 1
        AND
        averagingPeriodTypeID = %(averagingPeriodTypeID)s;"""
    cursor.execute(query, {'averagingPeriodTypeID': averagingTypeID})
    r = JSONResponse(data=(), success=True, message = "", status=204, timestamp='auto')
    return bottle.HTTPResponse(status=204, body=r.toJSON())

## UPDATE an existing averaging type
@put("/averagingTypes/<averagingTypeID>")
def updateAveragingTypeByID(averagingTypeID):
    """
    PUT an update on an averaging type into the database
    Parameters:
        @:param: averagingTypeID (integer) [required]
        @:param: days (integer) [optional]
        @:param: name (string) [otional]
    :returns:
        HTTP Response
        HTTP Statuses: 201 (request succesful, resource modified), 404 (request failed, resource does not exist)
    """
    ## check to see if averagingTypeID is set as a number
    try:
        int(averagingTypeID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=(), success=False, message = "Required parameters not set.  Required parameters: averagingTypeID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())

    numDays = request.query.days
    fullName = request.query.name
    if fullName == '':
        fullName = None
    else:
        fullName = fullName.lower()
    if numDays == '':
        numDays = None
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## check if it exists
    query = '''SELECT count(*) from averagingPeriodTypes WHERE averagingPeriodTypeID= %(averagingPeriodTypeID)s;'''
    cursor.execute(query, {'averagingPeriodTypeID' : averagingTypeID})
    count = cursor.fetchone()[0]
    if count == 0:
        ## does not exist, return 404
        r = JSONResponse(data=(), success=False, message = template("Averaging period {{variableID}} does not exist.", variableID=averagingTypeID), status=404, timestamp='auto')
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    ## otherwise, update it
    query = '''
        UPDATE averagingPeriodTypes
        SET
            averagingPeriodType = coalesce(%(averagingPeriodType)s, averagingPeriodType),
            averagingPeriodDays = coalesce(%(averagingPeriodDays)s, averagingPeriodDays)
        WHERE
            averagingPeriodTypeID = %(averagingPeriodTypeID)s;
    '''
    print averagingTypeID, fullName, numDays
    cursor.execute(query, {'averagingPeriodTypeID': averagingTypeID, 'averagingPeriodType': fullName, 'averagingPeriodDays':numDays})
    conn.commit()
    ## get the new copy and return it
    query = '''SELECT * FROM averagingPeriodTypes where averagingPeriodTypeID=%(averagingPeriodTypeID)s'''

    cursor.execute(query, {'averagingPeriodTypeID':averagingTypeID})
    header = ['averagingPeriodTypeID', 'averagingPeriodType', 'Days']
    out = []
    d = {}
    i = 0
    row = cursor.fetchone()
    while i <len(header):
        col = header[i]
        val = row[i]
        d[col] = val
        i += 1
    out.append(d)
    r = JSONResponse(data=out, success=True, message = template("Updated averaging period {{variableID}}", variableID=averagingTypeID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())


## GET a list of data source from the database
@get("/sources")
def getSources():
    """GET a list of the data sources in the database
        N.B.: Data source must be in this list before it can be listed as a source for a layer
        Parameters:
            @:param: producer (string) [optional]
            @:param: model (string) [optional]
            @:param: modelVersion (number) [optional]
            @:param: modelScenario (string) [optional]
        :returns:
            HTTP Response
            HTTP Statuses: 200 (request successful)
            Example:
               {
                  "message" : "",
                  "success" : true,
                  "status":200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data": [
                    {
                      "sourceID" : 237,
                      "producer" : "NCAR",
                      "model" : "CCSM",
                      "scenario":"",
                      "productVersion":3,
                      "productURL" : "http://www.cesm.ucar.edu/models/ccsm3.0/",
                      "lastUpdate" : "12/19/2016, 7:00:00 PM"
                    }
                  ]
                }
    """
    producer = request.query.producer
    model = request.query.model
    modelVersion = request.query.modelVersion
    modelScenario = request.query.modelScenario
    if model == '':
        model = None
    else:
        model = model.lower()
    if producer == '':
        producer = None
    else:
        producer = producer.lower()
    if modelScenario == '':
        modelScenario = None
    else:
        modelScenario = modelScenario.lower()
    if modelVersion == '':
        modelVersion = None

    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
        select sourceID, producer, model, productVersion, scenario, productURL, lastUpdate
        from sources
        WHERE 1=1
        AND
            (%(model)s is NULL or %(model)s LIKE lower(model) )
            AND  (%(producer)s is NULL or %(producer)s LIKE lower(producer) )
            AND (%(modelVersion)s is NULL or %(modelVersion)s = productVersion )
            AND (%(modelScenario)s is NULL or %(modelScenario)s LIKE lower(scenario) )
        """
    header = ['sourceID', 'producer', 'model', 'productVersion', 'scenario', 'producURL', 'lastUpdate']
    cursor.execute(query, {'model': model, 'producer' : producer,'modelVersion':modelVersion,
                           'modelScenario' : modelScenario})
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
    return bottle.HTTPResponse(status=200, body=r.toJSON())

## Add a new source
@post("/sources")
def addSource():
    """
    POST a new source to the database
    Parameters:
        @:param: producer (string) [required]
        @:param: model (string) [required]
        @:param: modelVersion (number) [required]
        @:param: modelScenario (string) [requir ed]
        @:param: modelURL (string) [required]
    :returns:
        HTTP Response
        HTTP Statuses: 201 (request successful, resource created), 400 (required parameters not set), 200 (resource exists, not modified)
        Example:
            {
              "message" : "",
              "success" : true,
              "status":201,
              "timestamp" : "12/19/2016, 7:00:00 PM",
              "data": []
            }
    """
    producer = request.query.producer
    model = request.query.model
    modelVersion = request.query.modelVersion
    modelScenario = request.query.modelScenario
    productURL = request.query.modelURL
    if model == '':
        model = None
    else:
        model = model.lower()
    if producer == '':
        producer = None
    else:
        producer = producer.lower()
    if modelScenario == '':
        modelScenario = None
    else:
        modelScenario = modelScenario.lower()
    if modelVersion == '':
        modelVersion = None
    if productURL == '':
        productURL = None
    if modelVersion is None or productURL is None or modelScenario is None or producer is None or model is None:
        ##Required parameters are not set, so return 400
        r = JSONResponse(data = [], status=400, message="Not all parameters were set.  Required parameters: producer, model, modelVersion, modelScenario, modelURL")
        return bottle.HTTPResponse(status=400, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## Check to see if the resource already exists
    query = '''SELECT COUNT(*) FROM sources WHERE
        1 = 1
        AND (lower(model) LIKE %(model)s )
        AND (lower(scenario) LIKE %(modelScenario)s)
        AND (lower(productVersion) = %(productVersion)s )
    '''
    cursor.execute(query, {'model' : model, 'modelScenario' : modelScenario, 'productVersion':modelVersion})
    count = cursor.fetchone()[0]
    if count > 0:
        ## resource exists
        ## return 200
        r = JSONResponse(data=[], success=False, message = "Resource already exists.  Not modified.", status=200, timestamp='auto')
        return bottle.HTTPResponse(status=200, body=r.toJSON())
    ## otherwise create the new resource
    query = """
        INSERT INTO sources VALUES(
        DEFAULT, %(producer)s, %(model)s, %(modelVersion)s, %(modelScenario)s, %(modelURL)s, DEFAULT) returning sourceID;
        """
    cursor.execute(query, {'model': model, 'producer' : producer,'modelVersion':modelVersion,
                           'modelScenario' : modelScenario, 'modelURL': productURL})
    response = cursor.fetchone()
    returnedID = response[0]
    r = JSONResponse(data=[], success=True, message = template("Added source {{sourceID}} to the database", sourceID=returnedID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())

## GET a source by its id
@get("/sources/<sourceID>")
def getSourceByID(sourceID):
    """GET details about a source using its sourceID
        Parameters:
            @:param: sourceID (integer) [required]
        :returns:
            HTTP Response
            HTTP Statuses: 200 (request successful, resource exists), 404 (request failed, resource does not exist)
            Example:
                {
                  "message" : "",
                  "success" : true,
                  "status":200,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data": [
                    {
                      "sourceID" : 237,
                      "producer" : "NCAR",
                      "model" : "CCSM",
                      "scenario":"",
                      "productVersion":3,
                      "productURL" : "http://www.cesm.ucar.edu/models/ccsm3.0/",
                      "lastUpdate" : "12/19/2016, 7:00:00 PM"
                    }
                  ]
                }
    """
    ## check to see if sourceID is set as a number
    try:
        int(sourceID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: sourceID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        select sourceID, producer, model, productVersion, productURL, lastUpdate
        from sources
        WHERE 1 = 1
        AND
        sourceID = %(sourceID)s;
        """
    header = ['sourceID', 'producer', 'model', 'productVersion', 'productURL', 'lastUpdate']
    cursor.execute(query, {'sourceID': sourceID})
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
    if len(out) == 0:
        ## resource does not exist, return 404
        r = JSONResponse(data=out, success=False, message = "Source does not exist.  You can POST a new one to the /sources resource.", status=404, timestamp='auto')
        code = 404
    else:
        ## resource exists, return 200
        r = JSONResponse(data=out, success=True, message = "", status=200, timestamp='auto')
        code = 200
    return bottle.HTTPResponse(status=code, body=r.toJSON())

## PUT an update to an existing source
@put("/sources/<sourceID>")
def updateSourceByID(sourceID):
    """
        PUT an update to a source in the database using its source ID and returns the modified copy.
        Parameters:
            @:param: sourceID (string) [required]
            @:param: producer (string) [optional]
            @:param: model (string) [optional]
            @:param: modelVersion (string) [optional]
            @:param: modelScenario (string) [optional]
            @:param: modelURL (string) [optional]
        :returns:
            HTTP Response
            HTTP Statuses: 201 (request successful, resource modified), 404 (request failed, resource does not exist)
            Example:
            {
              "message" : "Updated variable 231.",
              "success" : true,
              "status" : 200,
              "timestamp" : "12/19/2016, 7:00:00 PM",
              "data" : [
              {
                "variableDescription": "Decadal Averaged January Mean Temperature",
                "variablePeriod" : 1,
                "variablePeriodType": "Month",
                "averagingPeriod":1,
                "averagingPeriodType":"Decade",
                "variableUnits" : "C",
                "variableID" : 1,
                "lastUpdate" : "12/19/2016, 7:00:00 PM"
              }
              ]
            }
    """
    ## check to see if sourceID is set as a number
    try:
        int(sourceID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: sourceID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    producer = request.query.producer
    model = request.query.model
    modelVersion = request.query.modelVersion
    modelScenario = request.query.modelScenario
    productURL = request.query.modelURL
    if model == '':
        model = None
    else:
        model = model.lower()
    if producer == '':
        producer = None
    else:
        producer = producer.lower()
    if modelScenario == '':
        modelScenario = None
    else:
        modelScenario = modelScenario.lower()
    if modelVersion == '':
        modelVersion = None
    if productURL == '':
        productURL = None
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## see if the resource exists
    query  = '''SELECT count(*) from sources where sourceID = %(sourceID)s;'''
    cursor.execute(query, {'sourceID' : sourceID})
    count = cursor.fetchone()[0]
    if count == 0:
        ## resource does not exist, return 404
        r = JSONResponse(data=[], success=False, message = template("Source {{sourceID}} does not exist.", sourceID=sourceID), status=404, timestamp='auto')
        return bottle.HTTPResponse(status=404, body=r.toJSON())
    ## otherwise, it does exit, so modify
    query = """
        UPDATE sources
        SET
           producer = coalesce(%(producer)s, producer),
           model = coalesce(%(model)s, model),
           scenario = coalesce(%(modelScenario)s, scenario),
           productVersion = coalesce(%(modelVersion)s, productVersion),
           productURL = coalesce(%(productURL)s, productURL)
        WHERE
            sourceid = %(sourceID)s;
        """
    cursor.execute(query, {'model': model, 'producer' : producer,'modelVersion':modelVersion,
                           'modelScenario' : modelScenario, 'productURL': productURL, 'sourceID':sourceID})
    ## select the newly modified copy
    query = "SELECT sourceID, producer, model, productVersion, productURL, lastUpdate FROM sources WHERE sourceID = %(sourceID)s"
    header = ['sourceID', 'producer', 'model', 'productVersion', 'productURL', 'lastUpdate']
    cursor.execute(query, {'sourceID':sourceID})
    ## format response
    row = cursor.fetchone()
    out = []
    d = {}
    i = 0
    while i < len(row):
        col = header[i]
        val = row[i]
        d[col] = val
        i += 1
    d['lastUpdate'] = d['lastUpdate'].strftime("%Y-%m-%d %H:%M:%S")
    out.append(d)
    r = JSONResponse(data=out, success=True, message = template("Updated source {{sourceID}} ", sourceID=sourceID), status=201, timestamp='auto')
    return bottle.HTTPResponse(status=201, body=r.toJSON())

## DELETE a source from the database by its id
@delete("/sources/<sourceID>")
def deleteSourceByID(sourceID):
    """DELETE a source in the database using its sourceID
        Parameters:
            @:param: sourceID (integer) [required]
        Returns:
            HTTP Response
            HTTP Status Codes: 204 (request successful, resource deleted or did not exist)
            Example:
                {
                  "message" : "Deleted source 231",
                  "success" : true,
                  "status" : 204,
                  "timestamp" : "12/19/2016, 7:00:00 PM",
                  "data" : []
                }
    """
    ## check to see if sourceID is set as a number
    try:
        int(sourceID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: sourceID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    query = """
        DELETE FROM Sources
        WHERE 1 = 1
        AND
        sourceID = %(sourceID)s;
        """
    cursor.execute(query, {'sourceID' : sourceID})
    r = JSONResponse(data=[], success=True, message = template("Deleted source {{sourceID}} from the database", sourceID=sourceID), status=204, timestamp='auto')
    code = 204
    return bottle.HTTPResponse(status=code, body=r.toJSON())

## Search for layers
@get("/layers")
def getlayers():
    """Get a list of layers meeting query parameters.
        layers are the actual datasets held within the database are refer to a specific raster table
        Parameters:
            @:param: variableType (string) [optional]
            @:param: variablePeriod (number) [optional]
            @:param: variablePeriodType (string) [optional]
            @:param: averagingPeriod (string) [optional]
            @:param: averagingPeriodType (string) [optional]
            @:param: variableID (integer) [optional]
            @:param: sourceID (integer) [optional]
            @:param: sourceProducer (string) [optional]
            @:param: modelName (string) [optional]
            @:param: modelVersion (number) [optional]
            @:param: resolution (number) [optional]
            @:param: scenario (string) [optional]
        :returns:
            HTTP Response
            HTTP Statuses: 200 (request successful)
            Example:
                {
                "success": true,
                "status": 200,
                "message": "",
                "timestamp" : "1/1/2000 5:17pm",
                "data": [
                  {
                    "layerID" : 15,
                    "yearsBP":22000,
                    "variableID" : 22,
                    "variableType" : "Tmax"
                    "variableDescription" : "Decadal Average January Maximum Temperature"
                    "variablePeriod" : 1,
                    "VariablePeriodType" : "Month",
                    "AveragingPeriod" : 1,
                    "AveragingPeriodType" : "Decade",
                    "AveragingPeriodDays" : 3650,
                    "SourceID" : 2,
                    "DataProducer" : "NCAR",
                    "Model" :"CCSM",
                    "ModelVersion" : 3,
                    "TableName" : "ce7sf23wzs5d93"
                  }
                ]
                }
    """
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## parse the input
    yearsBP = request.query.yearsBP
    variableType = request.query.variableType
    variablePeriod = request.query.variablePeriod
    variablePeriodType = request.query.variablePeriodType
    averagingPeriod = request.query.averagingPeriod
    averagingPeriodType = request.query.averagingPeriodType
    variableID = request.query.variableID
    sourceID = request.query.sourceID
    sourceProducer = request.query.sourceProducer
    modelName = request.query.modelName
    modelVersion = request.query.modelVersion
    resolution = request.query.resolution
    modelScenario = request.query.scenario
    if yearsBP == '':
        yearsBP = None
    if variableType == '':
        variableType = None
    else:
        variableType = variableType.lower()
    if variablePeriod == '':
        variablePeriod = None
    if variablePeriodType == '':
        variablePeriodType = None
    else:
        variablePeriodType = variablePeriodType.lower()
    if averagingPeriod == '':
        averagingPeriod = None
    if averagingPeriodType == '':
        averagingPeriodType = averagingPeriodType.lower()
    if variableID == '':
        variableID = None
    if sourceID == '':
        sourceID = None
    if sourceProducer == '':
        sourceProducer = None
    else:
        sourceProducer = sourceProducer.lower()
    if modelName == '':
        modelName = None
    else:
        modelName = modelName.lower()
    if modelVersion == '':
        modelVersion = None
    if modelScenario == '':
        modelScenario = None
    else:
        modelScenario = modelScenario.lower()
    if resolution == '':
        resolution = None

    query = '''
        SELECT
            yearsBP, rasterindex.variableID, variableTypes.variableType, variables.variableDescription, variables.variablePeriod,
            variablePeriodTypes.variablePeriodType, variables.variableAveraging, variableUnits.variableUnit, averagingPeriodTypes.averagingPeriodType,
            sources.sourceID, sources.producer, sources.model, sources.productVersion, sources.scenario, "tableName", rasterindex.lastUpdate
        from rasterIndex
        INNER JOIN variables on rasterIndex.variableID=variables.variableID
        INNER JOIN sources on rasterIndex.sourceID = sources.sourceID
        INNER JOIN variableTypes on variables.variableType = variableTypes.variableTypeID
        INNER JOIN variableUnits on variables.variableUnits = variableUnits.variableUnitID
        INNER JOIN averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID
        INNER JOIN variablePeriodTypes on variables.variablePeriodType = variablePeriodTypes.variablePeriodTypeID
        WHERE 1 = 1
            AND (%(yearsBP)s is NULL or %(yearsBP)s = rasterIndex.yearsBP)
            AND (%(variableType)s is NULL or %(variableType)s LIKE lower(variableTypes.variableTypeAbbreviation) )
            AND (%(variablePeriod)s is NULL or %(variablePeriod)s = variables.variablePeriod )
            AND (%(variablePeriodType)s is NULL or %(variablePeriodType)s LIKE lower(variablePeriodTypes.variablePeriodType) )
            AND (%(averagingPeriod)s is NULL or %(averagingPeriod)s = variableAveraging )
            AND (%(averagingPeriodType)s is NULL or %(averagingPeriodType)s LIKE lower(averagingPeriodTypes.averagingPeriodType) )
            AND (%(variableID)s is NULL or %(variableID)s = rasterIndex.variableID)
            AND (%(sourceID)s is NULL or %(sourceID)s = rasterIndex.sourceID)
            AND (%(resolution)s is NULL or %(resolution)s = resolution)
            AND (%(modelName)s is NULL or %(modelName)s LIKE lower(sources.model) )
            AND (%(sourceProducer)s is NULL or %(sourceProducer)s LIKE lower(sources.producer) )
            AND (%(modelVersion)s is NULL or %(modelVersion)s = sources.productVersion )
            AND (%(modelScenario)s is NULL or %(modelScenario)s LIKE lower(scenario) );
        '''

    params = {
        'yearsBP' : yearsBP,
        'variableType' : variableType,
        'variablePeriod':variablePeriod,
        'variablePeriodType' :variablePeriodType,
        'variableID' : variableID,
        'averagingPeriod' : averagingPeriod,
        'averagingPeriodType' : averagingPeriodType,
        'sourceID': sourceID,
        'sourceProducer':sourceProducer,
        'modelName' :modelName,
        'modelVersion' : modelVersion,
        'resolution': resolution,
        'modelScenario' : modelScenario
    }
    header = ['yearsBP', 'variableID', 'variableType', 'ariableDescription', 'variablePeriod',
            'ariablePeriodType', 'variableAveraging', 'variableUnits', 'averagingPeriodType',
            'sourceID', 'producer', 'model', 'productVersion', 'scenario', 'tableName', 'lastUpdate']
    cursor.execute(query, params) ## do the search
    ## format the output
    out = []
    rows = cursor.fetchall()
    for row in rows:
        i = 0
        d = {}
        while i <  len(header):
            col = header[i]
            val = row[i]
            d[col] = val
            i += 1
        d['lastUpdate'] = d['lastUpdate'].strftime("%Y-%m-%d %H:%M:%S")
        out.append(d)
    r = JSONResponse(data=out, success=True, message="", status=200)
    return bottle.HTTPResponse(status=200, body=r.toJSON())

## POST A new layer
## ---> will required a posting of the actual data too
@post("/layers")
def addLayer():
    """NOT YET IMPLEMENTED"""
    #TODO:Implement this
    r = JSONResponse(data=[], message="POSTing to add new layer has not been implemented.", status=501)
    return bottle.HTTPResponse(status=501, body=r.toJSON())

## GET Layer details by ID
@get("/layers/<layerID>")
def getLayerByID(layerID):
    """GET details about a layer using its layerID
        Paramters:
            @:param: layerID (integer) [required]
        :returns:
            HTTP Response
            HTTP Statuses: 200 (request successful, resource exists), 404 (request failed, resource exists)
            Example:
                {
                "success": true,
                "status": 200,
                "message": "",
                "timestamp" : "1/1/2000 5:17pm",
                "data": [
                  {
                    "layerID" : 15,
                    "yearsBP":22000,
                    "variableID" : 22,
                    "variableType" : "Tmax"
                    "variableDescription" : "Decadal Average January Maximum Temperature"
                    "variablePeriod" : 1,
                    "VariablePeriodType" : "Month",
                    "AveragingPeriod" : 1,
                    "AveragingPeriodType" : "Decade",
                    "AveragingPeriodDays" : 3650,
                    "SourceID" : 2,
                    "DataProducer" : "NCAR",
                    "Model" :"CCSM",
                    "ModelVersion" : 3,
                    "TableName" : "ce7sf23wzs5d93"
                  }
                ]
                }
    """
    ## check to see if layerID is set as a number
    try:
        int(layerID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: layerID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''
        SELECT
            yearsBP, layers.variableID, variableTypes.variableType, variables.variableDescription, variables.variablePeriod,
            variablePeriodTypes.variablePeriodType, variables.variableAveraging, variableUnits.variableUnit, averagingPeriodTypes.averagingPeriodType,
            sources.sourceID, sources.producer, sources.model, sources.productVersion, sources.scenario, tableName, lastUpdate
        from rasterIndex
        INNER JOIN variables on rasterIndex.variableID=variables.variableID
            sources on rasterIndex.sourceID = sources.sourceID
            variableTypes on variables.variableType = variableTypes.variableTypeID
            variableUnits on variables.variableUnits = variableUnits.variableUnitID
            averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID
            variablePeriodTypes on variables.variablePeriodType = variablePeriodTypes.variablePeriodTypeID
        WHERE 1=1
        AND recordID=%(layerID)s;
        '''
    params = {
        'layerID':layerID
    }
    header = ['yearsBP', 'variableID', 'variableType', 'ariableDescription', 'variablePeriod',
            'ariablePeriodType', 'variableAveraging', 'variableUnits', 'averagingPeriodType',
            'sourceID', 'producer', 'model', 'productVersion', 'scenario', 'tableName', 'lastUpdate']
    cursor.execute(query, params) ## do the search
    ## format the response
    out = []
    rows = cursor.fetchall()
    for row in rows:
        i = 0
        d = {}
        while i <  len(row):
            col = header[i]
            val = row[i]
            d[col] = val
            i += 1
        d['lastUpdate'] = d['lastUpdate'].strftime("%Y-%m-%d %H:%M:%S")
        out.append(d)
    if len(out) == 0:
        ## resource does not exist, return 404
        r = JSONResponse(data = [], message="Layer does not exist.  You can POST a new one with the /layers resource.", status=404)
        code = 404
    else:
        ## resource exists, return 200
        r = JSONResponse(data = out, message="", status=200)
        code = 200
    return bottle.HTTPResponse(status=code, body=r.toJSON())


## DELETE a Layer and the associated raster table
@delete("/layers/<layerID>")
def deleteLayerByID(layerID):
    """Delete a layer in the layers table using its layerID
        Parameters:
            @:param: layerID (integer) [required]
        :returns:
            HTTP Response
            HTTP Statuses: 204 (request successful, resource deleted or did not exist)
            Example:
                {
                  "success" : true,
                  "timestamp" : "1/1/2000 5:17pm",
                  "message" : "Layer 231 deleted.",
                  "status" : 204,
                  "data" : []
                }
    """
    ## check to see if layerID is set as a number
    try:
        int(layerID)
    except (TypeError,ValueError):
        ## required parameters not set, return 400
        r = JSONResponse(data=[], success=False, message = "Required parameters not set.  Required parameters: layerID", status=400, timestamp='auto')
        code = 400
        return bottle.HTTPResponse(status=code, body=r.toJSON())
    conn = connectToDefaultDatabase()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ## first get the table name from the row
    query = "SELECT tableName FROM rasterIndex WHERE recordID = %(layerID)s;"
    cursor.execute(query, {'layerID':layerID})
    row = cursor.fetchone()
    if len(row) == 0:
        ## table doesn't exit
        message = "WARNING: associated table does not exist so was not deleted."
    else:
        tableName = row[0]
        query = "IF EXISTS (SELECT relname FROM pg_class WHERE relname=%(tableName)s) THEN DROP TABLE %(tableName)s;"
        cursor.execute(query, {'tableName' : tableName})
        conn.commit()
        message = "Table drop successful. "
    ## now drop the layer record
    query = "DELETE from rasterIndex where recordID = %(layerID)s;"
    cursor.execute(query, {'layerID' : layerID})
    message = template(message + " Deleted {{layerID}} from database.", layerID  = layerID)
    r = JSONResponse(data = [], message=message, status=204)
    return bottle.HTTPResponse(status=204, body=r.toJSON())

## update a layer
@put("/layers/<layerID>")
def updateLayer(layerID):
    """Update layer details using its layerID and return the updated copy.
    Parameters
        @:param: layerID (integer) [required]
    :returns:
        HTTP Response
        HTTP Statuses: 201 (request successful, resource modified), 404 (request failed, resource does not exist), 200 (resource exits, not modified)
        Example:
            {
            "success" : true,
            "message" : "Updated layer 231",
            "timestamp" : "1/1/2000 5:17pm",
            "data" : [
            {
              "layerID" : 231,
              "yearsBP":22000,
              "variableID" : 22,
              "variableType" : "Tmax"
              "variableDescription" : "Decadal Average January Maximum Temperature"
              "variablePeriod" : 1,
              "VariablePeriodType" : "Month",
              "AveragingPeriod" : 1,
              "AveragingPeriodType" : "Decade",
              "AveragingPeriodDays" : 3650,
              "SourceID" : 2,
              "DataProducer" : "NCAR",
              "Model" :"CCSM",
              "ModelVersion" : 3,
              "TableName" : "ce7sf23wzs5d93"
            }
            ]
            }
    """
    ##TODO: Implement this
    r = JSONResponse(data=[], success=False, message="Resource not yet implemented.", status=501)
    return bottle.HTTPResponse(status=501, body=r.toJSON())


## DATA
## GET Data
@get("/data")
def getData():
    """Get data from the raster datasets stored in the database.
    Filtering available on variables and sources.
    Spatial input:
        Latitude/Longitude: [supported]
        Bounding Box: [not yet implemented]
    Parameters:
        @:param: latitude (number) [required]
        @:param: longitude (number) [required]
        @:param: bbox [not yet implemented]
        @:param: yearsBP (number) [required]
        @:param: variableType (string) [optional]
        @:param: variablePeriod (integer) [optional]
        @:param: variablePeriodType (string) [optional]
        @:param: averagingPeriod (integer) [optional]
        @:param: averagingPeriodType (string) [optional]
        @:param: variableID (integer) [optional]
        @:param: sourceID (integer) [optional]
        @:param: modelName (string) [optional]
        @:param: modelVersion (number) [optional]
        @:param: scenario (string) [optional]
        @:param: resolution (number) [optional]
    :returns:
        HTTP Response
        HTTP Statuses: 200 (request successful)
        Example:
            {
              "success" : true,
              "timestamp" : "1/1/2000 5:17pm",
              "status" : 200,
              "message" : "",
              "data" : [
                "layerID" : 231,
                "variableID" :43,
                "sourceID" :2,
                "latitude" : 37.12,
                "longitude" : -124.235,
                "value" : 34.1,
                "yearsBP" : 22000
              ]
            }
    Implementation Notes:
        This is jerry-rigged to just do nearest neighbor interpolation (onto 1000 year intervals) until I have enough time to do k-nn or linear interpolation
        Also, the sql query is at risk of being unsafe, because I don't know how to properly parameterize the table name input.
    """
    #TODO: Add interpolation between time period
    #TODO: Add bounding box
    latitude = request.query.latitude
    longitude = request.query.longitude
    yearsBP = request.query.yearsBP
    if latitude == '' or longitude == '' or yearsBP == '':
        ## required parameters are not set
        r = JSONResponse(data= [], message = "Required parameters not set.  Required parameters: latitude, longitude, yearsBP", status=400)
        return bottle.HTTPResponse(status=400, body=r.toJSON())
    try:
        yearsBP = int(yearsBP)
    except (ValueError, TypeError):
        ## years BP isnt a number
        r = JSONResponse(data= [], message = "Required parameters not set.  Years BP must be numeric.", status=400)
        return bottle.HTTPResponse(status=400, body=r.toJSON())

    ## all other parameters are optional
    ## round time
    roundYear = int(math.ceil(yearsBP / 1000.0)) * 1000

    variableType = request.query.variableType
    if variableType == '':
        variableType = None
    variablePeriod = request.query.variablePeriod
    if variablePeriod == '':
        variablePeriod = None
    variablePeriodType = request.query.variablePeriodType
    if variablePeriodType == '':
        variablePeriodType = None
    variableUnits = request.query.variableUnits
    if variableUnits == '':
        variableUnits = None
    else:
        variableUnits = variableUnits.lower()
    averagingPeriod = request.query.averagingPeriod
    if averagingPeriod == '':
        averagingPeriod = None
    averagingPeriodType = request.query.averagingPeriodType
    if averagingPeriodType == '':
        averagingPeriodType = None
    variableID = request.query.variableID
    if variableID == '':
        variableID = None
    sourceID = request.query.sourceID
    if sourceID == '':
        sourceID = None
    sourceProducer = request.query.sourceProducer
    if sourceProducer == '':
        sourceProducer = None
    modelName = request.query.modelName
    if modelName == '':
        modelName = None
    modelVersion = request.query.modelVersion
    if modelVersion == '':
        modelVersion = None
    resolution = request.query.resolution
    if resolution == '':
        resolution = None
    modelScenario = request.query.scenario
    if modelScenario == '':
        modelScenario = None
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    print "Collected query parameters."
    ## fetch the table names that match our query
        query = '''
            SELECT
                "tableName", sources.sourceID, sources.model, sources.producer, sources.productVersion, variables.variableID,
                variables.variabledescription, variableTypes.variableType, variableUnits.variableUnitAbbreviation, variables.variablePeriod,
                variablePeriodTypes.variablePeriodType, variables.variableAveraging, averagingPeriodTypes.averagingPeriodType, yearsBP
            from rasterIndex
            INNER JOIN variables on rasterIndex.variableID=variables.variableID
            INNER JOIN    sources on rasterIndex.sourceID = sources.sourceID
            INNER JOIN    variableTypes on variables.variableType = variableTypes.variableTypeID
            INNER JOIN    variableUnits on variables.variableUnits = variableUnits.variableUnitID
            INNER JOIN    averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID
            INNER JOIN    variablePeriodTypes on variables.variablePeriodType = variablePeriodTypes.variablePeriodTypeID
            WHERE 1 = 1
                AND (%(variableType)s is NULL or %(variableType)s LIKE lower(variableTypes.variableTypeAbbreviation) )
                AND (%(variablePeriod)s is NULL or %(variablePeriod)s = variables.variablePeriod )
                AND (%(variablePeriodType)s is NULL or %(variablePeriodType)s LIKE lower(variablePeriodTypes.variablePeriodType) )
                AND (%(averagingPeriod)s is NULL or %(averagingPeriod)s = variableAveraging )
                AND (%(averagingPeriodType)s is NULL or %(averagingPeriodType)s LIKE lower(averagingPeriodTypes.averagingPeriodType) )
                AND (%(variableUnits)s is NULL or %(variableUnits)s LIKE lower(variableUnits.variableUnitAbbreviation))
                AND (%(variableID)s is NULL or %(variableID)s = variables.variableID)
                AND (%(sourceID)s is NULL or %(sourceID)s = sources.sourceID)
                AND (%(resolution)s is NULL or %(resolution)s = resolution)
                AND (%(modelName)s is NULL or %(modelName)s LIKE lower(sources.model) )
                AND (%(sourceProducer)s is NULL or %(sourceProducer)s LIKE lower(sources.producer) )
                AND (%(modelVersion)s is NULL or %(modelVersion)s = sources.productVersion )
                AND (%(modelScenario)s is NULL or %(modelScenario)s LIKE lower(scenario) )
                AND (yearsBP = %(yearsBP)s);
            '''

    params = {
        'variableType' : variableType,
        'variablePeriod':variablePeriod,
        'variablePeriodType' :variablePeriodType,
        'variableUnits' : variableUnits,
        'variableID' : variableID,
        'averagingPeriod' : averagingPeriod,
        'averagingPeriodType' : averagingPeriodType,
        'sourceID': sourceID,
        'sourceProducer':sourceProducer,
        'modelName' :modelName,
        'modelVersion' : modelVersion,
        'resolution': resolution,
        'modelScenario' : modelScenario,
        'yearsBP' : roundYear
    }
    cursor.execute(query, params)
    rows = cursor.fetchall()
    header = [ "tableName", "sourceID", "Model", "Producer", "ModelVersion", "variableID",
    "VariableDescription", "VariableType", "variableUnits", "variablePeriod", "variablePeriodType", "averagingPeriod", "averagingPeriodType", "yearsBP"]

    out = []
    ## fetch the actual point data from each of the returned tables
    for row in rows:
        try:
            tableName = row[0]
            ## this is hacky and bad, but it works...
            ## dangerous if we make it public
            query = '''SELECT ST_Value(rast,ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326)) FROM public.''' + tableName + '''
                WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326));
            '''
            params = { 'latitude' : latitude, 'longitude' : longitude}
            cursor.execute(query, params)
            tableRow = cursor.fetchone()
            if len(row) == 0: ## no results were returned, likely because point was outside of north america
                val = None
            else:
                val = tableRow[0]
            i = 0
            d = {}
            while i < len(header): ## add metadata about the table
                col = header[i]
                d[col] = row[i]
                i += 1
            d['value'] = val ## this is the actual point value
            d['latitude'] = float(latitude)
            d['longitude'] = float(longitude)
            out.append(d)
        except Exception as e: ## table doesn't exist, but record for table does exist --> oops
            conn.rollback()
            pass
    r = JSONResponse(data = out, message="Interpolation is nearest neighbor to closest 1000 year slice.", status=200)
    return bottle.HTTPResponse(status=200, body= r.toJSON())

## POST data
## This uses post so it can send a bigger payload with {lat, lng, time} objects and get a list of responses in return
## If this works, it prevents us from having to send individual api calls for sites, we can do it all in one
@post("/data")
def postData():
    """Get data from the raster datasets stored in the database for an array of [lat, lng, time] tuples.
    Filtering available on variables and sources.
    Spatial input:
        Latitude/Longitude: [supported]
        Bounding Box: [not yet implemented]
    Parameters:
        @:param: locations (array) [required]
            @:type: {
                latitude: latitude (number),
                longitude: longitude (number),
                yearsBP: yearsBP  (number)
            }
        @:param: latitude (number) [required]
        @:param: longitude (number) [required]
        @:param: bbox [not yet implemented]
        @:param: yearsBP (number) [required]
        @:param: variableType (string) [optional]
        @:param: variablePeriod (integer) [optional]
        @:param: variablePeriodType (string) [optional]
        @:param: averagingPeriod (integer) [optional]
        @:param: averagingPeriodType (string) [optional]
        @:param: variableID (integer) [optional]
        @:param: sourceID (integer) [optional]
        @:param: modelName (string) [optional]
        @:param: modelVersion (number) [optional]
        @:param: scenario (string) [optional]
        @:param: resolution (number) [optional]
    :returns:
        HTTP Response
        HTTP Statuses: 200 (request successful)
        Example:
            {
              "success" : true,
              "timestamp" : "1/1/2000 5:17pm",
              "status" : 200,
              "message" : "",
              "data" : [
                "layerID" : 231,
                "variableID" :43,
                "sourceID" :2,
                "latitude" : 37.12,
                "longitude" : -124.235,
                "value" : 34.1,
                "yearsBP" : 22000
              ]
            }
    Implementation Notes:
        See notes for GET
    """
    #TODO: Add interpolation between time period
    #TODO: Add bounding box
    r = request.json
    ## do basic type checking
    if 'locations' not in r:
        r = JSONResponse(data= [], message = "Required parameters not set.  Required parameters: Locations", status=400)
        return bottle.HTTPResponse(status=400, body=r.toJSON())
    i = 0
    while i < len(r['locations']):
        try:
            r['locations'][i]['latitude'] = float(r['locations'][i]['latitude'])
            r['locations'][i]['longitude'] = float(r['locations'][i]['longitude'])
            r['locations'][i]['yearsBP'] = float(r['locations'][i]['yearsBP'])
        except KeyError:
            r = JSONResponse(data= [], message = "Invalid formatting for locations, location index " + str(i), status=400)
            return bottle.HTTPResponse(status=400, body=r.toJSON())
        except ValueError:
            r = JSONResponse(data= [], message = "Encountered non-numeric location, location index " + str(i), status=400)
            return bottle.HTTPResponse(status=400, body=r.toJSON())
        i += 1
    print "Passed required variable checks."

    ## all other parameters are optional and apply to the request as a whole
    ## these requests come from the json body though
    locations = r['locations']
    if 'variableType' not in r:
        variableType = None
    else:
        variableType = r['variableType'].lower()
    if 'variablePeriod' not in r:
        variablePeriod = None
    else:
        variablePeriod = r['variablePeriod']
    if 'variablePeriodType' not in r:
        variablePeriodType = None
    else:
        variablePeriodType = r['variablePeriodType'].lower()
    if 'variableUnits' not in r:
        variableUnits = None
    else:
        variableUnits = r['variableUnits'].lower()
    if 'averagingPeriod' not in r:
        averagingPeriod = None
    else:
        averagingPeriod = r['averagingPeriod']
    if 'averagingPeriodType' not in r:
        averagingPeriodType = None
    else:
        averagingPeriodType = r['averagingPeriodType'].lower()
    if 'variableID' not in r:
        variableID = None
    else:
        variableID = r['variableID']
    if 'sourceID' not in r:
        sourceID = None
    else:
        sourceID = r['sourceID']
    if 'sourceProducer' not in r:
        sourceProducer = None
    else:
        sourceProducer = r['sourceProducer'].lower()
    if 'modelName' not in r:
        modelName = None
    else:
        modelName = r['modelName'].lower()
    if 'modelVersion' not in r:
        modelVersion = None
    else:
        modelVersion = r['modelVersion'].lower()
    if 'resolution' not in r:
        resolution = None
    else:
        resolution = r['resolution']
    if 'modelScenario' not in r:
        modelScenario = None
    else:
        modelScenario = r['modelScenario']
    conn = connectToDefaultDatabase()
    cursor = conn.cursor()
    print "Collected query parameters."
    i = 0;
    t0 = datetime.datetime.now()
    ## now just iterate through and do the basic GETTING but for all locations in the request
    out = [] ## collect them all in here
    i = 0
    while i < len(locations):
        thisLocation = locations[i]
        latitude = thisLocation['latitude']
        longitude = thisLocation['longitude']
        yearsBP = thisLocation['yearsBP']
        t1 = datetime.datetime.now()
        try:
            siteName = thisLocation['siteName']
        except KeyError:
            siteName = ""
        try:
            siteID = thisLocation['siteID']
        except KeyError:
            siteID = ""
        roundYear = int(math.ceil(yearsBP / 1000.0)) * 1000 ## this is the interpolation

        siteOut = {}
        siteOut['siteName'] = siteName
        siteOut['siteID'] = siteID
        siteOut['latitude'] = latitude
        siteOut['longitude'] = longitude
        siteOut['yearsBP'] = yearsBP
        siteOut['data'] = []
        # fetch the table names that match our query
        query = '''
            SELECT
                "tableName", sources.sourceID, sources.model, sources.producer, sources.productVersion, variables.variableID,
                variables.variabledescription, variableTypes.variableType, variableUnits.variableUnitAbbreviation, variables.variablePeriod,
                variablePeriodTypes.variablePeriodType, variables.variableAveraging, averagingPeriodTypes.averagingPeriodType, yearsBP
            from rasterIndex
            INNER JOIN variables on rasterIndex.variableID=variables.variableID
            INNER JOIN    sources on rasterIndex.sourceID = sources.sourceID
            INNER JOIN    variableTypes on variables.variableType = variableTypes.variableTypeID
            INNER JOIN    variableUnits on variables.variableUnits = variableUnits.variableUnitID
            INNER JOIN    averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID
            INNER JOIN    variablePeriodTypes on variables.variablePeriodType = variablePeriodTypes.variablePeriodTypeID
            WHERE 1 = 1
                AND (%(variableType)s is NULL or %(variableType)s LIKE lower(variableTypes.variableTypeAbbreviation) )
                AND (%(variablePeriod)s is NULL or %(variablePeriod)s = variables.variablePeriod )
                AND (%(variablePeriodType)s is NULL or %(variablePeriodType)s LIKE lower(variablePeriodTypes.variablePeriodType) )
                AND (%(averagingPeriod)s is NULL or %(averagingPeriod)s = variableAveraging )
                AND (%(averagingPeriodType)s is NULL or %(averagingPeriodType)s LIKE lower(averagingPeriodTypes.averagingPeriodType) )
                AND (%(variableUnits)s is NULL or %(variableUnits)s LIKE lower(variableUnits.variableUnitAbbreviation))
                AND (%(variableID)s is NULL or %(variableID)s = variables.variableID)
                AND (%(sourceID)s is NULL or %(sourceID)s = sources.sourceID)
                AND (%(resolution)s is NULL or %(resolution)s = resolution)
                AND (%(modelName)s is NULL or %(modelName)s LIKE lower(sources.model) )
                AND (%(sourceProducer)s is NULL or %(sourceProducer)s LIKE lower(sources.producer) )
                AND (%(modelVersion)s is NULL or %(modelVersion)s = sources.productVersion )
                AND (%(modelScenario)s is NULL or %(modelScenario)s LIKE lower(scenario) )
                AND (yearsBP = %(yearsBP)s);
            '''

        params = {
            'variableType' : variableType,
            'variablePeriod':variablePeriod,
            'variablePeriodType' :variablePeriodType,
            'variableUnits' : variableUnits,
            'variableID' : variableID,
            'averagingPeriod' : averagingPeriod,
            'averagingPeriodType' : averagingPeriodType,
            'sourceID': sourceID,
            'sourceProducer':sourceProducer,
            'modelName' :modelName,
            'modelVersion' : modelVersion,
            'resolution': resolution,
            'modelScenario' : modelScenario,
            'yearsBP' : roundYear
        }
        cursor.execute(query, params)
        rows = cursor.fetchall()
        header = [ "tableName", "sourceID", "Model", "Producer", "ModelVersion", "variableID",
        "VariableDescription", "VariableType", "variableUnits", "variablePeriod", "variablePeriodType", "averagingPeriod", "averagingPeriodType", "yearsBP"]
        # ## fetch the actual point data from each of the returned tables
        t2 = datetime.datetime.now()
        print "Got table list in", t2 - t1
        for row in rows:
            tableName = row[0]
            q = '''SELECT ST_Value(rast,ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326)) FROM public.''' + tableName + '''
                WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326)); '''
            params = { 'latitude' : latitude, 'longitude' : longitude}
            try:
                cursor.execute(q, params)
            except Exception as e:
                print str(e)
                conn.rollback()
            for res in cursor.fetchall():
                if len(res) == 0: ## no results were returned, likely because point was outside of north america
                    val = None
                else:
                    val = res[0]
                p = 0
                d = {}
                while p < len(header): ## add metadata about the table
                    col = header[p]
                    d[col] = row[p]
                    p += 1
                d['value'] = val ## this is the actual point value
                siteOut['data'].append(d)
        print "---------------"
        out.append(siteOut)
        i += 1
    t6 = datetime.datetime.now()
    print "------"
    print t6 - t0
    print "------"
    r = JSONResponse(data = out, message="Interpolation is nearest neighbor to closest 1000 year slice.", status=200)
    return bottle.HTTPResponse(status=200, body= r.toJSON())

@route("/data", method=['OPTIONS'])
def returnOptions():
    return bottle.HTTPResponse(status=200)

run(server='paste', host='0.0.0.0',  port=8080, debug=True)
