var util = require('util');

function getVariablePeriodTypes(req, res) {
  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  var variablePeriodTypeID = req.swagger.params.variablePeriodTypeId.value || null
  var db = global.createConnection()
  var query = "SELECT * FROM variablePeriodTypes \
    WHERE 1=1\
      AND (${variablePeriodTypeID} IS NULL OR variablePeriodTypeID = ${variablePeriodTypeID});\
    "

  var queryVals = {'variablePeriodTypeID': variablePeriodTypeID}
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
  getVariablePeriodTypes: getVariablePeriodTypes
};
