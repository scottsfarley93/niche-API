//This is png.js
//extract a user-defined geometry based subset of a raster
//save the subset as a png image
//Return the user a link to the newly created raster.

//v2.0

function getPNG(req, res) {
  // GET a list of all sources in the database

  //get query values
  var variableID = req.swagger.params.variableID.value || null
  var sourceID = req.swagger.params.sourceID.value || null
  var yearBP = req.swagger.params.yearsBP.value || null
  var geometry = req.swagger.params.geometry.value || null

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
          rasterQuery = "COPY \
          (SELECT \
            encode(\
              ST_AsPNG\
              (ST_ColorMap(\
                (SELECT rast FROM $1:value), 1, \
            \
            '100% 1,70,54\
            90% 1,70,54\
            80% 1,108,89\
            70% 2,129,138\
            60% 54,144,192\
            50% 103,169,207\
            40% 166,189,219\
            30% 208,209,230\
            20% 236,226,240\
            10% 255,247,251\
            0% 255,247,251\
            nodata 0,0,0'), $2:value), 'hex')) \
            TO 'test.hex';\
            "

          //facilitates linear interpolation in the query
              yearabove = closestAbove(yearBP, global.years) //closest year above the yearBP value
              yearbelow = closestBelow(yearBP, global.years) //closest year below the yearBP value
              bandabove = global.bands[global.years.indexOf(yearabove)] //corresponding band number for yearAbove
              bandbelow = global.bands[global.years.indexOf(yearbelow)] //coresponding band number for yearBelow
              console.log(rasterQuery)
          //execute query for values
          db.any(rasterQuery, [tableName, bandbelow])
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
  getPNG: getPNG
};
