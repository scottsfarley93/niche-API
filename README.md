# Niche API
### Scott Farley
### UW Madison

Creates a web-based data service that serves global climate model data at a specific point in space and time for a given set of climate variables.  

Gridded climate model output is great if you want to examine the spatial patterns of climate in a single time slice, but is difficult to use if you want to track the trajectory of a specific point in space (x, y) in climate space through time. I know of no way to programmatically and efficiently get the value of climatic variables (maximum temperature, minimum temperature, precipitation, etc) at a single grid cell at a time slice using standard web-based repositories.  My goal is to create a data service that allows a client to query a space-time point (e.g., 37N, -122W, 1250 years ago) for a specific climate layer and return the information in a consumable format (json).  I’d like whatever I build to be web-based, and have the heavy lifting done on the server side, so that the user doesn’t need to download the whole data file (e.g., netcdf) which would be a lot of data transfer and probably contain a lot of unnecessary information.  I’d also like to build out a REST interface so that the querying can be efficiently done by any client. The service would serve downscaled CCSM3 climate model output for North America between 22,000 years ago and the present, as well as, potentially, other climate models and/or other gridded datasets (soils, land use) though both of these seem like they’d be much more complicated.  

### Technical Configuration
***Database:*** Run a Postgres database with PostGIS spatial extensions. Store each time slice (e.g, 22000 years ago, 21900 years ago, 21800 years ago…) for each variable (e.g., January precipitation, January maximum temperature,…) as a separate postgres raster table table.  Store a pointer to that table in a central index table that keeps track of the layer’s metdata. When a client issues a query, search the index table to find the row(s) that meet the user’s query.  Go to the raster tables that are referred by each of these rows and do a point-in-raster value extraction. Send back the values at those points in those tables.

***Server/Service:*** Run a Node.js server interface. Using the Express.js and Postgres (pg) bindings for node, parse client requests and send them to the database.  When the database responds, package up the json and send the response back to the client.

### Libraries:
 - ```PostGIS```: Management of raster spatial data, handles geometry conversion on incoming calls
 - ```Swagger (swagger-express-mw)```: Ensures proper API returns by validating against a schema. Documents the API.
 - ```pg-promise```: Simplified connection to postgres database.
 - ```express```: Web framework for Node.js
 - ```uuid```: Node library for generating universally unique identifiers.  Used to assign IDs to client requests.
 - ```cors```: Allow cross-origin requests from this server.
 - ```compression```: Return all responses from the application as ```gzip``` compressed files.

### Projects Using the Niche API:
- [Ice Age Mapper](http://paleo.geography.wisc.edu)

### Example Calls
e
