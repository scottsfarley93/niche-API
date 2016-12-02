var util = require('util');

function getSources(req, res) {
  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  var sourceID = req.swagger.params.sourceId.value || null
  var sourceVersion = req.swagger.params.version.value || null
  var sourceScenario = req.swagger.params.scenario.value || null


  var db = global.createConnection()
  var query = "SELECT * FROM sources \
    WHERE 1=1\
      AND (${sourceID} IS NULL OR sourceid = ${sourceID}) \
      AND (${sourceVersion} IS NULL OR productversion = ${sourceVersion}) \
      AND (${sourceScenario} IS NULL OR scenario = ${sourceScenario}) \
      ;\
    "

  var queryVals = {'sourceID': sourceID, 'sourceVersion': sourceVersion, 'sourceScenario':sourceScenario}
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
  getSources: getSources
};
