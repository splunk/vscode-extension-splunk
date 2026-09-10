#   Version 10.0.2
#
# This file contains possible setting and value pairs for federated provider entries
# for use when the federated search functionality is enabled.
#
# A federated search lets authorized users run searches across one or more 
# federated providers. A federated provider is a remote data source, such as 
# another Splunk deployment. Each federated provider is defined by a federated 
# provider stanza in federated.conf. A Splunk deployment that runs federated 
# searches can have multiple federated indexes. Each federated index maps to a 
# dataset in a federated provider. You can set up role-based access control for 
# each federated index, just as you do for regular indexes. Federated indexes 
# are defined by stanzas in indexes.conf.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles
#

#
# Federated Provider Stanza
#
[provider]
* Each federated provider definition must have a separate stanza.
* <provider> must follow the following syntax: 
  provider://<unique-federated-provider-name>
* <unique-federated-provider-name> can contain only alphanumeric characters and 
  underscores.

type = [splunk]
* Specifies the type of the federated provider.
* A setting of 'splunk' means that the federated provider is a Splunk
  deployment.
* Default: splunk

hostPort = <Host_Name_or_IP_Address>:<service_port>
* Specifies the protocols required to connect to a federated provider.
* You can provide a host name or an IP address.
* The <service_port> can be any legitimate port number.
* No default.

serviceAccount = <user_name>
* Specifies the user name for a service account that has been set up on the
  federated provider for the purpose of enabling secure federated search.
* This service account allows the federated search head on your local Splunk
  platform deployment to query datasets on the federated provider in a secure
  manner.
* No default.

password = <password>
* Specifies the service account password for the user specified in the
  'serviceAccount' setting.
* No default.

appContext = <application_short_name>
* Specifies the Splunk application context for the federated searches that are
  run with this federated provider definition.
* NOTE: Applicable only to federated providers that have 'type = splunk' and
 'mode = standard'.
  * Federated providers with 'type = splunk' and 'mode = transparent' ignore
    the 'appContext' property. Such providers instead apply the application
    context of the federated search that is run from the local search head to
    the remote portion of the federated search that is run on the remote
    search head.
* Provision of an application context ensures that federated searches which use
  the federated provider are limited to the knowledge objects that are
  associated with the named application. Application context can also affect
  search job quota and resource allocation parameters.
* '<application_short_name>' must be the short name of a Splunk application
  currently installed on the federated provider. For example, the short name of
  Splunk IT Service Intelligence is 'itsi'.
  * Find the short names of apps installed on a Splunk deployment by going to
    'Apps > Manage Apps' and reviewing the values in the 'Folder name' column.
* You can create multiple federated provider definitions with 'type = splunk'
  and 'mode = standard' for the same remote search head that differ only by
  name and application context.
* Default: search

useFSHKnowledgeObjects = <boolean>
* Determines whether federated searches with this provider use knowledge
  objects from the federated provider (the remote search head) or from the
  federated search head (the local search head).
* When set to 'true' federated searches with this provider use knowledge
  objects from the federated search head.
* NOTE: This setting can be set to "true" only when the federated provider is in
  transparent mode. If this setting is set to "true" on a standard mode
  provider, the Splunk software considers the provider to be misconfigured and 
  ignores this setting when you run searches on it. So Splunk software always
  uses knowledge objects from the federated provider in standard mode.
* Default: false

mode = [ standard | transparent ]
* Specifies whether a federated provider is in standard or transparent mode.
* A setting of 'transparent' means that searches with the federated provider
  can use only knowledge objects from the federated search head. In other
  words, the value for 'useFSHKnowledgeObjects' is always interpreted by the
  transparent mode federated provider as 'true'.
* A setting of 'standard' means that the federated provider respects the
  setting of 'useFSHKnowledgeObjects'. In other words, searches with the
  federated provider can use knowledge objects from the remote search head or
  the federated search head.
* Default: standard


