
var util = require('util');

function getTimeseries(req, res) {
  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  var latitude = req.swagger.params.latitude.value || null
  var longitude = req.swagger.params.longitude.value || null
  var variableID = req.swagger.params.variableID.value || null
  var sourceID = req.swagger.params.sourceID.value || null



  var db = global.createConnection()
  //sql to get the name of the table to go to
  var query1 = "SELECT * from rasterindex \
    where 1=1 AND \
    variableid = $(variableID) AND sourceid = $(sourceID)\
    ;"

  var query1Vars = {
    'variableID' : variableID,
    'sourceID' : sourceID
  }
  console.log(sourceID)
  db.any(query1, query1Vars) //first get the table name
    .then(function(data){
      //sql to get the avtual values from the rasters
      console.log(data)
      var tablename = data[0]['tableName']
      var query2Vars = [longitude, latitude]
      var query2 = "SELECT "
      //get all the bands
      for (i=0; i< 23; i++){
        p = i + 3
        r = "band" + i //this is bad...
        query2 += " ST_Value(rast, $" + p + ", ST_SetSRID(ST_MakePoint($1, $2), 4326)) as " + r + ", "
        query2Vars.push(i)
      }
      query2 = query2.slice(0, -2) //get rid of trailing comma
      query2 += " FROM " + tablename + " " //this is bad...
      query2 += " WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint($1, $2), 4326));"
      console.log(query2Vars)
      db.any(query2, query2Vars)
        .then(function(rastData){
          //successfully got data
          //zip it up with the band interpretations to get timeline
          query3 = "SELECT bandnumber, bandvalue from bandindex;"
          db.any(query3)
            .then(function(bandindex){
              //get the json ready to send back
              out = {
                "success" : true,
                "timestamp" : new Date().toJSON(),
                "latitude" : latitude,
                "longitude" : longitude,
                "data" : []
              }
              for (var band=0; band < bandindex.length; band++){
                pt = {}
                bandtime = bandindex[band]['bandvalue']
                bandnumber = bandindex[band]['bandnumber']
                bandkey = "band" + bandnumber
                rastVal = rastData[0][bandkey]
                pt['time'] = bandtime
                pt['value'] = rastVal
                out['data'].push(pt)

              }
              console.log(out)
              res.json(out)
            })
            .catch(function(err){
              console.log(err)
              res.json(err)
            })
        }).catch(function(err){
          console.log(err)
          res.json(err)
        })
    })




}

module.exports = {
  getTimeseries: getTimeseries
};
