#   Version 7.3.0
#
# This file contains possible attribute/value pairs for creating roles in
# authorize.conf.  You can configure roles and granular access controls by
# creating your own authorize.conf.

# There is an authorize.conf in $SPLUNK_HOME/etc/system/default/. To set
# custom configurations, place an authorize.conf in
# $SPLUNK_HOME/etc/system/local/. For examples, see authorize.conf.example.
# You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see
# the documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#   * You can also define global settings outside of any stanza, at the top
#     of the file.
#   * Each .conf file should have at most one default stanza. If there are
#     multiple default stanzas, attributes are combined. In the case of
#     multiple definitions of the same attribute, the last definition in
#     the file wins.
#   * If an attribute is defined at both the global level and in a specific
#     stanza, the value in the specific stanza takes precedence.

[default]
srchFilterSelecting = <boolean>
* Determines whether a role's search filters are used for selecting or
  eliminating during role inheritance.
* If "true", the search filters are used for selecting. The filters are joined
  with an OR clause when combined.
* If "false", the search filters are used for eliminating. The filters are joined
  with an AND clause when combined.
* Example:
  * role1 srchFilter = sourcetype!=ex1 with selecting=true
  * role2 srchFilter = sourcetype=ex2 with selecting = false
  * role3 srchFilter = sourcetype!=ex3 AND index=main with selecting = true
  * role3 inherits from role2 and role 2 inherits from role1
  * Resulting srchFilter = ((sourcetype!=ex1) OR
    (sourcetype!=ex3 AND index=main)) AND ((sourcetype=ex2))
* Default: true

[capability::<capability>]
* DO NOT edit, remove, or add capability stanzas. The existing capabilities
  are the full set of Splunk system capabilities.
* Splunk software adds all of its capabilities this way.
* For the default list of capabilities and assignments, see authorize.conf
  under the 'default' directory.
* Only alphanumeric characters and "_" (underscore) are allowed in
  capability names.
  Examples:
  * edit_visualizations
  * view_license1
* Descriptions of specific capabilities are listed below.

[role_<roleName>]
<capability> = <enabled>
* A capability that is enabled for this role. You can list many capabilities
  for each role.
* NOTE: 'enabled' is the only accepted value here, as capabilities are
  disabled by default.
* Roles inherit all capabilities from imported roles, and you cannot disable
  inherited capabilities.
* Role names cannot have uppercase characters. Usernames, however, are
  case-insensitive.
* Role names cannot contain spaces, colons, semicolons, or forward slashes.

importRoles = <semicolon-separated list>
* A list of other roles and their associated capabilities that Splunk software
  should import.
* Importing other roles also imports the other aspects of that role, such as
  allowed indexes to search.
* By default a role imports no other roles.

grantableRoles = <semicolon-separated list>
* A list of roles that determines which users, roles, and capabilities 
  that a user with a specific set of permissions can manage.
* This setting lets you limit the scope of user, role, and capability
  management that these users can perform.
* When you set 'grantableRoles', a user that holds a role with the
  'edit_roles_grantable' and 'edit_user' capabilities can do only the
  following with regards to access control management for the Splunk
  Enterprise instance:
  * They can edit only the roles that contain capabilities that are a 
    union of the capabilities in the roles that you specify 
    with this setting.
  * Any new roles that they create can contain only the capabilities 
    that are a union of these capabilities.
  * Any new roles that they create can search only the indexes that
    have been assigned to all roles that have been specified with 
    this setting.
  * They can see only users who have been assigned roles that contain
    capabilities that are a union of these capabilities.
  * They can assign users only to roles whose assigned capabilities are a
    union of these capabilities.
* For this setting to work, you must assign a user at least one role 
  that:
  * Has both the 'edit_roles_grantable' and 'edit_user' capabilities
    assigned to it, and
  * Does NOT have the 'edit_roles' capability assigned to it.