#
# General Federated Search Stanza
#
[general]
* This stanza is for settings that are applicable to the overall logic for
  search federation. They are typically applicable to all federated providers
  and all search head cluster members.

needs_consent = <boolean>
* A setting of 'true' causes a checkbox to appear in the federated provider
  definition UI. This checkbox requires that users legally acknowledge that
  federated providers can be set up in a manner detrimental to regulatory
  compliance.
* Default: true

heartbeatEnabled = <boolean>
* Specifies whether the federated search heartbeat mechanism is running.
* A setting of 'true' means the heartbeat mechanism is running on an interval
  specified by 'heartbeatInterval'.
* The heartbeat mechanism monitors the remote federated providers for this
  Splunk platform instance. When you run federated searches and the heartbeat
  mechanism has detected problems with the federated providers, it can tell you
  what is wrong and take actions.
  * If a federated provider is found to be unreachable a consecutive number of
    times set by 'connectivityFailuresThreshold', the heartbeat mechanism sets
    the federated provider to an invalid state, meaning it ignores the
    unreachable provider in federated searches.
      * When the heartbeat mechanism reconnects to the provider, it resets the
        provider to a valid state.
  * If two transparent mode federated providers are found to point to the same
    server ID, the heartbeat mechanism randomly chooses one provider to run the
    search over.
    * On Splunk Enterprise deployments, this functionality is extended so that
      it also detects when two transparent mode federated providers share the
      same cluster ID. For this extension to work, the service accounts for the
      transparent mode federated providers must have the
      list_search_head_clustering capability.
* A setting of 'false' means the heartbeat mechanism does not take actions when
  it detects problems with providers.
* NOTE: Do not change this setting unless instructed to do so by Splunk
  Support.
* Default: true

heartbeatInterval = <integer>
* The interval, in seconds, of the federated search heartbeat mechanism.
  It's value should be greater than 5 seconds.
* When 'heartbeatEnabled = true' the federated search heartbeat mechanism
  performs its federated provider monitoring activities on this interval.
* NOTE: Do not change this setting unless instructed to do so by Splunk
  Support.
* Default: 60

connectivityFailuresThreshold = <integer>
* When the federated search heartbeat mechanism detects this number of
  consecutive connectivity failures for a specific remote provider, the
  heartbeat mechanism sets the remote provider to an invalid state.
* When the heartbeat mechanism successfully reconnects to an invalid state
  federated provider, it resets the federated provider to a valid state.
* NOTE: Do not change this setting unless instructed to do so by Splunk
  Support.
* Default: 3

controlCommandsMaxThreads = <int>
* The maximum number of threads that can run a federated search action, such as 
  a search pause or search cancellation, from a local federated search head on 
  the federated providers.
* Change this setting only when directed to do so by Splunk Support.
* Default: 5

controlCommandsMaxTimeThreshold = <int>
* The maximum number of seconds that a federated search action, such as
  a search pause or search cancellation, from a local federated search head waits
  for the federated providers to finish the same command.
* Change this setting only when directed to do so by Splunk Support.
* Default: 5

controlCommandsFeatureEnabled = <boolean>
* Specifies whether a federated search head can send a federated search action,
  such as a search pause or search cancellation, to federated providers.
* Change this setting only when directed to do so by Splunk Support.
* Default: true

allowLookupsToExistOnlyOnRshForStandardMode = <boolean>
* Specifies where lookups can exist for standard mode federated searches.
* When set to 'false', each lookup must be locally defined on the federated
  search head and remotely defined on the remote search head.
* When set to 'true', each lookup must be remotely defined on the remote search
  head.
* Change this setting only when directed to do so by Splunk Support.
* Default: true

allowedAndDefaultFederatedProvidersEnabled = <boolean>
* Specifies whether the RBAC for transparent mode federated providers that is 
  defined by 'srchFederatedProvidersAllowed' and 
  'srchFederatedProvidersDefault' in authorize.conf is applied to federated 
  searches run by users on this Splunk platform deployment.
