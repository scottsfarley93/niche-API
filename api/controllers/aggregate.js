//This is aggregate.js
//Enables data GET requests to aggregate (average) data over a user-specified geometry.
//v2.0

//load libraries
var util = require('util');
var uuid = require('node-uuid'); //generate uuids for callids
var promise = require('bluebird'); //promise library for pgp to run on
var pgp = require('pg-promise')( //postgres promise library makes it easier to execute user queries
  {promiseLib: promise}
);

function getAverage(req, res) {
  //GET data for a user specified geometry with given variable and source ids at a single point in time.

  // Get query parametersl
  var variableID = req.swagger.params.variableID.value || null
  var sourceID = req.swagger.params.sourceID.value || null
  var yearBP = req.swagger.params.yearsBP.value || null
  var userGeom = req.swagger.params.geometry.value || null

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

          var queryGeom = "SRID=4326;" + userGeom //set the coordinate system
          rasterQuery = " WITH g AS\
          (SELECT $3::geometry AS geom),\
        cells AS\
          (SELECT ST_Centroid((ST_Intersection(dat.rast, g.geom)).geom) AS geom,\
          (ST_Intersection(dat.rast, $2, g.geom)).val AS val\
           FROM $1:value as dat, g\
           WHERE ST_Intersects(dat.rast, g.geom)\
         )\
      	SELECT avg(val), count(val) \
      	     FROM cells, g\
      	     GROUP BY g.geom"

          //facilitates linear interpolation in the query
              yearabove = closestAbove(yearBP, global.years) //closest year above the yearBP value
              yearbelow = closestBelow(yearBP, global.years) //closest year below the yearBP value
              bandabove = global.bands[global.years.indexOf(yearabove)] //corresponding band number for yearAbove
              bandbelow = global.bands[global.years.indexOf(yearbelow)] //coresponding band number for yearBelow
          //execute query for values
          db.any(rasterQuery, [tableName, bandbelow, queryGeom])
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
  getAverage: getAverage
};
