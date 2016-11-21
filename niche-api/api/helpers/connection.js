//read the configuration file with the connection details
var conf = JSON.parse(fs.readFileSync('conf.js', 'utf8'))

function createConnection(){
  //CREATE THE CONNECTION TO THE DATABASE
  var cn = {
      host: conf.db.host,
      port: conf.db.port,
      database: conf.db.db,
      user: conf.db.username,
      password: conf.db.password
  };

  var db = pgp(cn); //do the connection using pg-promise library
  return db
}

module.exports = createConnection()