* When set to 'true', those settings are applied to all federated searches for 
  all roles.
* Change this setting only when directed to do so by Splunk Support.
* Default: true

allowAstProjectionElim = <boolean>
* Controls whether Splunk software enables projection elimination
  optimization on the federated search head.
* A value of "true" means that Splunk software enables projection
  elimination optimization.
* A value of "false" means that Splunk software does not enable
  projection elimination optimization.
* For more information, search for 'search_optimization::projection_elimination'
  in the limits.conf.spec file.
* CAUTION: Change this setting only when Splunk Support directs you to do so.
* Default: false

allowAstPredicateMerge = <boolean>
* Controls whether Splunk software enables predicate merge optimization
  on the federated search head.
* A value of "true" means that Splunk software enables predicate merge
  optimization.
* A value of "false" means that Splunk software does not enable predicate
  merge optimization.
* For more information, search for 'search_optimization::predicate_merge'
  in the limits.conf.spec file.
* CAUTION: Change this setting only when Splunk Support directs you to do so.
* Default: false

allowAstInsertRedistributeCommand = <boolean>
* Controls whether Splunk software enables a search language optimization
  that inserts a 'redistribute' command on the federated search head.
* A value of "true" means that Splunk software enables this optimization.
* A value of "false" means that Splunk software does not enable this
  optimization.
* For more information, search for 
  'search_optimization::insert_redistribute_command' in the limits.conf.spec 
  file.
* CAUTION: Change this setting only when Splunk Support directs you to do so.
* Default: false

allowAstReplaceChartCmdsWithTstats = <boolean>
* Controls whether Splunk software enables chart replacement with 'tstats'
  optimization on the federated search head.
* A value of "true" means that Splunk software enables this optimization.
* A value of "false" means that Splunk software does not enable this
  optimization.
* For more information, search for 
  'search_optimization::replace_chart_cmds_with_tstats' in the 
  limits.conf.spec file.
* CAUTION: Change this setting only when Splunk Support directs you to do so.
* Default: false

allowAstReplaceDatamodelStatsCmdsWithTstats = <boolean>
* Controls whether Splunk software enables a search language optimization
  that replaces 'stats' commands with 'tstats' commands in '| datamodel ..
  | stats' and '| from datamodel .. | stats' Search Processing Language
  (SPL) strings.
* A value of "true" means that Splunk software enables this optimization.
* A value of "false" means that Splunk software does not enable this
  optimization.
* For more information, search for 
  'search_optimization::replace_datamodel_stats_cmds_with_tstats' in the 
  limits.conf.spec file.
* CAUTION: Change this setting only when Splunk Support directs you to do so.
* Default: false

allowAstReplaceTableWithFields = <boolean>
* Controls whether Splunk software enables a search language optimization
  that replaces the 'table' command with the 'fields' command on the federated 
  search head.
* A value of "true" means that Splunk software enables this optimization.
* A value of "false" means that Splunk software does not enable this
  optimization.
* For more information, search for 
  'search_optimization::replace_table_with_fields' in the 'limits.conf.spec' 
  file.
* CAUTION: Change this setting only when Splunk Support directs you to do so.
* Default: false

allowAstReplaceSdselectWithSdsql = <boolean>
* Controls whether Splunk software enables the substitution of the
  'sdselect' command with 'sdsql' on the federated search head.
* A value of "true" means that Splunk software enables this substitution.
* A value of "false" means that Splunk software does not enable this
  substitution.
* CAUTION: Change this setting only when Splunk Support directs you to do so.
* Default: false

previewOnRshEnabled = <boolean>
* Specifies whether search preview is activated on remote search heads when 
  they process federated searches.
