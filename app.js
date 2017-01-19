//This is app.js
//This is the main server controller for the niche api
//uses express to route http requests
//uses swagger to validate request/response syntax

//v2.0

'use strict';


//load required modules
var SwaggerExpress = require('swagger-express-mw');
var app = require('express')();
var pg = require("pg")
var fs = require("fs")
var bodyParser = require('body-parser');
var compression = require('compression')
var cors = require('cors')
var promise = require('bluebird'); //promise library for pgp to run on
var pgp = require('pg-promise')( //postgres promise library makes it easier to execute user queries
  {promiseLib: promise}
);
var nodalytics = require('nodalytics');


app.use(cors()) //allowa allow cross-server responses
app.use(bodyParser({limit: '50mb'})); //there are going to be some big requests
app.use(compression()) //gzip all responses
app.use(nodalytics("UA-90190802-1"))

//set up logging
function logCall (req, res, next) { //we could go to a db table
   console.log("-------" + new Date().toJSON() + "------")
   console.log(req.method)
   console.log(req.path)
   var db = global.createConnection()
   var sql = "INSERT INTO calllog VALUES(DEFAULT, DEFAULT, ${method}, ${path}, ${params}, ${ip})"
   var vals = {method: req.method, path: req.path, params: req.params, ip: req.ip}
   db.none(sql, vals)
    .then(function(data){
      next()
    })
    .catch(function(err){
      console.log(err)
      next()
    })

}

app.use(logCall) //log every call

//read the configuration file with the connection details
global.conf = JSON.parse(fs.readFileSync('conf.js', 'utf8'))


global.createConnection =function(){
  //connect to the ddatabase specified in the config file
  //has to use VPN to SHC network
  var cn = {
      host: global.conf.host,
      port: global.conf.port,
      database: global.conf.db,
      user: global.conf.username,
      password: global.conf.password
  };
  var db = pgp(cn); //do the connection using pg-promise library
  console.log("Created connection to database.")
  return db
}

//get a list of the bands so we don't have to do it on every call
var db = global.createConnection()
var query2 = "SELECT * from bandindex ORDER BY bandnumber ASC;"
db.any(query2)
.then(function(bandindex){
  global.years = []
  global.bands = []
  for (var band in bandindex){
    global.years.push(bandindex[band]['bandvalue'])
    global.bands.push(bandindex[band]['bandnumber'])
  }
  console.log("Got band info.")
})
.catch(function(err){
  //errors getting band info
  console.log(err)
})

module.exports = app; // for testing

var config = {
  appRoot: __dirname // required config
};


SwaggerExpress.create(config, function(err, swaggerExpress) {
  if (err) { throw err; }

  // install middleware
  swaggerExpress.register(app);

  var port = process.env.PORT || 8080; //run
  app.listen(port);
});
