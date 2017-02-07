//This is map configs.js
//GET Ice Age Mapper configurations

var shortid = require("shortid");

function getMapConfig(req, res) {
  //GET a list of map configurations
  // optionally specify a specific configuration
  //
  //get query parameters
  var configID = req.swagger.params.configID.value || null

  //create connection to the database
  var db = global.createConnection()

  //query the variable units table
  var query = "SELECT * FROM IAMConfigs \
    WHERE 1=1\
      AND (${configID} IS NULL OR hash = ${configID});\
    "

  var queryVals = {'configID': configID}
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




///////////////////////////////////////////////////////////////////////////////



postMapConfig = function(req, res){
  //add a new configuration to the database
  //returns the shortid hash for the unique configuration

  //get query data --> everything is in the body of the request on a POST request
  var body = req.swagger.params.configData.value

  var hash = shortid.generate()

  //create connection to the database
  var db = global.createConnection()

  //do the insert
  sql = "INSERT INTO IAMConfigs VALUES(DEFAULT, ${hash}, ${config});"
  queryVals = {hash: hash, config: body}

  db.any(sql, queryVals)
    .then(function(data){
      //return data to the user
      var ts = new Date().toJSON()
      var resOut = {
        "success" : true,
        "timestamp" : ts,
        data: data,
        configHash: hash
      }
      res.json(resOut)
    })
    .catch(function(error){
      //return data to the user
      var ts = new Date().toJSON()
      var resOut = {
        "success" : false,
        "timestamp" : ts,
        data: [],
        error: error
      }
      res.json(resOut)
    })

}

module.exports = {
  getMapConfig: getMapConfig,
  postMapConfig: postMapConfig
};