* A setting of 'false' means different things depending on whether a search 
  head is acting as a local federated search head (FSH) or a remote search head 
  (RSH). A search head can simultaneously be an FSH and an RSH.
  * On an FSH, when 'previewOnRshEnabled=false', the FSH sends federated 
    searches to federated search heads with 'preview=false', meaning that 
    search preview is deactivated for the search on the remote search heads.
  * On an RSH, when 'previewOnRshEnabled=false', if the RSH detects that an 
    incoming federated search has 'preview=auto', it deactivates preview on the 
    RSH.
  * Note: This setting does not affect federated search previews on the 
    federated search head that initiates the search. 
* For federated searches, previews on the remote search head serve no purpose, 
  as results are viewed through the UI of the federated search head on your 
  local Splunk platform deployment. 
* Deactivating search preview on the remote search head can improve the overall 
  efficiency of long-running high cardinality federated searches.
* Change this setting only when directed to do so by Splunk Support.
* Default: false

proxyBundlesTTL = <int>
* Specifies the time to live in seconds of a proxy bundle on the remote search 
  head after the last time it was used for a search.
* Change this setting only when directed to do so by Splunk Support.
* Default: 172800

remoteEventsDownloadRetryCountMax = <integer>
* When you run a verbose-mode federated search, the federated search head 
  downloads events from the federated provider. 
* If this event download fails, the federated search head retries the download.
* This setting sets the maximum number of event download retries that the 
  federated search head can make before it reports a failure.
* See 'remoteEventsDownloadRetryTimeoutMs' for the interval between retries.
* Change this setting only when directed to do so by Splunk Support.
* Default: 20

remoteEventsDownloadRetryTimeoutMs = <int>
* Specifies the interval, in milliseconds, between retries of a failed event 
  download from a federated provider. 
* See 'remoteEventsDownloadRetryCountMax' for the total number of event 
  download retries a federated search head can make before it must report a 
  failure.
* Change this setting only when directed to do so by Splunk Support.
* Default: 1000

verbose_mode = <boolean>
* Specifies whether federated searches can be run in verbose mode. 
* A setting of 'false' restricts the ability of federated searches to run in 
  verbose mode, while allowing federated searches to run in fast and smart 
  mode.  
* In Transparent Mode, a setting of 'false' means that Splunk software runs 
  only the local portion of a verbose mode federated search.
* In Standard Mode, a setting of 'false' terminates verbose mode federated 
  searches without displaying their results.  
* NOTE: Do not change this setting unless instructed to do so by Splunk Support.
* Default: true

enable_streaming_optimization = <boolean>
* Controls whether federated searches use pure streaming optimization.
* A value of "false" means that federated searches do not use pure streaming
  optimization. A federated search gets all matching events from the remote
  search head and builds the timeline from these events.
* A value of "true" means that if a search is a pure streaming search, Splunk
  software optimizes the search to send just enough data to display events
  and the timeline in the user interface.
* This setting needs to be enabled only on federated search heads. Remote
  search heads follow instructions from federated search heads.
* NOTE: Do not change this setting unless Splunk Support instructs you to do so.
* Default: false

max_preview_generation_duration = <unsigned integer>
* The maximum amount of time, in seconds, that the search head can spend to 
  generate search result previews.
* NOTE: This setting applies only to Splunk-to-Splunk federated searches.
* This limit does not stop federated searches from completing and returning 
  final result sets. 
* When this limit is reached by a federated search, preview generation is 
  halted, but the search continues gathering results until it completes and 
  displays the final result set.
* Change the value of this setting to a number above zero if you find that your 
  federated searches are being terminated because their preview generation 
  duration exceeds a timeout set by another component in your network, such as 
  an elastic load balancer (ELB). 
  * For example, if you have an ELB that times out at 60 seconds, you might set 
    the 'max_preview_generation_duration' to "55". Additionally, set
    'max_preview_generation_inputcount' to "500000".
* A setting of "0" means that the preview generation duration of federated 
  searches is unlimited. 
* Default: 0

max_preview_generation_inputcount = <unsigned integer>
* The maximum number of input result rows that the search head can use to
  generate search result previews.
