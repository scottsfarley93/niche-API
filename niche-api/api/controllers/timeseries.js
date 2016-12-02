//This is timeseries.js
//GET a time series of a particular variable/source pair for a single spatial location
//Selects all data values in the database, which are referenced in the bands table

//v2.0

function getTimeseries(req, res) {
  //GET a timeseries for a single variable/source at a single spatial location at all timeslices

  //get query values
  var latitude = req.swagger.params.latitude.value || null
  var longitude = req.swagger.params.longitude.value || null
  var variableID = req.swagger.params.variableID.value || null
  var sourceID = req.swagger.params.sourceID.value || null


  //connect to the database
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

  db.any(query1, query1Vars) //first get the table name
    .then(function(data){
      //this is shitty SQL
      var tablename = data[0]['tableName']
      var query2Vars = [longitude, latitude]
      var query2 = "SELECT "
      //make a space-time geometry for each band
      for (i=0; i< global.bands.length; i++){
        p = global.bands[i]
        r = "year" + global.years[i] //this is bad...
        query2 += " ST_Value(rast, $" + p + ", ST_SetSRID(ST_MakePoint($1, $2), 4326)) as " + r + ", " //this specifies the band number of interest
        query2Vars.push(i) //list of space-time points to query for
      }
      query2 = query2.slice(0, -2) //get rid of trailing comma
      query2 += " FROM " + tablename + " " //this is bad...
      query2 += " WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint($1, $2), 4326));"
      console.log(query2)
      db.any(query2, query2Vars)
        .then(function(rastData){
          // //successfully got data
          //sendit back to the user
          var ts = new Date().toJSON()
          console.log("Success")
          var resOut = {
            "success" : true,
            "timestamp" : ts,
            data: rastData
          }
          res.json(resOut)
        })
        .catch(function(err){
          //error on the geometry/raster point selection
          console.log(err)
          res.json(err)
      }).catch(function(err){
        //errors on the table lookup
        console.log(err)
        res.json(err)
      })
  })




}

module.exports = {
  getTimeseries: getTimeseries
};
