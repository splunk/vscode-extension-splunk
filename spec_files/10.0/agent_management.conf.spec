#   Version 10.0.2
#
############################################################################
# OVERVIEW
############################################################################
# This file contains descriptions of the settings that you can use to
# configure the Agent Management feature.
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
* Agent Management helper process settings. This stanza must exist.

fallback_to_deployment_server_ui = <boolean>
* Indicates which UI the forwarder_management should use. When set to "false", the forwarder_management uses the agent management UI, When set to "true", the forwarder_management uses the deployment server UI.
* Default: false.

log_level = <string> 
* How verbose the logs are.
* log level = DEBUG | INFO | WARN | ERROR | FATAL
* Default: INFO

request_timeout = <string>
* A global request timeout setting that defines how long the Agent Manager processes a request before it times out.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", "h".
* Default: 90s.

[search_client]
* Agent Management helper process settings for the SPL subsystem.

polling_interval = <string>
* How long the Agent Manager waits between HTTP calls to retrieve search results.
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
* Agent Management helper process settings that are used for communicating with splunkd.

connection_pool_size = <integer>
* The number of HTTP connections that can be handled simultaneously by the Agent Manager.
* Default: 10

request_timeout = <string>
* A time limit for HTTP requests made by the Agent Manager to splunkd.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", "h".
* Default: 60s.

connection_keep_alive = <string>
* The maximum amount of time an idle connection made by the
  Agent Manager to splunkd remains idle before closing.
* This value must be set lower than the 'busyKeepAliveIdleTimeout'
  setting in server.conf, '[httpServer]' stanza.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", and "h".
* Default: 11s

[settings_sync]
* The Agent Management helper process settings for the settings synchronization subsystem.
* The settings synchronization subsystem periodically obtains the Deployment Server settings.

polling_interval = <string>
* How long the Agent Manager waits between HTTP calls to retrieve the Deployment Server settings.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", "h".
* Default: 5m.

[effective_configuration]
* Settings dedicated to the Effective Configuration feature.

max_size = <positive integer>
* The maximum size, in megabytes, of the effective configuration 
  that the universal forwarder sends to the Agent Manager, and that
  the deployment server saves.
* The effective configuration of the forwarder is comprised of 
  the rules of operation and data processing for the forwarder,
  specifically, the configuration as shown by various 'splunk
  btool' commands.
* If the size of the effective configuration for a forwarder
  exceeds this value, then the Agent Manager rejects the payload
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