* NOTE: This setting applies only to Splunk-to-Splunk federated searches.
* This limit does not stop federated searches from completing and returning 
  final result sets. 
* When a federated search reaches this limit, preview generation 
  processes only the first number of rows specified by the
  'max_preview_generation_inputcount' setting in order to generate the 
  preview results.
* Change the value of this setting to a number above zero if your 
  federated searches are being terminated because their preview generation 
  duration exceeds a timeout set by another component in your network, such as 
  an elastic load balancer (ELB). 
  * For example, if you have an ELB that times out at 60 seconds, you might set 
    the 'max_preview_generation_duration' to "55". Additionally, set
    'max_preview_generation_inputcount' to "500000".
* A setting of "0" means that the preview generation input count of federated 
  searches is unlimited. 
* Default: 0

federated_search_remote_ttl = <unsigned integer>
* The amount of time, in seconds, that Splunk software stores artifacts from
  federated searches on the remote search head after those searches complete.
* Default: 600 (10 minutes)

s2s_standard_mode_local_only_commands = <comma-separated list>
* Specifies search processing language (SPL) commands that, in standard mode
  federated searches, must be processed only on the local search head, and not
  on the remote search head.
  * When a command on this list is used in a standard mode federated search,
    the command and all the commands that follow it in the search string are
    processed only on the local search head.
* Change this setting only when instructed to do so by Splunk Support.
* Default: mcollect, outputlookup, sendalert, sendemail

############################################################################
# Configs for blocking unsupported commands in Federated Search
############################################################################

# Change this setting only when instructed to do so by Splunk Support.
[s2s_standard_mode_unsupported_command:metadata]
* This stanza controls whether the metadata command is blocked for 
  Federated Search for Splunk on standard mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'metadata' command for standard mode 
  federated search.
  * A value of "true" means that the 'metadata' command is not blocked for 
    standard mode federated search.
  * A value of "false" means that the 'metadata' command is blocked for 
    standard mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_standard_mode_unsupported_command:metasearch]
* This stanza controls whether the metasearch command is blocked for 
  Federated Search for Splunk on standard mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'metasearch' command for standard mode 
  federated search.
  * A value of "true" means that the 'metasearch' command is not blocked for 
    standard mode federated search.
  * A value of "false" means that the 'metasearch' command is blocked for 
    standard mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:makeresults]
* This stanza controls whether Splunk software blocks the 'makeresults' command 
  on transparent mode federated providers for Federated Search for Splunk.

active = <boolean>
* Controls whether Splunk software blocks the 'makeresults' command for 
  transparent mode federated search.
  * A value of "true" means that Splunk software does not block the 
    'makeresults' command for transparent mode federated search.
  * A value of "false" means that Splunk software blocks the 'makeresults' 
    command for transparent mode federated search. The 'makeresults' command 
    still runs on your local search head.
* Even when 'active=false', you can run a 'makeresults' search over a 
  transparent mode federated provider when the following things are true:
  * The 'allow_target' setting is set to 'true' and you use the 'splunk_server' 
    or 'splunk_server_group' arguments in conjunction with the 'makeresults' 
    command. 
  * The 'splunk_server' or 'splunk_server_group' arguments point to a server or 
    server group that exists on the transparent mode federated provider.
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

allow_target = <boolean>
* Determines whether you can run the 'makeresults' command over transparent 
  mode federated providers with the 'splunk_server' or 'splunk_server_group' 
  arguments even when 'active = false'.
  * A value of "true" means that you can run the specified command over 
    transparent mode federated providers when you use the 'splunk_server' or 
    'splunk_server_group' argument in conjunction with the command. 
    * If you do not specify a server or server group that exists on the the 
      transparent mode federated provider, Splunk software blocks 'makeresults' 
      for transparent mode federated search, and runs only on your local search 
      head.
  * A value of "false" means that you cannot run 'makeresults' over transparent 
    mode federated providers even when you use the 'splunk_server' or 
   'splunk_server_group' arguments to specify servers or server groups that 
   exist on the transparent mode provider.  
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: true

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:delete]
* This stanza controls whether the delete command is blocked for 
  Federated Search for Splunk on transparent mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'delete' command for transparent mode 
  federated search.
  * A value of "true" means that the 'delete' command is not blocked for 
    transparent mode federated search.
  * A value of "false" means that the 'delete' command is blocked for 
    transparent mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:dump]
