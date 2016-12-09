# SwaggerClient::DefaultApi

All URIs are relative to *http://grad.geography.wisc.edu:8080/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_averaging_period_types**](DefaultApi.md#get_averaging_period_types) | **GET** /averagingPeriodTypes | 
[**get_data_point**](DefaultApi.md#get_data_point) | **GET** /data | 
[**get_sources**](DefaultApi.md#get_sources) | **GET** /sources | 
[**get_timeseries**](DefaultApi.md#get_timeseries) | **GET** /timeseries | 
[**get_variable_period_types**](DefaultApi.md#get_variable_period_types) | **GET** /variablePeriodTypes | 
[**get_variable_types**](DefaultApi.md#get_variable_types) | **GET** /variableTypes | 
[**get_variable_units**](DefaultApi.md#get_variable_units) | **GET** /variableUnits | 
[**get_variables**](DefaultApi.md#get_variables) | **GET** /variables | 
[**post_data**](DefaultApi.md#post_data) | **POST** /data | 


# **get_averaging_period_types**
> GenericResponse get_averaging_period_types(opts)



Get a list of the time periods over which a variable could be averaged.  Averaging period types are the amount of time over which data is averaged.  For example, decadally averaged climate annual precipitation would represent a ten year average, and have an averaging period type of decades.

### Example
```ruby
# load the gem
require 'swagger_client'

api_instance = SwaggerClient::DefaultApi.new

opts = { 
  averaging_period_type_id: 3.4 # Float | Database ID of the averaging period type.
}

begin
  result = api_instance.get_averaging_period_types(opts)
  p result
rescue SwaggerClient::ApiError => e
  puts "Exception when calling DefaultApi->get_averaging_period_types: #{e}"
end
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **averaging_period_type_id** | [**Float**](.md)| Database ID of the averaging period type. | [optional] 

### Return type

[**GenericResponse**](GenericResponse.md)

### Authorization

No authorization required

### HTTP reuqest headers

 - **Content-Type**: application/json
 - **Accept**: application/json



# **get_data_point**
> DataResponse get_data_point(latitude, longitude, variable_id, source_id, years_bp)



Get data for a single space-time point for a given source and variable combination.

### Example
```ruby
# load the gem
require 'swagger_client'

api_instance = SwaggerClient::DefaultApi.new

latitude = 3.4 # Float | Latitude of point of interest.

longitude = 3.4 # Float | Longitude of point of interest.

variable_id = 3.4 # Float | Database ID of variable of interest

source_id = 3.4 # Float | Database ID of source of interest.

years_bp = 3.4 # Float | years before present of point of interest. AD1950 is considered zero in this context.


begin
  result = api_instance.get_data_point(latitude, longitude, variable_id, source_id, years_bp)
  p result
rescue SwaggerClient::ApiError => e
  puts "Exception when calling DefaultApi->get_data_point: #{e}"
end
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **latitude** | [**Float**](.md)| Latitude of point of interest. | 
 **longitude** | [**Float**](.md)| Longitude of point of interest. | 
 **variable_id** | [**Float**](.md)| Database ID of variable of interest | 
 **source_id** | [**Float**](.md)| Database ID of source of interest. | 
 **years_bp** | [**Float**](.md)| years before present of point of interest. AD1950 is considered zero in this context. | 

### Return type

[**DataResponse**](DataResponse.md)

### Authorization

No authorization required

### HTTP reuqest headers

 - **Content-Type**: application/json
 - **Accept**: application/json



# **get_sources**
> GenericResponse get_sources(opts)



Get a list of data sources in the database. A source is the data producer from which the raster data originated.  Each source contains information on the producer of the product, the model used to produced the data, the forcings/emissions scenario used to run the model, and the product version. In the current version, only a single source is supported, Lorenz et al (2016) downscaled north american CCSM3 climate model output.

### Example
```ruby
# load the gem
require 'swagger_client'

api_instance = SwaggerClient::DefaultApi.new

opts = { 
  source_id: 3.4, # Float | Database ID of the source.
  scenario: 3.4, # Float | Emission scenario under which the model was run.
  version: 3.4 # Float | The version of the modeling product.
}

begin
  result = api_instance.get_sources(opts)
  p result
rescue SwaggerClient::ApiError => e
  puts "Exception when calling DefaultApi->get_sources: #{e}"
end
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_id** | [**Float**](.md)| Database ID of the source. | [optional] 
 **scenario** | [**Float**](.md)| Emission scenario under which the model was run. | [optional] 
 **version** | [**Float**](.md)| The version of the modeling product. | [optional] 

### Return type

[**GenericResponse**](GenericResponse.md)

### Authorization

No authorization required

### HTTP reuqest headers

 - **Content-Type**: application/json
 - **Accept**: application/json



# **get_timeseries**
> GenericResponse get_timeseries(latitude, longitude, variable_id, source_id)



Get all time points in the database for a single spatial location.  References a single variable/source pair.

### Example
```ruby
# load the gem
require 'swagger_client'

api_instance = SwaggerClient::DefaultApi.new

latitude = 3.4 # Float | Latitude of point of interest.

longitude = 3.4 # Float | Longitude of point of interest.

variable_id = 3.4 # Float | Database ID of variable of interest.

source_id = 3.4 # Float | Database ID of source of interest.


begin
  result = api_instance.get_timeseries(latitude, longitude, variable_id, source_id)
  p result
rescue SwaggerClient::ApiError => e
  puts "Exception when calling DefaultApi->get_timeseries: #{e}"
end
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **latitude** | [**Float**](.md)| Latitude of point of interest. | 
 **longitude** | [**Float**](.md)| Longitude of point of interest. | 
 **variable_id** | [**Float**](.md)| Database ID of variable of interest. | 
 **source_id** | [**Float**](.md)| Database ID of source of interest. | 

### Return type

[**GenericResponse**](GenericResponse.md)

### Authorization

No authorization required

### HTTP reuqest headers

 - **Content-Type**: application/json
 - **Accept**: application/json



# **get_variable_period_types**
> GenericResponse get_variable_period_types(opts)



Get a list of the time periods a variable could represent. A variable period is period of time represented by the measurement. For example, monthly precipitation has a variable period of months.

### Example
```ruby
# load the gem
require 'swagger_client'

api_instance = SwaggerClient::DefaultApi.new

opts = { 
  variable_period_type_id: 3.4 # Float | Database ID of the variable period type
}

begin
  result = api_instance.get_variable_period_types(opts)
  p result
rescue SwaggerClient::ApiError => e
  puts "Exception when calling DefaultApi->get_variable_period_types: #{e}"
end
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_period_type_id** | [**Float**](.md)| Database ID of the variable period type | [optional] 

### Return type

[**GenericResponse**](GenericResponse.md)

### Authorization

No authorization required

### HTTP reuqest headers

 - **Content-Type**: application/json
 - **Accept**: application/json



# **get_variable_types**
> GenericResponse get_variable_types(opts)



Get a list of the variable types in the database. A variable type is a generic representation of what is measured in a dataset. For example, precipitation or maximum temperature.

### Example
```ruby
# load the gem
require 'swagger_client'

api_instance = SwaggerClient::DefaultApi.new

opts = { 
  variable_type_id: 3.4 # Float | Database ID of the variable type
}

begin
  result = api_instance.get_variable_types(opts)
  p result
rescue SwaggerClient::ApiError => e
  puts "Exception when calling DefaultApi->get_variable_types: #{e}"
end
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_type_id** | [**Float**](.md)| Database ID of the variable type | [optional] 

### Return type

[**GenericResponse**](GenericResponse.md)

### Authorization

No authorization required

### HTTP reuqest headers

 - **Content-Type**: application/json
 - **Accept**: application/json



# **get_variable_units**
> GenericResponse get_variable_units(opts)



Get a list of variable units in the database. A variable unit is the units in which a variable is measured.

### Example
```ruby
# load the gem
require 'swagger_client'

api_instance = SwaggerClient::DefaultApi.new

opts = { 
  variable_unit_id: 3.4, # Float | Database ID of the variableUnit.
  variable_unit_abbreviation: "variable_unit_abbreviation_example" # String | Abbreviation of the variable unit in SI units.
}

begin
  result = api_instance.get_variable_units(opts)
  p result
rescue SwaggerClient::ApiError => e
  puts "Exception when calling DefaultApi->get_variable_units: #{e}"
end
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_unit_id** | [**Float**](.md)| Database ID of the variableUnit. | [optional] 
 **variable_unit_abbreviation** | **String**| Abbreviation of the variable unit in SI units. | [optional] 

### Return type

[**GenericResponse**](GenericResponse.md)

### Authorization

No authorization required

### HTTP reuqest headers

 - **Content-Type**: application/json
 - **Accept**: application/json



# **get_variables**
> VariableResponse get_variables(opts)



Returns a list of the variables that currently have raster data associated with them in the database.  A variable is a unique combination of units, averaging period, variable period, and variable type.

### Example
```ruby
# load the gem
require 'swagger_client'

api_instance = SwaggerClient::DefaultApi.new

opts = { 
  variable_type: 56, # Integer | Database ID of the variable type of interest.
  variable_period: 56, # Integer | Variable period by which to filter results.  A variable period type is the period over which the data is representitive.
  variable_period_type: "variable_period_type_example", # String | String representation of the name of the variable period type over which the data is representitive. Example - month.
  averaging_period: 56, # Integer | Period over which the variable has been averaged.
  averaging_period_type: "averaging_period_type_example", # String | String representation of the type of period over which the variable has been averaged. Example - Week.
  variable_units: "variable_units_example", # String | Canonical SI abbreviation for units in which the variable is measured.
  variable_id: 56 # Integer | Database ID of the variable. Returns a single unique variable as the result.
}

begin
  result = api_instance.get_variables(opts)
  p result
rescue SwaggerClient::ApiError => e
  puts "Exception when calling DefaultApi->get_variables: #{e}"
end
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_type** | [**Integer**](.md)| Database ID of the variable type of interest. | [optional] 
 **variable_period** | [**Integer**](.md)| Variable period by which to filter results.  A variable period type is the period over which the data is representitive. | [optional] 
 **variable_period_type** | **String**| String representation of the name of the variable period type over which the data is representitive. Example - month. | [optional] 
 **averaging_period** | [**Integer**](.md)| Period over which the variable has been averaged. | [optional] 
 **averaging_period_type** | **String**| String representation of the type of period over which the variable has been averaged. Example - Week. | [optional] 
 **variable_units** | **String**| Canonical SI abbreviation for units in which the variable is measured. | [optional] 
 **variable_id** | [**Integer**](.md)| Database ID of the variable. Returns a single unique variable as the result. | [optional] 

### Return type

[**VariableResponse**](VariableResponse.md)

### Authorization

No authorization required

### HTTP reuqest headers

 - **Content-Type**: application/json
 - **Accept**: application/json



# **post_data**
> DataResponse post_data(opts)



Get data for an array of space-time points for a given source and variable combination. Each point in the array must specify latitude, longitude, and time.  The source and variables are specified for the request as a whole.

### Example
```ruby
# load the gem
require 'swagger_client'

api_instance = SwaggerClient::DefaultApi.new

opts = { 
  data: SwaggerClient::PostDataRequest.new # PostDataRequest | An array of space-time locations for which to get data.
}

begin
  result = api_instance.post_data(opts)
  p result
rescue SwaggerClient::ApiError => e
  puts "Exception when calling DefaultApi->post_data: #{e}"
end
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data** | [**PostDataRequest**](PostDataRequest.md)| An array of space-time locations for which to get data. | [optional] 

### Return type

[**DataResponse**](DataResponse.md)

### Authorization

No authorization required

### HTTP reuqest headers

 - **Content-Type**: application/json
 - **Accept**: application/json