* Example:
  Consider a Splunk instance where roles role1-role4 have the
  following capabilities:
  
  role1: cap1, cap2, cap3
  role2: cap4, cap5, cap6
  role3: cap1, cap6
  role4: cap4, cap8

  And users user1-user4 have been assigned the following roles:
  user1: role1
  user2: role2
  user3: role3
  user4: role4

  If you define the 'grantableRoles' setting as follows for 
  the 'power' role:
  
  [role_power]
  grantableRoles = role1;role2

  and edit the role so that the 'edit_roles_grantable' 
  capability is selected, and the 'edit_roles' capability
  is not selected,
  
  then a user that has been assigned the 'power' role can make only
  the following access control changes on the instance:
  * View or edit the following users: user1, user2, user3
  * Assign the following roles: role1, role2, role3
  * Create roles with the following capabilities: cap1, cap2, cap3,
    cap4, cap5, cap6
* Only the 'admin' role holds the 'edit_roles_grantable' capability on
  a new Splunk Enterprise installation.
* If you make changes to the 'admin' role, 'grantableRoles' is set to
  "admin".
* This setting does not work if you use tokens to authenticate into a
  Splunk Enterprise instance.
* Default (if 'admin' role is edited): admin
* Default (otherwise): not set

srchFilter = <semicolon-delimited list>
* A list of search filters for this role.
* To override any search filters from imported roles, set this to "*", as
  the 'admin' role does.
* By default, Splunk software does not perform search filtering.

srchTimeWin = <integer>
* Maximum time span, in seconds, of a search.
* This time window limit is applied backwards from the latest time
  specified in a search.
* To override any search time windows from imported roles, set this to "0"
  (infinite), as the 'admin' role does.
* "-1" is a special value implying that no search window has been set for
  this role.
    * This is equivalent to not setting the 'srchTimeWin' setting at all,
      which means it can be easily overridden by an imported role.
* By default, searches are not limited to any specific time window.

srchDiskQuota = <integer>
* The maximum amount of disk space, in megabytes, that can be used by search
  jobs for a specific user with this role.
* In search head clustering environments, this setting takes effect on a
  per-member basis. There is no cluster-wide accounting.
* The dispatch manager checks the quota at the dispatch time of a search.
  Additionally, the search process checks the quota at intervals that are defined
  in the 'disk_usage_update_period' setting in limits.conf as long as the
  search is active.
* A user can occasionally exceed the quota because the search process does
  not constantly check the quota.
* Exceeding this quota causes the search to be auto-finalized immediately,
  even if there are results that have not yet been returned.
* Default: 100

srchJobsQuota = <integer>
* The maximum number of concurrently running historical searches that a user
  with this role can have.
* This setting excludes real-time searches. See the 'rtSrchJobsQuota' setting.
* Default: 3

rtSrchJobsQuota = <integer>
* The maximum number of concurrently running real-time searches that a user
  with this role can have.
* Default: 6

srchMaxTime = <integer><unit>
* The maximum amount of time that search jobs from specific users with this role are
  allowed to run.
* After a search runs for this amount of time, it auto-finalizes.
* If the role inherits from other roles, the value of the 'srchMaxTime' setting is
  specified in the included roles.
* This maximum value does not apply to real-time searches.
* Examples: 1h, 10m, 2hours, 2h, 2hrs, 100s
* Default: 100days

srchIndexesDefault = <semicolon-separated list>
* A list of indexes to search when no index is specified.
* These indexes can be wild-carded ("*"), with the exception that "*" does not
  match internal indexes.
* To match internal indexes, start with an underscore ("_"). All internal indexes are
  represented by "_*".
* The wildcard character "*" is limited to match either all the non-internal
  indexes or all the internal indexes, but not both at once.
* If you make any changes in the "Indexes searched by default" Settings panel
  for a role in Splunk Web, those values take precedence, and any wildcards
  you specify in this setting are lost.
* No default.

srchIndexesAllowed = <semicolon-separated list>
* A list of indexes that this role is allowed to search.
* Follows the same wildcarding semantics as the 'srchIndexesDefault' setting.
* If you make any changes in the "Indexes" Settings panel for a role in Splunk Web,
  those values take precedence, and any wildcards you specify in this setting are lost.
* No default.

deleteIndexesAllowed = <semicolon-separated list>
* A list of indexes that this role is allowed to delete.
* This setting must be used in conjunction with the 'delete_by_keyword' capability.
* Follows the same wildcarding semantics as the 'srchIndexesDefault' setting.
* No default.

