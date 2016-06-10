# Niche API API documentation version v1
http://api.niche.geography.wisc.edu

---

## /variables

### /variables

* **get**: Get a list of variables in the database
* **post**: Get a list of variables in the database

### /variables/{variableid}

* **get**: Get details on a specific variable
* **put**: Update details of a specific variable with new information
* **delete**: Delete a variable from the database

### /variables/variableTypes

* **get**: List all variable types in the database
* **post**: Add a new variable type to the database

### /variables/variableTypes/{variableTypeID}

* **get**: Get details about a specific variable type in the database
* **put**: Update a variable type defintion with new information
* **delete**: Delete a variable type from the database

### /variables/variableTypes/variableUnits

* **get**: Get a list of variable units in the database
* **post**: Add a new variable unit to the database

### /variables/variableTypes/variableUnits/{unitID}

* **get**: Get details about a specific variable unit
* **put**: Updated a variable unit with new information
* **delete**: Delete a variable unit from the database

### /variables/variablePeriodTypes

* **get**: Get a list of variable period types in the database
* **post**: Add a new variable period to the database

### /variables/variablePeriodTypes/{variablePeriodID}

* **get**: Get details about a specific variable period
* **put**: Updated a variable period with new information
* **delete**: Delete a variable period from the database

### /variables/averagingTypes

* **get**: Get a list of variable averaging types in the database
* **post**: Add a new averaging period to the database

### /variables/averagingTypes/{averagingPeriodID}

* **get**: Get details about a specific averaging period
* **put**: Update a variable period with new information
* **delete**: Delete an averaging period from the database

## /sources

### /sources

* **get**: Get a list of the models and data sources in the database
* **post**: Add a new source or model data source to the database
* **put**: Update specific source with new information
* **delete**: Delete a source from the database

### /sources/{sourceid}

* **get**: List details about a specific source

