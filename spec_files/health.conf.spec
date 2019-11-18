#   Version 7.3.0
#
# This file sets the default thresholds for Splunk Enterprise's built
# in Health Report.
#
# Feature stanzas contain indicators, and each indicator has two thresholds:
# * Yellow: Indicates something is wrong and should be investigated.
# * Red: Means that the indicator is effectively not working.
#
# There is a health.conf in the $SPLUNK_HOME/etc/system/default/ directory.
# Never change or copy the configuration files in the default directory.
# The files in the default directory must remain intact and in their original
# location.
#
# To set custom configurations, create a new file with the name health.conf in
# the $SPLUNK_HOME/etc/system/local/ directory. Then add the specific settings
# that you want to customize to the local configuration file.
#
# To learn more about configuration files (including precedence), see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

[health_reporter]
full_health_log_interval = <number>
* The amount of time, in seconds, that elapses between each ‘PeriodicHealthReporter=INFO’ log entry.
* Default: 30.

suppress_status_update_ms = <number>
* The minimum amount of time, in milliseconds, that must elapse between an
  indicator's health status changes.
* Changes that occur earlier will be suppressed.
* Default: 300.

alert.disabled = [0|1]
* A value of 1 disables the alerting feature for health reporter.
* If the value is set to 1, alerting for all features is disabled.
* Default: 0 (enabled)

alert.actions = <string>
* The alert actions that will run when an alert is fired.

alert.min_duration_sec = <integer>
* The minimum amount of time, in seconds, that the health status color must 
  persist within threshold_color before triggering an alert.
* Default: 60.

alert.threshold_color = [yellow|red]
* The health status color that will trigger an alert.
* Default: red.

alert.suppress_period = <integer>[m|s|h|d]
* The minimum amount of time, in [minutes|seconds|hours|days], that must
  elapse between each fired alert.
* Alerts that occur earlier will be sent as a batch after this time period
  elapses.
* Default: 10 minutes.

[clustering]
health_report_period = <number>
* The amount of time, in seconds, that elapses between each Clustering
  health report run.
* Default: 20.
disabled = [0|1]
* A value of 1 disables the clustering feature health check.
* Default: 0 (enabled)

[feature:*]
suppress_status_update_ms = <number>
* The minimum amount of time, in milliseconds, that must elapse between an indicator's
  health status changes.
* Changes that occur earlier will be suppressed.
* Default: 300.

display_name = <string>
* A human readable name for the feature.

alert.disabled = [0|1]
* A value of 1 disables alerting for this feature.
* If alerting is disabled in the [health_reporter] stanza, alerting for this feature is disabled,
  regardless of the value set here.
* Otherwise, if the value is set to 1, alerting for all indicators is disabled.
* Default: 0 (enabled)

alert.min_duration_sec = <integer>
* The minimum amount of time, in seconds, that the health status color must 
  persist within threshold_color before triggering an alert.

alert.threshold_color = [yellow|red]
* The health status color to trigger an alert.
* Default: red.

indicator:<indicator name>:description = <string>
* Description of this indicator to help users to make basic decisions such as:
  Turning indicators on or off
  Adjusting the threshold of an indicator
  Turning on alerting for an indicator

indicator:<indicator name>:<indicator color> = <number>
* There are various indicator names. See your health.conf for the complete list.
* There are two valid colors: yellow and red.
* These settings should not be adjusted lightly. If the numbers are set too
  high, you might inadvertently mask serious errors that the Health Report is
  trying to bring to your attention.

alert:<indicator name>.disabled = [0|1]
* A value of 1 disables alerting for this indicator.
* Default: 0 (enabled)

alert:<indicator name>.min_duration_sec = <integer>
* The minimum amount of time, in seconds, that the health status color must 
  persist within threshold_color before triggering an alert.

alert:<indicator name>.threshold_color = [yellow|red]
* The health status color to trigger an alert.

[alert_action:*]
disabled = [0|1]
* A value of 1 disables this alert action.
* Default: 0 (enabled)

action.<action parameter> = <string>
* There are various parameters for different alert actions.
* Each value defines one parameter for the alert action.
