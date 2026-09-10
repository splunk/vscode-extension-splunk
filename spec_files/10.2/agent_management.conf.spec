#   Version 10.2.3
#
############################################################################
# OVERVIEW
############################################################################
# This file contains descriptions of the settings that you can use to
# configure the agent management feature.
#
# There is an agent_management.conf file in the $SPLUNK_HOME/etc/system/default/ directory.
# Never change or copy the configuration files in the default directory.
# The files in the default directory must remain intact and in their original
# location.
#
# To set custom configurations, create a new file with the name agent_management.conf in
# the $SPLUNK_HOME/etc/system/local/ directory. Then add the specific settings
# that you want to customize to the local configuration file.
# You must restart the Splunk instance to enable configuration changes.
#
# To learn more about configuration files (including file precedence) see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

[general]
* Agent management helper process settings. This stanza must exist.

fallback_to_deployment_server_ui = <boolean>
* REMOVED.  This setting is no longer used.

log_level = <string> 
* How verbose the logs are.
* log level = DEBUG | INFO | WARN | ERROR | FATAL
* Default: INFO

request_timeout = <string>
* A global request timeout setting that defines how long the agent management processes a request before it times out.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", "h".
* Default: 5m.

[search_client]
* Agent management helper process settings for the SPL subsystem.

polling_interval = <string>
* How long the agent management waits between HTTP calls to retrieve search results.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", "h".
* Default: 500ms.

query_agents_with_error = <string>
* The SPL search that is run to obtain a list of agents with a status of "error".

query_agents_offline = <string>
* The SPL search that is run to obtain a list of offline agents. 

query_agents_updated_config = <string>
* The SPL search that is run to obtain a list of agents with updated configurations.

query_agent_version = <string>
* The SPL search that is run to obtain a list of agents and their corresponding versions.

query_app_summary = <string>
* The SPL search that is run to obtain a summary of the status of each application.

[splunkd_client]
* Agent management helper process settings that are used for communicating with splunkd.

connection_pool_size = <integer>
* The number of HTTP connections that can be handled simultaneously by the agent management.
* Default: 10

request_timeout = <string>
* A time limit for HTTP requests made by the agent management to splunkd.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", "h".
* Default: 285s

connection_keep_alive = <string>
* The maximum amount of time an idle connection made by the
  agent management to splunkd remains idle before closing.
* This value must be set lower than the 'busyKeepAliveIdleTimeout'
  setting in server.conf, '[httpServer]' stanza.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", and "h".
* Default: 11s

[settings_sync]
* The agent management helper process settings for the settings synchronization subsystem.
* The settings synchronization subsystem periodically obtains the Deployment Server settings.

polling_interval = <string>
* How long the agent management waits between HTTP calls to retrieve the Deployment Server settings.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", "h".
* Default: 5m.

[effective_configuration]
* Settings dedicated to the Effective Configuration feature.

max_size = <positive integer>
* The maximum size, in megabytes, of the effective configuration 
  that the universal forwarder sends to the agent management, and that
  the deployment server saves.
* The effective configuration of the forwarder is comprised of 
  the rules of operation and data processing for the forwarder,
  specifically, the configuration as shown by various 'splunk
  btool' commands.
* If the size of the effective configuration for a forwarder
  exceeds this value, then the agent management rejects the payload
  as too large, and the deployment server does not save
  the configuration.
* Must be a positive number.
* Default: 16

cleanup_threshold = <positive integer>
* The limit of the total size of all effective configurations
  data on the disk (in MB). When this limit is exceeded,
  the scheduled cron cleanup job will perform the cleanup.
* There is no maximum value for this setting, a very large value
  (over 10000) can cause the cleanup to never run.
* Must be a positive number.
* Default: 6144

cleanup_schedule = <string>
* The cron schedule for cleaning up the effective configuration data.
* The default schedule is set to 3:00 AM every day in the local time zone.
* To turn off the effective configuration cleanup, set the value to "disabled".
* Must be in the cron format.
* Default: 0 3 * * *

[telemetry]
* Agent management settings for product telemetry data collection.
* These settings control whether and how the agent management collects
  telemetry data.
* Sending telemetry data to the Splunk platform is done according to rules
  defined in the 'telemetry.conf' file.

enabled = <boolean>
* A value of "true" enables product telemetry collection in agent
  management.
* A value of "false" disables product telemetry collection.
* This flag does not override settings from the 'telemetry.conf' file.
  In particular, collected data will not be sent to the Splunk platform
  until proper consent is given in general telemetry settings for the
  Splunk software instance.
Default: true

cron_schedule = <string>
* The cron schedule for telemetry data collection by agent management.
* The default schedule is set to 3:15 AM every day in the local time zone.
* The value must be in cron format.
* Default: 15 3 * * *

collection_timeout = <string>
* The maximum amount of time agent management can spend processing
  the whole telemetry collection operation.
* Valid values are numbers followed by a time unit.
* Minimum value is 1s.
* Valid time units are "s", "m", "h".
* Default: 10m

job_timeout = <string>
* The maximum amount of time agent management can spend on running a single
  telemetry job, which is a part of whole telemetry collection.
* Valid values are numbers followed by a time unit.
* Minimum value is 1s.
* Valid time units are "s", "m", "h".
* Default: 5m
