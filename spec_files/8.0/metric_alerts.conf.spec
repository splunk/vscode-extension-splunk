#   Version 8.0.0
#
# This file contains possible setting/value pairs for metric alert entries in the
# metric_alerts.conf file. You can configure metric alerts by creating your own
# metric_alerts.conf file.
#
# There is a default metric_alerts.conf file in $SPLUNK_HOME/etc/system/default. To
# set custom configurations, place a metric_alerts.conf file in
# $SPLUNK_HOME/etc/system/local/. For examples, see the
# metric_alerts.conf.example file. You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#  * You can also define global settings outside of any stanza, at the top of
#    the file.
#  * Each conf file should have at most one default stanza. If there are
#    multiple default stanzas, settings are combined. In the case of multiple
#    definitions of the same settings, the last definition in the file wins.
#  * If a setting is defined at both the global level and in a specific
#    stanza, the value in the specific stanza takes precedence.

#*******
# The possible settings for the metric_alerts.conf file are:
#*******

[<alert_name>]
* The <alert_name> is the name of the metric alert. 
* Required.

description = <string>
* This string provides a description of the metric alert. 
* Optional.
* Default: No default

groupby = <list of dimension fields>
* The list of dimension fields, delimited by comma, for the group-by clause of 
  the alert search.
* This leads to multiple aggregation values, one per group, instead of one 
  single value.
* Optional.
* Default: No default
 
filter = <string>
* This setting provides one or more Boolean expressions like 
  '<dimension_field>=<value>' to define the search result dataset to monitor 
  for the alert condition. 
* Link multiple Boolean expressions with the 'AND' operator.
* The filter does not support subsearches, macros, tags, event types, or time 
  modifiers such as 'earliest' or 'latest'.
* This setting combines with the metric_index setting to provide the full alert 
  search filter.
* Optional.
* Default: No default

metric_indexes = <metric index name>
* Specifies one or more metric indexes, delimited by comma.
* Combines with the filter setting to define search result dataset to monitor 
  for the alert condition. 
* Required.
* Default: No default

condition = <boolean eval expression>
* Specifies an alert condition for one or more metric_name and aggregation 
  pairs. The Splunk software applies this evaluation to the results of the 
  alert search on a regular interval. When the alert condition evaluates to 
  'true', the alert is triggered. 
* The condition must reference at least one 'mstats_aggregation(metric_name)' 
  field in single quotes.
* The condition can also reference dimensions specified in the group-by fields.
* Required.
* Default: No default

trigger.suppress = <time-specifier>
* Specifies the suppression period to silence alert actions and notifications.
  * The suppression period goes into effect when an alert is triggered.
  * During this period, if the alert is triggered, its actions do not happen 
    and its notifications do not go out. 
  * When the period elapses, a subsequent triggering of the alert causes alert 
    actions and notifications to take place as usual, and the alert is
    suppressed again.
* Use [number]m to specify a timespan in minutes.
* Set to 0 to disable suppression.
* Default: 0

trigger.expires = <time-specifier>
* Sets the period of time that a triggered alert record displays on the
  Triggered Alerts page.
* Use [positive integer][time-unit], where time_unit can be 'm' for minutes,
  'h' for hours, and 'd' for days.
* Set to 0 to make triggered alerts expire immediately so they do not appear on
  the Triggered Alerts page at all.
* Default: 24h

trigger.max_tracked = <number>
* Specifies the maximum number of instances of this alert that can display in 
  the triggered alerts dashboard.
* When this threshold is passed, the Splunk software removes the earliest 
  instances from the dashboard to honor this maximum number.
* Set to 0 to remove the cap.
* Default: 20

label.<label-name> = <label-value>
* Arbitrary key-value pairs for labeling this alert.
* These settings will be opaque to the backend (not interpreted in any way).
* Can be used by applications calling `alerts/metric_alerts` endpoint.

splunk_ui.<label-name> = <label-value>
* For Splunk internal use only.
* Arbitrary key-value pairs for labeling this alert for the exclusive use by 
  Splunk.
* These settings are automatically generated and should not be changed.

#*******
# generic action settings.
# For a comprehensive list of actions and their arguments, refer to the 
# alert_actions.conf file.
#*******

action.<action_name> = <boolean>
* Indicates whether the action is enabled or disabled for a particular metric 
  alert.
* The 'action_name' can be: email | logevent | rss | script | webhook
* For more about the defined alert actions see the alert_actions.conf file.
* Optional.
* Default: No default

action.<action_name>.<parameter> = <value>
* Overrides an action's parameter as defined in the alert_actions.conf file, 
  with a new <value> for this metric alert only.
* Default: No default
