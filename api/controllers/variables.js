//this is Variables.js
//GET information about the variables in the database
// v2.0

function getVariables(req, res) {
  //GET a list of all variables that currently have data associated with them in the database

  //get query parameters
  var variableType = req.swagger.params.variableType.value || null
  var variablePeriod = req.swagger.params.variablePeriod.value || null
  var variablePeriodType = req.swagger.params.variablePeriodType.value || null
  var averagingPeriod = req.swagger.params.averagingPeriod.value || null
  var averagingPeriodType = req.swagger.params.averagingPeriodType.value || null
  var variableUnits = req.swagger.params.variableUnits.value  || null
  var variableID = req.swagger.params.variableID.value  || null

  //create connection to database
  var db = global.createConnection()

  //get details about the variables in the database
  // only select variables for which there is at least one raster dataset
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
        AND (${variableUnits} IS NULL or variableUnits.variableUnitAbbreviation = ${variableUnits}) \
        AND (${variableID} IS NULL or rasterindex.variableID = ${variableID}) \
      ORDER BY rasterindex.variableID asc ;"


  //query data from API call
  var queryVals = {'variableType': variableType,
                    'variablePeriod' : variablePeriod,
                    'variablePeriodType':variablePeriodType,
                    'averagingPeriod' : averagingPeriod,
                    'averagingPeriodType' : averagingPeriodType,
                    'variableUnits' : variableUnits,
                    'variableID': variableID
                  }
  //execute SQL
  db.any(query, queryVals)
    .then(function(data){
      //return response to user
      var ts = new Date().toJSON()
      console.log("Success")
      var resOut = {
        "success" : true,
        "timestamp" : ts,
        data: data
      }
      res.json(resOut)
    }).catch(function(err){
      //error on SQL call
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
