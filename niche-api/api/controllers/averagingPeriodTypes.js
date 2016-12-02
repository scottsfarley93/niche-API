var util = require('util');

function getAveragingPeriodTypes(req, res) {
  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  var averagingPeriodTypeId = req.swagger.params.averagingPeriodTypeId.value || null
  var db = global.createConnection()
  var query = "SELECT * FROM averagingPeriodTypes \
    WHERE 1=1\
      AND (${averagingPeriodTypeId} IS NULL OR averagingPeriodTypeId = ${averagingPeriodTypeId});\
    "

  var queryVals = {'averagingPeriodTypeId': averagingPeriodTypeId}
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
  getAveragingPeriodTypes: getAveragingPeriodTypes
};
