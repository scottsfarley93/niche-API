'use strict';
var util = require('util');

function getVariables(req, res) {
  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  var variableType = req.swagger.params.variableType.value || null
  var variablePeriod = req.swagger.params.variablePeriod.value || null
  var variablePeriodType = req.swagger.params.variablePeriodType.value || null
  var averagingPeriod = req.swagger.params.averagingPeriod.value || null
  var averagingPeriodType = req.swagger.params.averagingPeriodType.value || null
  var variableUnits = req.swagger.params.variableUnits.value  || null
  var variableID = req.swagger.params.variableID.value  || null

  console.log(variableType)

  var db = global.createConnection()
  var query = "select distinct variableDescription, variablePeriod, variableTypes.variabletype,\
        variableTypes.variabletypeabbreviation, \
        variablePeriodTypes.variablePeriodType, variableUnits.variableUnit, \
        variableAveraging, averagingPeriodTypes.averagingPeriodType, rasterindex.variableID \
      from rasterindex  \
      inner join variables on variables.variableid = rasterindex.variableid \
      inner join variableTypes on variables.variableType = variableTypes.variableTypeID \
      inner join variableUnits on variables.variableUnits = variableUnits.variableUnitID \
      inner join variablePeriodTypes on variables.variablePeriod = variablePeriodTypes.variablePeriodTypeID \
      inner join averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID \
      WHERE 1=1 \
        AND (${variableType} IS NULL or variableTypes.variabletypeid = ${variableType}) \
        AND (${variablePeriod} IS NULL or variablePeriod = ${variablePeriod}) \
        AND (${variablePeriodType} IS NULL or variableTypes.variabletype = ${variablePeriodType}) \
        AND (${averagingPeriod} IS NULL or variableAveraging = ${averagingPeriod}) \
        AND (${averagingPeriodType} IS NULL or averagingPeriodTypes.averagingPeriodType = ${averagingPeriodType}) \
        AND (${variableUnits} IS NULL or variableUnits.variableUnit = ${variableUnits}) \
        AND (${variableID} IS NULL or rasterindex.variableID = ${variableID}) \
      ORDER BY rasterindex.variableID asc ;"


  var queryVals = {'variableType': variableType,
                    'variablePeriod' : variablePeriod,
                    'variablePeriodType':variablePeriodType,
                    'averagingPeriod' : averagingPeriod,
                    'averagingPeriodType' : averagingPeriodType,
                    'variableUnits' : variableUnits,
                    'variableID': variableID
                  }
console.log(queryVals)

  db.any(query, queryVals)
    .then(function(data){
      var ts = new Date().toJSON()
      console.log("Success")
      var resOut = {
        "success" : true,
        "timestamp" : ts,
        data: data
      }
      res.json(resOut)
    }).catch(function(err){
      console.log(err)
      console.log("Fail")
      var resOut = {
        "status" : "500",
        "message" : "Failed Database Request"
      }
      res.json(resOut)
    })
}



module.exports = {
  getVariables: getVariables
};
