//This is variableTypes.js
//GET a list of variable types in the database
//A variable type is a generic representation of what is measured
//For example, precipitation, maximum temperature, wind speed

//v2.0


function getVariableTypes(req, res) {
  //GET a list of all variable types in the database

  //Get query variables
  var variableTypeID = req.swagger.params.variableTypeId.value || null

  //connect to the database
  var db = global.createConnection()

  //query the variable types table
  var query = "SELECT * FROM variableTypes \
    WHERE 1=1\
      AND (${variableTypeID} IS NULL OR variabletypeid = ${variableTypeIDs});"

  var queryVals = {'variableTypeID': variableTypeID}

  //execute the sql query
  db.any(query, queryVals)
    .then(function(data){
      //successful query --> return data to the user
      var ts = new Date().toJSON()
      console.log("Success")
      var resOut = {
        "success" : true,
        "timestamp" : ts,
        data: data
      }
      res.json(resOut)
    }).catch(function(err){
      //error on sql call
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
