//Module imports
var http = require('http');
var express = require("express");
var dispatcher = require('httpdispatcher');
var pg = require('pg');


var app = express()


var bodyParser = require('body-parser');

// configure app to use bodyParser()
// this will let us get the data from a POST
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

var router = express.Router();


keys = {
  user : 'paleo',
  password : 'Alt0Sax!!',
  dbName : 'paleo',
  hostname : '127.0.0.1'
}

const PORT=8000;

app.get("/", function(req, res){
  //Root method to test if we have connection set up correctly and that postgres/postgis are installed on server machine
  var client = new pg.Client({
    user: keys.user,
    password: keys.password,
    database: keys.dbName,
    hostname: keys.hostname
  });
  console.log('Connect.')
  client.connect(function(err){
    if (err){
      console.log(err)
    }else{
      console.log("Done.")
    }
    var query = client.query("SELECT PostGIS_full_version();")
    query.on('row', function(row, result){
      console.log("Got row.")
      result.addRow(row);
    })
    query.on('end', function(result){
      res.json(result)
      client.end()
    })

  })
})


app.get("/variables", function(req, res){
  //get a list of the variables in the database
  var variableType = req.query.variableType
  if (variableType == undefined){
    variableType = null;
  }
  var variablePeriod = req.query.variablePeriod
  if (variablePeriod == undefined){
    variablePeriod = null
  }
  var variablePeriodType = req.query.variablePeriodType
  if (variablePeriodType == undefined){
    variablePeriodType = null;
  }
  var averagingPeriodType = req.query.averagingPeriodType
  if (averagingPeriodType == undefined){
    averagingPeriodType = null
  }
  var averagingPeriod = req.query.averagingPeriod
  if (averagingPeriod == undefined){
    averagingPeriod = null;
  }
  var variableUnits = req.query.averagingPeriod
  if (variableUnits == undefined){
    variableUnits = null
  }
  var client = new pg.Client({
    user: keys.user,
    password: keys.password,
    database: keys.dbName,
    hostname: keys.hostname
  })
  client.connect(function(err){
    if (err){
      res.json(err);
    }
    q = " select variableDescription, variablePeriod, variablePeriodTypes.variablePeriodType, variableUnits.variableUnit, \
        variableAveraging, averagingPeriodTypes.averagingPeriodType, variableID, lastUpdate\
        from variables\
        inner join variableTypes on variables.variableType = variableTypes.variableTypeID\
        inner join variableUnits on variables.variableUnits = variableUnits.variableUnitID\
        inner join variablePeriodTypes on variables.variablePeriod = variablePeriodTypes.variablePeriodTypeID\
        inner join averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID\
        WHERE 1 = 1\
        AND\
            (" + variableType + " is NULL or " + variableType + " LIKE lower(variableTypes.variableTypeAbbreviation) )\
            AND  (" + variablePeriod + " is NULL or " + variablePeriod + " = variables.variablePeriod )\
             AND (" + variablePeriodType + " is NULL or " + variablePeriodType + " LIKE lower(variablePeriodTypes.variablePeriodType) )\
            AND (" + averagingPeriod + "is NULL or " + averagingPeriod + " = variableAveraging )\
            AND (" + averagingPeriodType + " is NULL or " + averagingPeriodType + " LIKE lower(averagingPeriodTypes.averagingPeriodType) )\
            AND (" + variableUnits + " is NULL or " + variableUnits + " LIKE lower(variableUnits.variableUnitAbbreviation))"
    var query = client.query(q);
    console.log(query)
    query.on('row', function(row, result){
      console.log("Got row")
      result.addRow(row)
    })
    query.on('end', function(result){
      console.log("Done.")
      res.json(result)
      client.end()
    })
  })
})

app.listen(PORT);