cumulativeSrchJobsQuota = <integer>
* The maximum total number of concurrently running historical searches
  across all members of this role.
* For this setting to take effect, you must set the 'enable_cumulative_quota'
  setting to "true" in limits.conf.
* If a user belongs to multiple roles, the user's searches count against
  the role with the largest cumulative search quota. Once the quota for
  that role is consumed, the user's searches count against the role with
  the next largest quota, and so on.
* In search head clustering environments, this setting takes effect on a
  per-member basis. There is no cluster-wide accounting.
* No default.

cumulativeRTSrchJobsQuota = <integer>
* The maximum total number of concurrently running real-time searches
  across all members of this role.
* For this setting to take effect, you must set the 'enable_cumulative_quota'
  setting to "true" in limits.conf.
* If a user belongs to multiple roles, the user's searches count against
  the role with the largest cumulative search quota. Once the quota for
  that role is consumed, the user's searches count against the role with
  the next largest quota, and so on.
* In search head clustering environments, this setting takes effect
  on a per-member basis. There is no cluster-wide accounting.
* No default.

federatedProviders = <semicolon-separated list>
* List of federated providers that the role can access.
* Allows a user to run federated searches defined in the savedsearches.conf file. This
* setting must be used in conjunction with fsh_search capability.
* Defaults to none.

####
# Descriptions of Splunk system capabilities.
# Capabilities are added to roles to which users are then assigned.
# When a user is assigned a role, they acquire the capabilities added to that role.
####

[tokens_auth]
* Settings for token authorization.

expiration = <relative-time-modifier>|never
* The relative time when an authorization token expires.
* The syntax for using time modifiers is:
  * [+]<time_integer><time_unit>@<time_unit>
  * Where time_integer is an integer value and time_unit is relative
  * time unit in seconds (s), minutes (m), hours (h) or days (d) etc.
* The steps to specify a relative time modifier are:
  * Indicate the time offset from the current time.
  * Define the time amount, which is a number and a unit.
  * Specify a "snap to" time unit. The time unit indicates the nearest
    or latest time to which your time amount rounds down.
* For example, if you configure this setting to "+2h@h", the token expires at
  the top of the hour, two hours from the current time.
* For more information on relative time identifiers, see "Time Modifiers" in
  the Splunk Enterprise Search Reference Manual.
* The default value indicates that a token never expires. To set token
  expiration, you must set this value to a relative time value.
* Your account must hold the admin role to update this setting.
* This setting is optional.
* Default: never

disabled = <boolean>
* Disables and enables Splunk token authorization.
* Defaults to true.

[capability::accelerate_datamodel]
* Lets a user enable or disable data model acceleration.

[capability::accelerate_search]
* Lets a user enable or disable acceleration for reports.
* The assigned role must also be granted the 'schedule_search' capability.

[capability::run_multi_phased_searches]
* Lets a user in a distributed search environment run searches with
  three or more map-reduce phases.
* Lets users take advantage of the search performance gains
  related to parallel reduce functionality.
* Multi-phased searches can lead to higher resource utilization on
  indexers, but they can also reduce resource utilization on search heads.

[capability::admin_all_objects]
* Lets a user access all objects in the system, such as user objects and
  knowledge objects.
* Lets a user bypass any Access Control List (ACL) restrictions, similar
  to the way root access in a *nix environment does.
* Splunk software checks this capability when accessing manager pages and objects.

[capability::edit_tokens_settings]
* Lets a user access all token auth settings in the system, such as turning the
  the feature on/off and system-wide expiration.
* Splunk checks this capability when accessing manager pages and objects.

[capability::change_authentication]
* Lets a user change authentication settings through the authentication endpoints.
* Lets the user reload authentication.

[capability::change_own_password]
* Lets a user change their own password. You can remove this capability
  to control the password for a user.

[capability::delete_by_keyword]
* Lets a user use the 'delete' command.
* NOTE: The 'delete' command does not actually delete the raw data on disk.
  Instead, it masks the data (via the index) from showing up in search results.

[capability::dispatch_rest_to_indexers]
* Lets a user dispatch the REST search command to indexers.

[capability::edit_deployment_client]
* Lets a user edit the deployment client.
* Lets a user edit a deployment client admin endpoint.

