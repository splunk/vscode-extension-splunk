#   Version 9.1.4
#
# This file contains possible attribute/value pairs for rollup policy entries in
# metric_rollups.conf.  You can configure rollup policies by creating your own
# metric_rollups.conf.
#
# There is a default metric_rollups.conf in $SPLUNK_HOME/etc/system/default. To
# set custom configurations, place a metric_rollups.conf in
# $SPLUNK_HOME/etc/system/local/.  For examples, see
# metric_rollups.conf.example. You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#  * You can also define global settings outside of any stanza, at the top of
#    the file.
#  * Each conf file should have at most one default stanza. If there are
#    multiple default stanzas, attributes are combined. In the case of multiple
#    definitions of the same attribute, the last definition in the file wins.
#  * If an attribute is defined at both the global level and in a specific
#    stanza, the value in the specific stanza takes precedence.

#*******
# The possible attribute/value pairs for metric_rollups.conf are:
#*******

[index:<Metric Index Name>]
* Each metric_rollups.conf stanza defines the rollup summarization policy for a
  specific metric index.
* A rollup policy can include multiple rollup summaries, each with a
  different rollup period.
* Go to indexes.conf to find metric index configurations. Metric indexes have
  datatype=metric in their configurations.

defaultAggregation = <'#' separated list of aggregation functions>
* Required. The default aggregation function for the rollup policy. The Splunk
  software uses this aggregation function to generate the rollup summmary data
  points for all metrics in the source index with the exception of metrics that
  are identified by 'aggregation.<metric_name>'
  exclusion rules.
* For example, if a rollup summary with a period of 1 hour has
  'defaultAggregation = avg', each metric data point that it generates is the
  average of an hour of data points from the source metric.
* Note that the 'perc' and 'upperperc' options require an integer.
* Supported aggregation functions: [avg|count|max|median|min|perc<int>|sum]
* Default: avg

dimensionList = <comma-separated list of dimensions>
* Optional. This setting provides a comma-separated list of dimensions. The
  dimensions must be present within the index to which the rollup policy
  applies.
* This list corresponds to the `dimensionListType` setting, which determines
  whether this set of dimensions is included or excluded from the rollup
  metrics that are generated by the rollup summary.
* Use the Metrics Catalog REST API endpoints to see the metrics and dimensions
  for a particular index. For more information see the REST API Reference
  Manual.
* Default: not set

dimensionListType = [excluded|included]
* Optional. This setting determines whether the list of dimensions specified by
  the `dimensionList` setting is included or excluded from the rollup metrics
  that are generated by the rollup summaries in the rollup policy.
* Select 'included' to indicate that the rollup metrics produced by the rollup
  policy will filter out all dimensions except the ones in the list.
* Select 'excluded' to indicate that the rollup metrics produced by the rollup
  policy will include all available dimensions except the ones in the list.
* Default: excluded

metricList = <comma-separated list of metrics>
* Optional. This setting provides a comma-separated list of metrics.
* This list corresponds to the 'metricListType' setting.
* The listed metrics must be present within the source metric index.
  * Use the Metrics Catalog REST API endpoints in conjunction with the 'rest'
    command to see the metrics that exist within a particular source index. See
    the REST API Reference Manual and the Search Reference for more information.
* Default: not set

metricListType = <excluded/included>
* Optional. This setting determines whether the list of metrics specified by
  the 'metricList' setting is included or excluded when the search head rolls
  metrics up to the rollup summaries.
* Select "included" to have the search head roll up only the listed metrics.
* Select "excluded" to have the search head roll up all available metrics in
  the source metric index except the listed metrics.
* Default: excluded

aggregation.<metric_name> = <'#' separated list of aggregation functions>
* Optional. Sets an exclusion rule for a rollup policy. Use this setting to
  override the 'defaultAggregation' setting for a specific metric.
* Create exclusion rules for metrics that require different aggregation
  functions than the majority of the metrics in a rollup policy.
* A single rollup policy can have multiple exclusion rules.
* Supported aggregation functions: [avg|count|max|median|min|perc<int>|sum]
* Default: no values

rollup.<summary number>.span = <time range string>
* Required for each rollup summary in the rollup policy.
* The Splunk software defines the '<summary number>' when you create a summary
  policy through Splunk Web or the REST API endpoint.
* Defines the rollup period for a rollup summary.
* The '<time range string>' cannot be shorter than the 'minSpanAllowed' setting
  in limits.conf.
* This setting is required. Do not leave it blank.
* Default for <summary number>: 1
* Default for <time range string>: 1h

rollup.<summary number>.rollupIndex = <string Index name>
* Required for each rollup summary in the rollup policy.
* Defines the target index for the rollup metrics generated by a rollup summary.
* The Splunk software defines the '<summary number>' when you create a summary
  policy through Splunk Web or the REST API endpoint.
* The index name must exist in indexes.conf.
* This setting is required. Do not leave it blank.
* Default for <summary number>: 1
* Default for <string Index name>: The <Metric Index Name> in the stanza header
  for this rollup policy.
