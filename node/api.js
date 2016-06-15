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
    // query = " select variableDescription, variablePeriod, variablePeriodTypes.variablePeriodType, variableUnits.variableUnit, \
    //     variableAveraging, averagingPeriodTypes.averagingPeriodType, variableID, lastUpdate\
    //     from variables\
    //     inner join variableTypes on variables.variableType = variableTypes.variableTypeID\
    //     inner join variableUnits on variables.variableUnits = variableUnits.variableUnitID\
    //     inner join variablePeriodTypes on variables.variablePeriod = variablePeriodTypes.variablePeriodTypeID\
    //     inner join averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID\
    //     WHERE 1 = 1\
    //     AND\
    //         (($1) is NULL or ($1) LIKE lower(variableTypes.variableTypeAbbreviation) )\
    //         AND  (($2) is NULL or ($2) = variables.variablePeriod )\
    //          AND (($3) is NULL or ($3) LIKE lower(variablePeriodTypes.variablePeriodType) )\
    //         AND (($4)is NULL or ($4) = variableAveraging )\
    //         AND (($5) is NULL or ($5) LIKE lower(averagingPeriodTypes.averagingPeriodType) )\
    //         AND (($6) is NULL or ($6) LIKE lower(variableUnits.variableUnitAbbreviation))"
    q = "SELECT * FROM variableTypes where (($1) is NULL or ($1) LIKE lower(variableTypes.variableTypeAbbreviation));"
    console.log(query)
    //values = [variableType, variablePeriod, variablePeriodType, averagingPeriod, averagingPeriodType, variableUnits]
    values = [NaN]
    console.log(values)
    var query = client.query(q, values);
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
