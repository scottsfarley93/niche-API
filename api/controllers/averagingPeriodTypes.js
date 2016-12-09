//This is averagingPeriodTypes.js
//GET a list of the period over which data can be averaged
//An averaging period is the amount of time that the data represents
//For example, decadally averaged precipitation

//v2.0

function getAveragingPeriodTypes(req, res) {
  //GET a list of all available averaging period types

  //get query values
  var averagingPeriodTypeId = req.swagger.params.averagingPeriodTypeId.value || null

  //create connection to database
  var db = global.createConnection()

  //query the averaging period type table
  var query = "SELECT * FROM averagingPeriodTypes \
    WHERE 1=1\
      AND (${averagingPeriodTypeId} IS NULL OR averagingPeriodTypeId = ${averagingPeriodTypeId});\
    "

  var queryVals = {'averagingPeriodTypeId': averagingPeriodTypeId}


  //execute sql query
  db.any(query, queryVals)
    .then(function(data){
      //successful execution, send data back to user
      var ts = new Date().toJSON()
      console.log("Success")
      var resOut = {
        "success" : true,
        "timestamp" : ts,
        data: data
      }
      res.json(resOut)
    }).catch(function(err){
      //errors on SQL call 
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
  getAveragingPeriodTypes: getAveragingPeriodTypes
};