[capability::edit_deployment_server]
* Lets a user edit the deployment server.
* Lets a user edit a deployment server admin endpoint.
* Lets a user change or create remote inputs that are pushed to the
  forwarders and other deployment clients.

[capability::edit_dist_peer]
* Lets a user add and edit peers for distributed search.

[capability::edit_encryption_key_provider]
* Lets a user view and edit keyprovider properties when using
  the Server-Side Encryption (SSE) feature for a remote storage volume.

[capability::request_pstacks]
* Lets a user trigger pstacks generation of the main splunkd process
  using a REST endpoint.

[capability::edit_watchdog]
* Lets a user reconfigure watchdog settings using a REST endpoint.

[capability::edit_forwarders]
* Lets a user edit settings for forwarding data, including settings
  for SSL, backoff schemes, and so on.
* Also used by TCP and Syslog output admin handlers.

[capability::edit_health]
* Lets a user disable or enable health reporting for a feature in the splunkd
  health status tree through the server/health-config/{feature_name} endpoint.

[capability::edit_httpauths]
* Lets a user edit and end user sessions through the httpauth-tokens endpoint.

[capability::edit_indexer_cluster]
* Lets a user edit or manage indexer clusters.

[capability::edit_indexerdiscovery]
* Lets a user edit settings for indexer discovery, including settings
  for master_uri, pass4SymmKey, and so on.
* Also used by Indexer Discovery admin handlers.

[capability::edit_input_defaults]
* Lets a user change the default hostname for input data through the server
  settings endpoint.

[capability::edit_local_apps]
* Lets a user edit apps on the local Splunk instance through the
  local apps endpoint.

[capability::edit_monitor]
* Lets a user add inputs and edit settings for monitoring files.
* Also used by the standard inputs endpoint as well as the oneshot input
  endpoint.

[capability::edit_modinput_winhostmon]
* Lets a user add and edit inputs for monitoring Windows host data.

[capability::edit_modinput_winnetmon]
* Lets a user add and edit inputs for monitoring Windows network data.

[capability::edit_modinput_winprintmon]
* Lets a user add and edit inputs for monitoring Windows printer data.

[capability::edit_modinput_perfmon]
* Lets a user add and edit inputs for monitoring Windows performance.

[capability::edit_modinput_admon]
* Lets a user add and edit inputs for monitoring Active Directory (AD).

[capability::edit_roles]
* Lets a user edit roles.
* Lets a user change the mappings from users to roles.
* Used by both user and role endpoints.

[capability::edit_roles_grantable]
* Lets a user edit roles and change user-to-role mappings for a limited
  set of roles.
* To limit this ability, also assign the 'edit_roles_grantable' capability
  and configure the 'grantableRoles' setting in authorize.conf.
  	* For example:
		grantableRoles = role1;role2;role3
        This configuration lets a user create roles using the subset of
        capabilities that the user has in their 'grantable_roles' setting.

[capability::edit_scripted]
* Lets a user create and edit scripted inputs.

[capability::edit_search_head_clustering]
* Lets a user edit and manage search head clustering.

[capability::edit_search_concurrency_all]
* Lets a user edit settings related to maximum concurrency of searches.

[capability::edit_search_concurrency_scheduled]
* Lets a user edit settings related to concurrency of scheduled searches.

[capability::edit_search_scheduler]
* Lets a user disable and enable the search scheduler.

[capability::edit_search_schedule_priority]
* Lets a user assign a search a higher-than-normal schedule priority.

[capability::edit_search_schedule_window]
* Lets a user edit a search schedule window.

[capability::edit_search_server]
* Lets a user edit general distributed search settings like timeouts,
  heartbeats, and blacklists.

[capability::edit_server]
* Lets a user edit general server and introspection settings, such
  as the server name, log levels, and so on.
* This capability also inherits the ability to read general server
  and introspection settings.

[capability::edit_server_crl]
* Lets a user reload Certificate Revocation Lists (CRLs) within Splunk.
* A CRL is a list of digital certificates that have been revoked by the
  issuing certificate authority (CA) before their scheduled expiration
  date and should no longer be trusted.

[capability::edit_sourcetypes]
* Lets a user create and edit sourcetypes.