* This stanza controls whether the dump command is blocked for 
  Federated Search for Splunk on transparent mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'dump' command for transparent mode 
  federated search.
  * A value of "true" means that the 'dump' command is not blocked for 
    transparent mode federated search.
  * A value of "false" means that the 'dump' command is blocked for 
    transparent mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:map]
* This stanza controls whether the map command is blocked for 
  Federated Search for Splunk on transparent mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'map' command for transparent mode 
  federated search.
  * A value of "true" means that the 'map' command is not blocked for 
    transparent mode federated search.
  * A value of "false" means that the 'map' command is blocked for 
    transparent mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:run]
* This stanza controls whether the run command is blocked for 
  Federated Search for Splunk on transparent mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'run' command for transparent mode 
  federated search.
  * A value of "true" means that the 'run' command is not blocked for 
    transparent mode federated search.
  * A value of "false" means that the 'run' command is blocked for 
    transparent mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:runshellscript]
* This stanza controls whether the runshellscript command is blocked for 
  Federated Search for Splunk on transparent mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'runshellscript' command for transparent mode 
  federated search.
  * A value of "true" means that the 'runshellscript' command is not blocked for 
    transparent mode federated search.
  * A value of "false" means that the 'runshellscript' command is blocked for 
    transparent mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:script]
* This stanza controls whether the script command is blocked for 
  Federated Search for Splunk on transparent mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'script' command for transparent mode 
  federated search.
  * A value of "true" means that the 'script' command is not blocked for 
    transparent mode federated search.
  * A value of "false" means that the 'script' command is blocked for 
    transparent mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:sendalert]
* This stanza controls whether the sendalert command is blocked for 
  Federated Search for Splunk on transparent mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'sendalert' command for transparent mode 
  federated search.
  * A value of "true" means that the 'sendalert' command is not blocked for 
    transparent mode federated search.
  * A value of "false" means that the 'sendalert' command is blocked for 
    transparent mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:sendemail]
* This stanza controls whether the sendemail command is blocked for 
  Federated Search for Splunk on transparent mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'sendemail' command for transparent mode 
  federated search.
  * A value of "true" means that the 'sendemail' command is not blocked for 
    transparent mode federated search.
  * A value of "false" means that the 'sendemail' command is blocked for 
    transparent mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change this setting only when instructed to do so by Splunk Support.
[s2s_transparent_mode_unsupported_command:rest]
* This stanza controls whether the rest command is blocked for 
  Federated Search for Splunk on transparent mode federated providers.

active = <boolean>
* Whether Splunk software blocks the 'rest' command for transparent mode 
  federated search.
  * A value of "true" means that the 'rest' command is not blocked for 
    transparent mode federated search.
  * A value of "false" means that the 'rest' command is blocked for 
    transparent mode federated search. 
* NOTE: Do not change this setting unless instructed to do so by Splunk 
  Support. 
* Default: false

# Change the settings in this stanza only when Splunk Support instructs you to 
# do so.
[s2s_transparent_mode_unsupported_command:summarize]
* This stanza controls whether Splunk software blocks the 'summarize' command
  on transparent mode federated providers for Federated Search for Splunk.
* Note: The 'summarize' command is an internal command. Use it only under the 
  direction of Splunk Support. 

active = <boolean>
* Controls whether Splunk software blocks the 'summarize' command for
  transparent mode federated search.
  * A value of "true" means that Splunk software does not block the
    'summarize' command for transparent mode federated search.
  * A value of "false" means that Splunk software blocks the 'summarize'
    command for transparent mode federated search. The 'summarize' command
    still runs on your local search head.
