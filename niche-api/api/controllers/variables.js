'use strict';
var util = require('util');

function getVariables(req, res) {
  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  var variableType = req.swagger.params.variableType || null
  var variablePeriod = req.swagger.params.variablePeriod || null
  var variablePeriodType = req.swagger.params.variablePeriodType || null
  var averagingPeriod = req.swagger.params.averagingPeriod || null
  var averagingPeriodType = req.swagger.params.averagingPeriodType || null
  var variableUnits = req.swagger.params.variableUnits || null
  var variableid = req.swagger.params.variableid || null

  var db = global.createConnection()
  var query = "select variableDescription, variablePeriod, variablePeriodTypes.variablePeriodType, variableUnits.variableUnit, \
      variableAveraging, averagingPeriodTypes.averagingPeriodType, variableID, lastUpdate \
      from variables \
      inner join variableTypes on variables.variableType = variableTypes.variableTypeID \
      inner join variableUnits on variables.variableUnits = variableUnits.variableUnitID \
      inner join variablePeriodTypes on variables.variablePeriod = variablePeriodTypes.variablePeriodTypeID \
      inner join averagingPeriodTypes on variables.variableAveragingType = averagingPeriodTypes.averagingPeriodTypeID \
      WHERE  ($(variableid) is NULL or $(variableid) = variables.variableid);"


  var queryVals = {'variableType': variableType,
                  'variablePeriod' : variablePeriod,
                    'variablePeriodType':variablePeriodType,
                         'averagingPeriod' : averagingPeriod,
                         'averagingPeriodType' : averagingPeriodType,
                         'variableUnits' : variableUnits,
                       'variableID' : variableID}
  db.any(query, queryVals)
    .then(function(data){
      console.log(data)
      res.json(data)
    }).catch(function(err){
      console.log(err)
      res.json(err)
    })
}



module.exports = {
  getVariables: getVariables
};
