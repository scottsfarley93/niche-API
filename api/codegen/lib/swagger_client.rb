=begin
Niche API

REST API to access gridded climate model data at specific points in time.  Developed specifically to support Ice Age Mapper / Niche Viewer, and to tie into morphospace visualizations of NeotomaDB data. Enables users to select climate data at single space-time points, arrays of space-time points, or time series at single points.  University of Wisconsin, Madison Department of Geography.

OpenAPI spec version: 2.0.0

Generated by: https://github.com/swagger-api/swagger-codegen.git


=end

# Common files
require 'swagger_client/api_client'
require 'swagger_client/api_error'
require 'swagger_client/version'
require 'swagger_client/configuration'

# Models
require 'swagger_client/models/data_point'
require 'swagger_client/models/data_response'
require 'swagger_client/models/error_response'
require 'swagger_client/models/generic_response'
require 'swagger_client/models/point_request'
require 'swagger_client/models/post_data_request'
require 'swagger_client/models/time_series_point'
require 'swagger_client/models/time_series_response'
require 'swagger_client/models/variable'
require 'swagger_client/models/variable_response'

# APIs
require 'swagger_client/api/default_api'

module SwaggerClient
  class << self
    # Customize default settings for the SDK using block.
    #   SwaggerClient.configure do |config|
    #     config.username = "xxx"
    #     config.password = "xxx"
    #   end
    # If no block given, return the default Configuration object.
    def configure
      if block_given?
        yield(Configuration.default)
      else
        Configuration.default
      end
    end
  end
end