* Transparent mode federated providers with lower versions encounter  
  complications when they run the 'summarize' command. For those providers, the 
  command must always be blocked. The 'rsh_min_version_cloud' and 
  'rsh_version_onprem' settings ensure that 'summarize' is blocked for 
  transparent mode federated providers that have versions lower than the 
  versions those settings specify, even when 'active=true'. 
* Default: true

rsh_min_version_cloud = <string>
* Specifies the minimal Splunk Cloud Platform version with full support for 
  'summarize'. 
* Affects only transparent mode federated providers.
* This setting blocks 'summarize' for any Splunk Cloud Platform transparent 
  mode federated provider with a version lower than this setting.
* Default: 9.0.2303.100

rsh_min_version_onprem = <string>
* Specifies the minimal Splunk Enterprise version with full support for 
  'summarize'. 
* Affects only transparent mode federated providers.
* This setting blocks 'summarize' for any Splunk Enterprise transparent mode 
  federated provider with a version lower than this setting.
* Default: 9.1.0

# Change the settings in this stanza only when Splunk Support instructs you to 
# do so.
[s2s_transparent_mode_unsupported_command:tstats]
* This stanza controls whether Splunk software blocks the 'tstats' command
  on transparent mode federated providers for Federated Search for Splunk.

active = <boolean>
* Controls whether Splunk software blocks the 'tstats' command for
  transparent mode federated search.
  * A value of "true" means that Splunk software does not block the
    'tstats' command for transparent mode federated search.
  * A value of "false" means that Splunk software blocks the 'tstats'
    command for transparent mode federated search. The 'tstats' command
    still runs on your local search head.
* Under certain conditions, transparent mode federated providers with lower 
  versions encounter complications when they run the 'tstats' command.
  * The 'rsh_min_version_cloud' and 'rsh_version_onprem' settings block 
    'tstats' searches that inlude 'FROM' clauses for transparent mode
    federated providers that have versions lower than the versions the
    'rsh_min_version_cloud' and 'rsh_version_onprem' settings specify,
    even when 'active=true'.
  * However, if a 'tstats' search on a lower-version transparent mode federated 
    provider does not include a 'FROM' clause, Splunk software ignores the 
    'rsh_min_version_cloud' and 'rsh_version_onprem' settings and allows the 
    'tstats' search to proceed.
* Default: true

rsh_min_version_cloud = <string>
* Specifies the minimal Splunk Cloud Platform version with full support for 
  'tstats'.
* Affects only transparent mode federated providers.
* This setting blocks 'tstats' for any Splunk Cloud Platform transparent mode 
  federated provider with a version lower than this setting, when the 'tstats' 
  search includes a 'FROM' clause.
* Default: 9.0.2303.100

rsh_min_version_onprem = <string>
* Specifies the minimal Splunk Enterprise version with full support for 
  'tstats'.
* Affects only transparent mode federated providers.
* This setting blocks 'tstats' for any Splunk Enterprise transparent mode 
  federated provider with a version lower than this setting, when the 'tstats' 
  search includes a 'FROM' clause.
* Default: 9.1.0


[s2s_unsupported_command:show_source]
* This stanza controls whether Splunk software blocks the Show Source feature
  on federated providers for Federated Search for Splunk.

rsh_min_version_cloud = <string>
* Specifies the minimal Splunk Cloud Platform version with full support for
  Show Source in federated searches.
* This setting blocks sending Show Source requests for any Splunk Cloud Platform
  federated provider with a version lower than this setting.
* Default: 10.0.2503.100


rsh_min_version_onprem = <string>
* Specifies the minimal Splunk Enterprise version with full support for
  Show Source in federated searches.
* This setting blocks sending Show Source requests for any Splunk Enterprise
  federated provider with a version lower than this setting.
* Default: 10.0.0
