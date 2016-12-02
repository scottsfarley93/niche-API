
var util = require('util');
var uuid = require('node-uuid');
var promise = require('bluebird'); //promise library for pgp to run on
var pgp = require('pg-promise')( //postgres promise library makes it easier to execute user queries
  {promiseLib: promise}
);

function getDataPoint(req, res) {
  // variables defined in the Swagger document can be referenced using req.swagger.params.{parameter_name}
  var latitude = req.swagger.params.latitude.value || null
  var longitude = req.swagger.params.longitude.value || null
  var variableID = req.swagger.params.variableID.value || null
  var sourceID = req.swagger.params.sourceID.value || null
  var yearBP = req.swagger.params.yearsBP.value || null

  var db = global.createConnection()

  //sql to get the name of the table to go to
  var query1 = "SELECT * from rasterindex \
    where 1=1 AND \
    variableid = $(variableID) AND sourceid = $(sourceID)\
    ;"

  db.one(query1, {"variableID": variableID, "sourceID":sourceID})
    .then(function(tabledata){
      tableName = tabledata['tableName']
      //find the closest band
      query2 = "SELECT * from bandindex;"
      db.any(query2)
        .then(function(bandindex){
          years = []
          bands = []
          for (band in bandindex){
            years.push(bandindex[band]['bandvalue'])
            bands.push(bandindex[band]['bandnumber'])
          }
          //find the closest years and assocaited band index
          closestYearAbove = closestAbove(yearBP, years)
          closestYearBelow = closestBelow(yearBP, years)
          closestBandAbove = bands[years.indexOf(closestYearAbove)]
          closestBandBelow = bands[years.indexOf(closestYearBelow)]

          //define sql query
          closestQuery = "SELECT \
            ST_Value(rast, $3, ST_SetSRID(ST_MakePoint($1, $2), 4326)) as belowVal, \
            ST_Value(rast, $4, ST_SetSRID(ST_MakePoint($1, $2), 4326)) as aboveVal\
            FROM "
          closestQuery += tableName
          closestQuery += " WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint($1, $2), 4326));"

          closestQueryVals = [longitude, latitude, closestBandBelow, closestBandAbove]
          db.any(closestQuery, closestQueryVals)
            .then(function(rasterdata){
              //do linear interpolation
              valAbove = rasterdata[0]['aboveval']
              valBelow = rasterdata[0]['belowval']
              interpValue = linear(yearBP, [closestYearBelow, closestYearAbove], [valBelow, valAbove ])[0]
              if (isNaN(interpValue)){
                interpValue = valAbove
              }
              pt = {
                "value": interpValue,
                "year" : yearBP,
                "latitude": latitude,
                "longitude" : longitude
              }
              out = {
                "success": true,
                "timestamp" : new Date().toJSON(),
                "variableID" : variableID,
                "sourceID" : sourceID,
                "data": [pt]
              }
              res.json(out)
            }).catch(function(err){
              res.json(err)
            })
        })
        .catch(function(err){
          res.json(err)
        })
    }).catch(function(err){
      res.json(err)
    })
}

postData = function(req, res){
  //get an array of space-time locations via a POST request
  console.log("Got to posting data.")
  var body = req.swagger.params.data
  var bodyContent = body.value
  var variableID = bodyContent.variableID
  var sourceID = bodyContent.sourceID
  var db = global.createConnection()

  //insert the values into the data table
  callid = uuid.v1();
  insertPoints = []
  for (var i =0; i < bodyContent.points.length; i++){
    pt = bodyContent.points[i]
    pt['yearabove'] = closestAbove(pt['year'], global.years)
    pt['yearbelow'] = closestBelow(pt['year'], global.years)
    pt['bandabove'] = global.bands[global.years.indexOf(pt['yearabove'])]
    pt['bandbelow'] = global.bands[global.years.indexOf(pt['yearbelow'])]
    pt['geom'] = 'ST_SetSRID(ST_MakePoint(' + pt['longitude'] + ',' + pt['latitude'] +'), 4326)'
    pt['callid'] = callid
    pt['ptrequestid'] = 'default'
    pt['yr'] = pt['year']
    pt['id'] = pt['id']
    if (pt['id'] == undefined){
      pt['id'] = null
    }
    insertPoints.push(pt)
  }
  // performance-optimized, reusable set of columns:
  var cs = new pgp.helpers.ColumnSet(['ptrequestid', 'yr',
        'bandabove', 'bandbelow', 'yearabove',
        'yearbelow', 'geom', 'callid', 'id'], {table: 'pointrequests'});
  //
  // // generating a multi-row insert query:
  var query = pgp.helpers.insert(insertPoints, cs);
  // // // executing the query:
  query = query.replaceAll("'", "")
  query = query.replaceAll(callid, "'" + callid + "'")
  db.none(query)
      .then(function(data){
        //sql to get the name of the table to go to
        var query1 = "SELECT * from rasterindex \
          where 1=1 AND \
          variableid = $(variableID) AND sourceid = $(sourceID);"
        //query for the table
        db.oneOrNone(query1, {"variableID": variableID, "sourceID":sourceID})
            .then(function(tabledata){
                //get the value for every point in the Request
                //first assemble all of the requests
                tableName = tabledata['tableName']
                rasterQuery = "SELECT(\
                    	belowVal + ((aboveVal - belowVal)/ NULLIF((yearAbove - yearBelow), 0))*(yr - yearBelow)) as value,\
                      yr, id \
                        FROM (\
                    SELECT\
                    	ST_Value(rast, bandBelow, pt) as belowVal,\
                    	ST_Value(rast, bandAbove, pt) as aboveVal,\
                    	yearBelow, yearAbove,\
                    	yr, \
                      id \
                    FROM\
                    $1:value,\
                    	(select p.geom as pt, \
                    	p.yearBelow as yearBelow, \
                    	p.yearAbove as yearAbove, \
                    	p.bandBelow as bandBelow, \
                    	p.bandAbove as bandAbove,\
                    	p.yr as yr, \
                      p.id as id \
                    	from pointrequests as p WHERE callID = $2) as makePoint\
                    WHERE ST_Intersects(rast, pt)) as vals;"
                db.any(rasterQuery, [tableName, callid])
                  .then(function(data){
                    res.json(data)
                    deleteQuery = "DELETE FROM pointrequests WHERE callid=$1;"
                    db.none(deleteQuery, [callid])
                      .then(function(data){
                        console.log("Done.")
                      })
                      .catch(function(err){
                        console.log(err)
                      })
                  })
                  .catch(function(err){
                    res.json(err)
                    console.log(err)
                  })
            }).catch(function(err){
              console.log(err)
              res.json(err)
            })
      })
      .catch(function(err){
        console.log(err)
      })
}


function closestBelow(closestTo, arr){
    var closest = 0 //Get the highest number in arr in case it match nothing.
    for(var i = 0; i < arr.length; i++){ //Loop the array
        if(arr[i] <= closestTo && arr[i] >= closest) closest = arr[i]; //Check if it's higher than your number, but lower than your closest value
    }
    return closest; // return the value
}

function closestAbove(closestTo, arr){
    var closest = Math.max.apply(null, arr); //Get the highest number in arr in case it match nothing.
    for(var i = 0; i < arr.length; i++){ //Loop the array
        if(arr[i] >= closestTo && arr[i] <= closest) closest = arr[i]; //Check if it's higher than your number, but lower than your closest value
    }
    return closest; // return the value
}

String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};


module.exports = {
  getDataPoint: getDataPoint,
  postData: postData
};
