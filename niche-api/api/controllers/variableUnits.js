var util = require('util');

function getVariableUnits(req, res) {
  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  var variableUnitId = req.swagger.params.variableUnitId.value || null
  var variableUnitAbbreviation = req.swagger.params.variableUnitAbbreviation.value || null

  var db = global.createConnection()
  var query = "SELECT * FROM variableUnits \
    WHERE 1=1\
      AND (${variableUnitId} IS NULL OR variableunitid = ${variableUnitId}) \
      AND (${variableUnitAbbreviation} IS NULL OR variableUnitAbbreviation = ${variableUnitAbbreviation}) \
      ;\
    "

  var queryVals = {'variableUnitAbbreviation': variableUnitAbbreviation, 'variableUnitId':variableUnitId}
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
  getVariableUnits: getVariableUnits
};
