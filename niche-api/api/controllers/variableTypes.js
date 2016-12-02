var util = require('util');

function getVariableTypes(req, res) {
  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  var variableTypeID = req.swagger.params.variableTypeId.value || null
  var db = global.createConnection()
  var query = "SELECT * FROM variableTypes \
    WHERE 1=1\
      AND (${variableTypeID} IS NULL OR variabletypeid = ${variableTypeIDs});\
    "



  var queryVals = {'variableTypeID': variableTypeID}
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
  getVariableTypes: getVariableTypes
};
