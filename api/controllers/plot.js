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


getPlotData = function(req, res){
  //get values for an array of space-time locations via a POST request

  //get query data --> everything is in the body of the request on a POST request
  var body = req.swagger.params.data
  var bodyContent = body.value
  var variableID1 = req.swagger.params.variableID1.value || null
  var sourceID1 = req.swagger.params.sourceID1.value || null
  var variableID2 = req.swagger.params.variableID2.value || null
  var sourceID2 = req.swagger.params.sourceID2.value || null

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
        var tablequery = "SELECT * from rasterindex \
          where 1=1 AND \
          variableid = $(variableID) AND sourceid = $(sourceID);"

        db.tx(function (t) {
          // `t` and `this` here are the same;
          // this.ctx = transaction config + state context;
          return t.batch([
              t.one(tablequery, {variableID: variableID1, sourceID: sourceID1}),
              t.one(tablequery, {variableID: variableID2, sourceID: sourceID2})
          ]);
      })
      .then(function (data) {
        console.log(data)
        table1 = data[0]['tableName']
        table2 = data[1]['tableName']
        console.log(table1)
        console.log(table2)

        rasterquery =  "  SELECT(\
              CASE \
            WHEN (yearAbove - yearBelow) = 0 THEN belowVal \
            ELSE belowVal + ((aboveVal - belowVal)/ NULLIF((yearAbove - yearBelow), 0))*(yearBP - yearBelow) \
                END ) as value,\
              yearBP, id \
                FROM (\
            SELECT\
              ST_Value(rast, bandBelow, pt) as belowVal,\
              ST_Value(rast, bandAbove, pt) as aboveVal,\
              yearBelow, yearAbove,\
              yearBP, \
              id \
            FROM\
            $1:value,\
              (select p.geom as pt, \
              p.yearBelow as yearBelow, \
              p.yearAbove as yearAbove, \
              p.bandBelow as bandBelow, \
              p.bandAbove as bandAbove,\
              p.yr as yearBP, \
              p.id as id \
              from pointrequests as p WHERE callID = $2) as makePoint\
            WHERE ST_Intersects(rast, pt)) as vals;"
          db.tx(function (t) {
            // `t` and `this` here are the same;
            // this.ctx = transaction config + state context;
            return t.batch([
                t.any(rasterquery, [table1, callid]),
                t.any(rasterquery, [table2, callid])
            ]);
          }).then(function(data){
            var ts = new Date().toJSON()
            console.log("Success")
            var resOut = {
              success : true,
              timestamp : ts,
            }
            pts = []
            for (i = 0; i < data[1].length; i++){
              x = data[0][i]['value']
              y = data[1][i]['value']
              t = data[0][i]['yearbp']
              pts.push({
                x : x,
                y : y,
                t: t
              })
            }
            resOut['data'] = pts
            res.json(resOut)
          })
          .catch(function(error){
              console.log("ERROR:", error.message || error);
          })
        })
        .catch(function (error) {
            console.log("ERROR:", error.message || error);
        });

      }).catch(function(err){
        //error in table lookup
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
  getPlotData: getPlotData,
};
