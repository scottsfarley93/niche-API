'use strict';

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

app.use(cors())
app.use(bodyParser({limit: '50mb'}));
app.use(compression())

//set up logging
function logCall (req, res, next) {
   console.log("-------" + new Date().toJSON() + "------")
   console.log(req.method)
   console.log(req.path)

   next()
}

app.use(logCall)

//read the configuration file with the connection details
global.conf = JSON.parse(fs.readFileSync('conf.js', 'utf8'))

global.createConnection =function(){
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
var query2 = "SELECT * from bandindex;"
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

  var port = process.env.PORT || 10010;
  app.listen(port);
});
