//This is map configs.js
//GET Ice Age Mapper configurations

var shortid = require("shortid");

function getMapConfig(req, res) {
  //GET a list of map configurations
  // optionally specify a specific configuration
  //
  //get query parameters
  var configID = req.swagger.params.configID.value || null
  var organization = req.swagger.params.organization.value || null
  var author = req.swagger.params.author.value || null
  var title = req.swagger.params.title.value || null
  var limit = req.swagger.params.limit.value || null
  var summaryOnly = req.swagger.params.summaryOnly.value || false
  //can't search on description

  //create connection to the database
  var db = global.createConnection()

  if (summaryOnly){
    fields = "hash,author,organization,created_at, description, title"
  }else{
    fields = "*"
  }

  //query the variable units table
  var query = "SELECT " + fields + " FROM IAMConfigs \
    WHERE 1=1\
      AND (${configID} IS NULL OR hash = ${configID})\
      AND ($(author) IS NULL OR author LIKE $(author)) \
      AND ($(organization) IS NULL OR organization LIKE $(organization))\
      AND (${title} IS NULL OR title LIKE ${title})\
      ORDER BY created_at DESC LIMIT ${limit};\
    "

  var queryVals = {'configID': configID, 'author': author, 'organization':organization, 'title': title, 'limit':limit}
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
  var author = req.swagger.params.author.value || null
  var organization = req.swagger.params.organization.value || null
  var description = req.swagger.params.description.value || null
  var title = req.swagger.params.title.value || null

  var hash = shortid.generate()

  //create connection to the database
  var db = global.createConnection()

  //do the insert
  sql = "INSERT INTO IAMConfigs VALUES(DEFAULT, ${hash}, ${config}, ${author}, ${organization}, DEFAULT, ${description}, ${title});"
  queryVals = {'hash': hash, 'config': body, 'author':author, 'organization':organization, 'description': description, 'title': title}

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
