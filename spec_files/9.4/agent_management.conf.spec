#   Version 9.4.3
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
* Default: ERROR.

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
* The maximum amount of time an idle connection made by the Agent Manager to splunkd remains idle before closing.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", "h".
* Default: 5m.

[settings_sync]
* The Agent Management helper process settings for the settings synchronization subsystem.
* The settings synchronization subsystem periodically obtains the Deployment Server settings.

polling_interval = <string>
* How long the Agent Manager waits between HTTP calls to retrieve the Deployment Server settings.
* Valid values are numbers followed by a time unit.
* Valid time units are "ms", "s", "m", "h".
* Default: 5m.
