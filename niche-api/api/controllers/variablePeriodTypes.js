//This is variablePeriodTypes.js
//GET a list of variable period types in the database
//A variable period type is the period over which the data is representitive
//For example, a month
//A January (1) variable period would have a variable period of month
//Annual precipitation would have a variable period of years

//v2.0



function getVariablePeriodTypes(req, res) {
  //GET a list of variable period types

  //get query variables
  //only allow query on id
  var variablePeriodTypeID = req.swagger.params.variablePeriodTypeId.value || null

  //connect to database
  var db = global.createConnection()

  //query the variable period types table
  var query = "SELECT * FROM variablePeriodTypes \
    WHERE 1=1\
      AND (${variablePeriodTypeID} IS NULL OR variablePeriodTypeID = ${variablePeriodTypeID});"

  var queryVals = {'variablePeriodTypeID': variablePeriodTypeID}

  //execute sql
  db.any(query, queryVals)
  //successful return --> return data
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
      //errors on sql call 
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
