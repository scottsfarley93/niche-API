//This is variableUnits.js
//GET a list of the units in which data is measured in the database
//v2.0

function getVariableUnits(req, res) {
  //GET a list of variable units from the database
  //Not a list of variable units currently in use -- a full list of all available units

  //get query parameters
  var variableUnitId = req.swagger.params.variableUnitId.value || null
  var variableUnitAbbreviation = req.swagger.params.variableUnitAbbreviation.value || null

  //create connection to the database
  var db = global.createConnection()

  //query the variable units table
  var query = "SELECT * FROM variableUnits \
    WHERE 1=1\
      AND (${variableUnitId} IS NULL OR variableunitid = ${variableUnitId}) \
      AND (${variableUnitAbbreviation} IS NULL OR variableUnitAbbreviation = ${variableUnitAbbreviation}) \
      ;\
    "

  var queryVals = {'variableUnitAbbreviation': variableUnitAbbreviation, 'variableUnitId':variableUnitId}
  //execute SQL query
  db.any(query, queryVals)
    .then(function(data){
      //return data to the user
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
  getVariableUnits: getVariableUnits
};
