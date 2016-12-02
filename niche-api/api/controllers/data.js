//This is data.js
//Enables data GET and POST requests for space-time locations on raster grids
//v2.0

//load libraries
var util = require('util');
var uuid = require('node-uuid'); //generate uuids for callids
var promise = require('bluebird'); //promise library for pgp to run on
var pgp = require('pg-promise')( //postgres promise library makes it easier to execute user queries
  {promiseLib: promise}
);

function getDataPoint(req, res) {
  //GET data for a single space-time location with given variable and source ids.

  // Get query parameters
  var latitude = req.swagger.params.latitude.value || null
  var longitude = req.swagger.params.longitude.value || null
  var variableID = req.swagger.params.variableID.value || null
  var sourceID = req.swagger.params.sourceID.value || null
  var yearBP = req.swagger.params.yearsBP.value || null

  // connect to database
  var db = global.createConnection()

  //ask the database which raster table we should query
  var query1 = "SELECT * from rasterindex \
    where 1=1 AND \
    variableid = $(variableID) AND sourceid = $(sourceID);"

  //execute query for table
  db.oneOrNone(query1, {"variableID": variableID, "sourceID":sourceID})
      .then(function(tabledata){
        //successful execution of first query
          tableName = tabledata['tableName']
          // query the database for interpolated values at the specific space-time location
          //use linear interpolation between two nearest time slices
          rasterQuery = "\
          SELECT(\
            belowVal + ((aboveVal - belowVal)/ NULLIF((yearAbove - yearBelow), 0))*(yr - yearBelow)) as value,\
                yearBP\
               FROM (\
		      SELECT\
			ST_Value(rast, $5, pt) as belowVal,\
			ST_Value(rast, $6, pt) as aboveVal,\
			$7 as yearAbove, $8 as yearBelow,\
			$4 as yearBP\
		      FROM\
			$1:value, (SELECT ST_SetSRID(ST_MakePoint($2, $3), 4326) as pt) as makePoint \
		      WHERE \
		      ST_Intersects(rast, pt)\
		  ) as vals;"

          //facilitates linear interpolation in the query
              yearabove = closestAbove(yearBP, global.years) //closest year above the yearBP value
              yearbelow = closestBelow(yearBP, global.years) //closest year below the yearBP value
              bandabove = global.bands[global.years.indexOf(yearabove)] //corresponding band number for yearAbove
              bandbelow = global.bands[global.years.indexOf(yearbelow)] //coresponding band number for yearBelow
          //execute query for values
          db.any(rasterQuery, [tableName, longitude, latitude, yearBP, bandbelow, bandabove, yearabove, yearbelow])
            .then(function(data){
              //return generic response to user
              var ts = new Date().toJSON()
              console.log("Success")
              var resOut = {
                success : true,
                timestamp : ts,
                data: data
              }
              res.json(resOut)
            })
            .catch(function(err){
              //errors caused by raster lookup
              res.json(err)
              console.log(err)
            })
      }).catch(function(err){
        //errors caused by index table lookup
        console.log(err)
        res.json(err)
      })
}

postData = function(req, res){
  //get values for an array of space-time locations via a POST request

  //get query data --> everything is in the body of the request on a POST request
  var body = req.swagger.params.data
  var bodyContent = body.value
  var variableID = bodyContent.variableID
  var sourceID = bodyContent.sourceID

  //connect to DB
  var db = global.createConnection()

  //insert the values into the data table
  callid = uuid.v1(); //unique id for this call
  insertPoints = []
  for (var i =0; i < bodyContent.points.length; i++){
    //process each point in the request
    pt = bodyContent.points[i]
    //find closest data
    pt['yearabove'] = closestAbove(pt['year'], global.years)
    pt['yearbelow'] = closestBelow(pt['year'], global.years)
    pt['bandabove'] = global.bands[global.years.indexOf(pt['yearabove'])]
    pt['bandbelow'] = global.bands[global.years.indexOf(pt['yearbelow'])]
    pt['geom'] = 'ST_SetSRID(ST_MakePoint(' + pt['longitude'] + ',' + pt['latitude'] +'), 4326)' //make a geometry out of lat/lng
    pt['callid'] = callid
    pt['ptrequestid'] = 'default'
    pt['yr'] = pt['year']
    pt['id'] = pt['id']
    if (pt['id'] == undefined){
      pt['id'] = null
    }
    insertPoints.push(pt)
  }
  // Define query structure
  var cs = new pgp.helpers.ColumnSet(['ptrequestid', 'yr',
        'bandabove', 'bandbelow', 'yearabove',
        'yearbelow', 'geom', 'callid', 'id'], {table: 'pointrequests'});
  //
  // insert all of the points into the request into the point request table
  var query = pgp.helpers.insert(insertPoints, cs);

  //make sure the quotes are the right direction
  // this is bad -- probably an easier way
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
              // select points from the point request table, then select the raster values at those space-time locations
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
                    //return generic response to user
                    var ts = new Date().toJSON()
                    console.log("Success")
                    var resOut = {
                      success : true,
                      timestamp : ts,
                      data: data
                    }
                    res.json(resOut)
                    //get rid of the point requests, so the table doesn't get super big super fast
                    deleteQuery = "DELETE FROM pointrequests WHERE callid=$1;"
                    db.none(deleteQuery, [callid])
                      .then(function(data){
                        //no return, successful delete.
                        console.log("Points associated with callid " + callid + " were deleted.")
                      })
                      .catch(function(err){
                        //error in deleting points
                        console.log(err)
                      })
                  })
                  .catch(function(err){
                    //error in raster lookup.
                    res.json(err)
                    console.log(err)
                  })
            }).catch(function(err){
              //error in table lookup
              console.log(err)
              res.json(err)
            })
      })
      .catch(function(err){
        //error in point insert
        res.json(err)
        console.log(err)
      })
}


//utility functions

function closestBelow(number, arr){
  //find the closest existing number in an array that is less than a given number
    var closest = 0
    for(var i = 0; i < arr.length; i++){
        if(arr[i] <= number && arr[i] >= closest) closest = arr[i];
    }
    return closest; // return the value
}

function closestAbove(number, arr){
  //find the closest number in an array that is more than a given number
    var closest = Math.max.apply(null, arr);
    for(var i = 0; i < arr.length; i++){
        if(arr[i] >= number && arr[i] <= closest) closest = arr[i];
    }
    return closest; // return the value
}


String.prototype.replaceAll = function(search, replacement) {
  //replace all occurrences in string
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};


module.exports = {
  getDataPoint: getDataPoint,
  postData: postData
};
