
var util = require('util');
var linear = require('everpolate').linear

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

  //sql to get the name of the table to go to
  var query1 = "SELECT * from rasterindex \
    where 1=1 AND \
    variableid = $(variableID) AND sourceid = $(sourceID);"
  //query for the table
  db.oneOrNone(query1, {"variableID": variableID, "sourceID":sourceID})
      .then(function(tabledata){
        tableName = tabledata['tableName']
        //find the band listing
        query2 = "SELECT * from bandindex;"
        db.any(query2)
            .then(function(bandindex){

              //process the band info
              years = []
              bands = []
              for (i =0; i< bandindex.length; i++){
                years.push(+bandindex[i]['bandvalue'])
                bands.push(+bandindex[i]['bandnumber'])
              }
          //get the value for every point in the Request
          //first assemble all of the requests

          rasterQuery = "SELECT(\
              	belowVal + ((aboveVal - belowVal)/ (yearAbove - yearBelow))*(yr - yearBelow)) as interp  FROM (\
              SELECT\
              	ST_Value(rast, bandBelow, pt) as belowVal,\
              	ST_Value(rast, bandAbove, pt) as aboveVal,\
              	yearBelow, yearAbove,\
              	yr\
              FROM\
              data_28e09e9cb03211e694989cf387ae7186,\
              	(select p.geom as pt, \
              	p.yearBelow as yearBelow, \
              	p.yearAbove as yearAbove, \
              	p.bandBelow as bandBelow, \
              	p.bandAbove as bandAbove,\
              	p.yr as yr \
              	from pointrequests as p) as makePoint\
              WHERE ST_Intersects(rast, pt)) as vals;"

          // db.tx(function(t){
          //   requests = []
          //
          //   for (ptIdx in bodyContent.points){
          //     year = bodyContent.points[i].year
          //     cBelow = closestBelow(year, years)
          //     bBelow = bands[years.indexOf(cBelow)]
          //     cAbove = closestAbove(year, years)
          //     bAbove = bands[years.indexOf(cAbove)]
          //     pt = bodyContent.points[ptIdx]
          //     param = [pt.longitude, pt.latitude, bBelow, bAbove, cBelow, cAbove , year, tableName]
          //     request = t.oneOrNone(rasterQuery, param)
          //     requests.push(request)
          //   }
          //   //use a transaction to do a batch
          //   return t.batch(requests)
          // }).then(function(rasterdata){
          //   res.json(rasterdata)
          //   // outPoints = []
          //   // for (i in rasterdata){
          //   //   try{
          //   //     pt = {}
          //   //     year = bodyContent.points[i].year
          //   //     valAbove = rasterdata[i]['aboveval']
          //   //     valBelow = rasterdata[i]['belowval']
          //   //     closestYearAbove = Math.round(year/1000)*1000
          //   //     closestYearBelow = closestYearAbove - 1000
          //   //     interpValue = linear(year, [closestYearBelow, closestYearAbove], [valBelow, valAbove ])[0]
          //   //     pt['latitude'] = bodyContent.points[i].latitude
          //   //     pt['longitude'] = bodyContent.points[i].longitude
          //   //     pt['value'] = interpValue
          //   //     pt['year'] = year
          //   //     outPoints.push(pt)
          //   //   }catch(err){
          //   //     outPoints.push({ 'latitude' : bodyContent.points[i].latitude,
          //   //                     'longitude': bodyContent.points[i].longitude,
          //   //                     'value' : -9999,
          //   //                     'year':  year})
          //   //   }
          //   //
          //   // }
          //   // out = {
          //   //   "success": true,
          //   //   "timestamp" : new Date().toJSON(),
          //   //   "variableID" : variableID,
          //   //   "sourceID" : sourceID,
          //   //   "data" : outPoints
          //   // }
          //   // res.json(out)
          }).catch(function(err){
            console.log(err)
            res.json(err)
          })
        }).catch(function(err){
          console.log(err)
          res.json(err)
        })
      }).catch(function(err){
        console.log(err)
        res.json(err)
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


module.exports = {
  getDataPoint: getDataPoint,
  postData: postData
};
