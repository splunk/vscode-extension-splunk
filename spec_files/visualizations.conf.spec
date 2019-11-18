#   Version 7.3.0
#
# This file contains definitions for visualizations an app makes available
# to the system. An app intending to share visualizations with the system
# should include a visualizations.conf in $SPLUNK_HOME/etc/apps/<appname>/default
#
# visualizations.conf should include one stanza for each visualization to be shared
#
# To learn more about configuration files (including precedence) please see
# the documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

#*******
# The possible attribute/value pairs for visualizations.conf are:
#*******

[<stanza name>]
* Create a unique stanza name for each visualization. It should match the name
  of the visualization 
* Follow the stanza name with any number of the following attribute/value
  pairs.
* If you do not specify an attribute, Splunk uses the default.

disabled = <bool>
* Optional.
* Disable the visualization by setting to true.
* If set to true, the visualization is not available anywhere in Splunk
* Defaults to false.

allow_user_selection = <bool>
* Optional.
* Whether the visualization should be available for users to select
* Defaults to true

label = <string>
* Required.
* The human-readable label or title of the visualization
* Will be used in dropdowns and lists as the name of the visualization
* Defaults to <app_name>.<viz_name>

description = <string>
* Required.
* The short description that will show up in the visualization picker
* Defaults to ""

search_fragment = <string>
* Required.
* An example part of a search that formats the data correctly for the viz. Typically the last pipe(s) in a search query.
* Defaults to ""

default_height = <int>
* Optional.
* The default height of the visualization in pixels
* Defaults to 250

default_width = <int>
* Optional.
* The default width of the visualization in pixels
* Defaults to 250

min_height = <int>
* Optional.
* The minimum height the visualizations can be rendered in.
* Defaults to 50.

min_width = <int>
* Optional.
* The minimum width the visualizations can be rendered in.
* Defaults to 50.

max_height = <int>
* The maximum height the visualizations supports.
* Optional.
* Default is unbounded.

max_width = <int>
* The maximum width the visualizations supports.
* Optional.
* Default is unbounded.

trellis_default_height = <int>
* Default is 400

trellis_min_widths = <string>
* Default is undefined

trellis_per_row = <string>
* Default is undefined

# Define data sources supported by the visualization and their initial fetch params for search results data

data_sources = <csv-list>
* Comma separated list of data source types supported by the visualization.
* Currently the visualization system provides these types of data sources:
* - primary: Main data source driving the visualization.
* - annotation: Additional data source for time series visualizations to show discrete event annotation on the time axis.
* Defaults to "primary"

data_sources.<data-source-type>.params.output_mode = [json_rows|json_cols|json]
* Optional.
* the data format that the visualization expects. One of:
*  - "json_rows": corresponds to SplunkVisualizationBase.ROW_MAJOR_OUTPUT_MODE
*  - "json_cols": corresponds to SplunkVisualizationBase.COLUMN_MAJOR_OUTPUT_MODE
*  - "json": corresponds to SplunkVisualizationBase.RAW_OUTPUT_MODE
* Defaults to undefined and requires the javascript implementation to supply initial data params.

data_sources.<data-source-type>.params.count = <int>
* Optional.
* How many rows of results to request, default is 1000

data_sources.<data-source-type>.params.offset = <int>
* Optional.
* The index of the first requested result row, default is 0

data_sources.<data-source-type>.params.sort_key = <string>
* Optional.
* The field name to sort the results by

data_sources.<data-source-type>.params.sort_direction = [asc|desc]
* Optional.
* The direction of the sort
* - asc: sort in ascending order
* - desc: sort in descending order
* Defaults to desc

data_sources.<data-source-type>.params.search = <string>
* Optional.
* A post-processing search to apply to generate the results

data_sources.<data-source-type>.mapping_filter = <bool>
data_sources.<data-source-type>.mapping_filter.center = <string>
data_sources.<data-source-type>.mapping_filter.zoom = <string>

supports_trellis = <bool>
* Optional.
* Indicates whether trellis layout is available for this visualization
* Defaults to false

supports_drilldown = <bool>
* Optional.
* Indicates whether the visualization supports drilldown (responsive actions triggered when users click on the visualization).
* Defaults to false

supports_export = <bool>
* Optional.
* Indicates whether the visualization supports being exported to PDF.
* This setting has no effect in third party visualizations. 
* Defaults to false

# Internal settings for bundled visualizations. They are ignored for third party visualizations.
core.type = <string>
core.viz_type = <string>
core.charting_type = <string>
core.mapping_type = <string>
core.order = <int>
core.icon = <string>
core.preview_image = <string>
core.recommend_for = <string>
core.height_attribute = <string>

