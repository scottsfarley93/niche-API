//This is sources.js
//GET a list of the sources in the Database
//A source is the the model and forcing that produced the dataset
//For example, CCSM3 climate model under the RCP8.5 scenario

//v2.0

function getSources(req, res) {
  // GET a list of all sources in the database

  //get query values
  var sourceID = req.swagger.params.sourceId.value || null
  var sourceVersion = req.swagger.params.version.value || null
  var sourceScenario = req.swagger.params.scenario.value || null

  //create connection to database
  var db = global.createConnection()

  //query the sources table
  var query = "SELECT * FROM sources \
    WHERE 1=1\
      AND (${sourceID} IS NULL OR sourceid = ${sourceID}) \
      AND (${sourceVersion} IS NULL OR productversion = ${sourceVersion}) \
      AND (${sourceScenario} IS NULL OR scenario = ${sourceScenario}) \
      ;\
    "

  var queryVals = {'sourceID': sourceID, 'sourceVersion': sourceVersion, 'sourceScenario':sourceScenario}

  //execute SQL query
  db.any(query, queryVals)
    .then(function(data){
      //successful execution--send data back to the user
      var ts = new Date().toJSON()
      console.log("Success")
      var resOut = {
        "success" : true,
	"message": "it worked!",
        "timestamp" : ts,
        data: data
      }
      res.json(resOut)
    }).catch(function(err){
      //errors on the sql call 
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