[capability::edit_splunktcp]
* Lets a user change settings for receiving TCP input from another Splunk
  instance.

[capability::edit_splunktcp_ssl]
* Lets a user view and edit SSL-specific settings for Splunk TCP input.

[capability::edit_splunktcp_token]
* Lets a user view or edit splunktcptokens. The tokens can be used on a
  receiving system to only accept data from forwarders that have been
  configured with the same token.

[capability::edit_tcp]
* Lets a user change settings for receiving general TCP inputs.

[capability::edit_telemetry_settings]
* Lets a user change settings for opting in and sending telemetry data.

[capability::edit_token_http]
* Lets a user create, edit, display, and remove settings for HTTP token input.
* Enables the HTTP Events Collector feature, which is a way to send data to
  Splunk Enterprise and Splunk Cloud.

[capability::edit_tokens_all]
* Lets a user issue tokens to all users.

[capability::edit_tokens_own]
* Lets a user issue tokens to themself.

[capability::edit_udp]
* Lets a user change settings for UDP inputs.

[capability::edit_user]
* Lets a user create, edit, or remove other users.
* Also lets a user manage certificates for distributed search.
* To limit this ability, assign the 'edit_roles_grantable' capability
  and configure the 'grantableRoles' setting in authorize.conf.
	* Example: grantableRoles = role1;role2;role3

[capability::edit_view_html]
* Lets a user create, edit, or otherwise modify HTML-based views.

[capability::edit_web_settings]
* Lets a user change the settings for web.conf through the system settings
  endpoint.

[capability::export_results_is_visible]
* Lets a user show or hide the Export button in Splunk Web.
* Disable this setting to hide the Export button and prevent users with
  this role from exporting search results.

[capability::get_diag]
* Lets the user generate a diag on a remote instance through the
  /streams/diag endpoint.

[capability::get_metadata]
* Lets a user use the metadata search processor.

[capability::get_typeahead]
* Enables typeahead for a user, both the typeahead endpoint and the
  'typeahead' search processor.

[capability::indexes_edit]
* Lets a user change any index settings such as file size and memory limits.

[capability::input_file]
* Lets a user add a file as an input through the inputcsv command (except for
  dispatch=t mode) and the inputlookup command.

[capability::license_tab]
* Lets a user access and change the license.
* DEPRECATED.
* Replaced with the 'license_edit' capability.

[capability::license_edit]
* Lets a user access and change the license.

[capability::license_view_warnings]
* Lets a user see if they are exceeding limits or reaching the expiration
  date of their license.
* License warnings are displayed on the system banner.

[capability::list_deployment_client]
* Lets a user list the deployment clients.

[capability::list_deployment_server]
* Lets a user list the deployment servers.

[capability::list_pipeline_sets]
* Lets a user list information about pipeline sets.

[capability::list_forwarders]
* Lets a user list settings for data forwarding.
* Used by TCP and Syslog output admin handlers.

[capability::list_health]
* Lets a user monitor the health of various Splunk features
  (such as inputs, outputs, clustering, and so on) through REST endpoints.

[capability::list_httpauths]
* Lets a user list user sessions through the httpauth-tokens endpoint.

[capability::list_indexer_cluster]
* Lets a user list indexer cluster objects such as buckets, peers, and so on.

[capability::list_indexerdiscovery]
* Lets a user view settings for indexer discovery.
* Used by indexer discovery handlers.

[capability::list_inputs]
* Lets a user view the list of inputs including files, TCP, UDP, scripts, and so on.

[capability::list_introspection]
* Lets a user read introspection settings and statistics for indexers, search,
  processors, queues, and so on.

[capability::list_search_head_clustering]
* Lets a user list search head clustering objects such as artifacts, delegated
  jobs, members, captain, and so on.

[capability::list_search_scheduler]
* Lets a user list search scheduler settings.

[capability::list_settings]
* Lets a user list general server and introspection settings such as the server
  name and log levels.

[capability::list_metrics_catalog]
* Lets a user list metrics catalog information such as the metric names,
  dimensions, and dimension values.

[capability::edit_metrics_rollup]
* Lets a user create/edit metrics rollup defined on metric indexes.

[capability::list_storage_passwords]
* Lets a user access the /storage/passwords endpoint.
* Lets the user perform GET operations.
* The 'admin_all_objects' capability must be added to the role in order for the user to
  perform POST operations to the /storage/passwords endpoint.

[capability::list_tokens_all]
* Lets a user view all tokens.

[capability::list_tokens_own]
* Lets a user view their own tokens.

[capability::never_lockout]
* Allows a user's account to never lockout.

[capability::never_expire]
* Allows a user's account to never expire.

[capability::output_file]
* Lets a user create file outputs, including the 'outputcsv' command (except for
  dispatch=t mode) and the 'outputlookup' command.

[capability::request_remote_tok]
* Lets a user get a remote authentication token.
* Used for distributing search to old 4.0.x Splunk instances.
* Also used for some distributed peer management and bundle replication.

[capability::rest_apps_management]
* Lets a user edit settings for entries and categories in the Python remote
  apps handler.
* See restmap.conf.spec for more information.

[capability::rest_apps_view]
* Lets a user list various properties in the Python remote apps handler.
* See restmap.conf.spec for more info

[capability::rest_properties_get]
* Lets a user get information from the services/properties endpoint.

[capability::rest_properties_set]
* Lets a user edit the services/properties endpoint.

[capability::restart_splunkd]
* Lets a user restart Splunk software through the server control handler.

[capability::rtsearch]
* Lets a user run real-time searches.

[capability::run_collect]
* Lets a user run the 'collect' command.

[capability::run_mcollect]
* Lets a user run the 'mcollect' and 'meventcollect' commands.

[capability::run_debug_commands]
* Lets a user run debugging commands, for example 'summarize'.

[capability::schedule_rtsearch]
* Lets a user schedule real-time saved searches.
* You must enable the 'scheduled_search' and 'rtsearch' capabilities for the role.

[capability::schedule_search]
* Lets a user schedule saved searches, create and update alerts, and
  review triggered alert information.

[capability::search]
* Lets a user run a search.

[capability::search_process_config_refresh]
* Lets a user manually flush idle search processes through the
  'refresh search-process-config' CLI command.

[capability::use_file_operator]
* Lets a user use the 'file' command.
* The 'file' command is DEPRECATED.

[capability::upload_lookup_files]
* Lets a user upload files which can be used in conjunction with lookup definitions.

[capability::web_debug]
* Lets a user access /_bump and /debug/** web debug endpoints.

[capability::fsh_manage]
* Lets a user in Splunk platform implementations that have enabled Data
  Fabric Search (DFS) functionality manage the federated search settings.
* With the federated search settings, users with this role can add federated
  providers to federated.conf and manage user access to those federated 
  providers through the maintenance of authentication settings.
* The 'admin' role has this capability enabled by default.

[capability::fsh_search]
* Lets a user in Splunk platform implementations that have enabled Data Fabric
  Search (DFS) functionality run federated searches.
* Lets a user create federated searches in the savedsearches.conf.
* The 'admin' role has this capability enabled by default.

[capability::edit_statsd_transforms]
* Lets a user define regular expressions to extract manipulated dimensions out of
  metric_name fields in statsd metric data using the
  services/data/transforms/statsdextractions endpoint.
* For example, dimensions can be mashed inside a metric_name field like
  "dimension1.metric_name1.dimension2" and you can use regular expressions to extract it.

[capability::edit_metric_schema]
* Lets a user define the schema of the log data that must be converted
  to metric format using the services/data/metric-transforms/schema endpoint.

[capability::list_workload_pools]
* Lets a user list and view workload pool and workload status information through
  the workloads endpoint.

[capability::edit_workload_pools]
* Lets a user create and edit workload pool and workload configuration information
  (except workload rule) through the workloads endpoint.

[capability::select_workload_pools]
* Lets a user select a workload pool for a scheduled or ad-hoc search.

[capability::list_workload_rules]
* Lets a user list and view workload rule information from the workloads/rules
  endpoint.

[capability::edit_workload_rules]
* Lets a user create and edit workload rules through the workloads/rules endpoint.

[capability::apps_restore]
* Lets a user restore configurations from a backup archive through
  the apps/restore endpoint.
