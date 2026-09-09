#   Version 10.2.3
#
# This file contains possible attributes and values for defining server
# classes to which deployment clients can belong. These attributes and
# values specify what content a given server class member will receive from
# the deployment server.
#
# For examples, see serverclass.conf.example. You must reload the deployment
# server configuration ("splunk reload deploy-server"), or restart splunkd,
# for changes to this file to take effect.
#
# To learn more about configuration files, including file precedence, search
# for "About configuration files" in the Admin Manual in the Splunk Docs.



#***************************************************************************
# Configure the server classes used by a deployment server instance.
#
# Server classes are essentially categories. They use filters to control
# what clients they apply to, contain a set of applications, and might define
# deployment server behavior for the management of those applications. The
# filters can be based on DNS name, IP address, build number of client
# machines, platform, and the clientName. If a target machine
# matches the filter, then the deployment server deploys the apps and configuration
# content that make up the server class to that machine.

# Property inheritance
#
# Stanzas in serverclass.conf go from general to more specific, in the
# following order:
# [global] -> [serverClass:<name>] -> [serverClass:<scname>:app:<appname>]
#
# Some properties defined in the [global] stanza can be
# overridden by a more specific stanza as it applies to them. If a global
# setting can be overridden, the description says so.

#***************************************************************************
# Understanding the three-level hierarchy
#
# The serverclass.conf file uses a three-level hierarchy. Each level serves
# a distinct purpose in agent matching and filtering.
#
# Level 1: [global] stanza
# * Acts as a template only. This stanza does not perform agent matching.
# * Provides default values that all [serverClass:<name>] stanzas inherit.
# * Allows any setting to be overridden by child stanzas.
# * Use this level for serverclass-wide defaults.
#
# Level 2: [serverClass:<name>] stanza
# * Performs primary agent matching.
# * Inherits all settings from [global]. Child stanzas can override these
#   settings.
# * Determines which agents belong to this server class.
# * If an agent does not match at this level, it receives no apps from
#   this server class, regardless of app-level filters.
#
# Level 3: [serverClass:<name>:app:<appName>] stanza
# * Performs secondary filtering within the server class scope.
# * Inherits settings from the parent [serverClass:<name>] stanza.
# * Cannot add agents beyond those matched by the parent
#   server class.
# * Can only further restrict which agents receive this specific app.
#
# Matching flow: The [global] stanza sets defaults. The [serverClass:<name>]
# stanza performs primary matching. The app stanza performs secondary
# filtering within the matched agent set.
#***************************************************************************


###########################################
########### FIRST LEVEL: global ###########
###########################################

# Global stanza that defines properties for all server classes.
[global]
# Caution: The [global] stanza is the only supported global configuration
# stanza. Do not use [default] as a stanza name in serverclass.conf, even
# though it may be used in other Splunk configuration files. Using [default]
# results in an error message and incorrect matching behavior.

disabled = <boolean>
* Determines whether the deployment server is active.
* A value of "true" means the deployment server is inactive and does not 
  process server class configurations or deploy content.
* A value of "false" means the deployment server operates normally.
* Default: false

crossServerChecksum = <boolean>
* Determines whether the deployment server ensures consistent app checksums
  across multiple deployment servers.
* A value of "true" means the deployment server generates the same checksum
  for each app across different deployment servers. This setting is useful
  if you have multiple deployment servers behind a load balancer.
* A value of "false" means each deployment server generates its own checksum
  independently.
* Default: false

excludeFromUpdate = <comma-separated list>
* Specifies paths to one or more top-level files or directories, and their
  contents, to exclude from being touched during app updates.
* After removing a path from the list, you must update or touch at least
  one of the app files so that the deployment server deploys
  a new app version to the deployment client.
* Prefix each comma-separated entry by "$app_root$/"
  to avoid warning messages.
* You can override this setting at the serverClass level.
* You can override this setting at the app level.
* Requires version 6.2.x or higher for both the deployment server and
  deployment client.
* No default.

repositoryLocation = <path>
* The path to the repository of applications on the deployment server
  machine.
* You can override this setting at the serverClass level.
* Default: $SPLUNK_HOME/etc/deployment-apps

syncMode = none | sharedDir
* Specifies whether deployment apps are shared across multiple deployment
  servers.
* A value of "none" means the set of deployment apps are specific to
  this deployment server only and are not shared with any other
  deployment servers.
* A value of "sharedDir" means multiple deployment servers share the same
  deployment app directory and sync app bundles and serverclass.conf.
* Each deployment server specifies its app directory with the
  'repositoryLocation' setting.
* When the deployment server reloads, either through manual intervention
  using CLI or the REST endpoint or automatically in response to the 
  forwarder management interface, the deployment server updates the
  "_splunk_ds_info/_metadata" file in the shared deployment server app
  directory. The other deployment servers that share the directory
  periodically check that file to determine whether they must run a
  reload.
* Default: none

maxConcurrentDownloads = <positive integer>
* The maximum number of deployment clients that can simultaneously download
  the bundle from the deployment server.
* If a deployment client fails to download the bundle because of this
  setting, it retries the bundle download on the next phonehome until
  it successfully downloads the bundle.
* A value of "0" means there is no limit to the number of deployment
  clients that can simultaneously download.
* Default: 0

reloadCheckInterval = <integer>
* The interval, in seconds, between reload checks, where a deployment
  server determines whether it must run a reload to sync its
  configurations.
* This setting only applies when 'syncMode' has a value of "sharedDir".
* Default: 60

targetRepositoryLocation = <path>
* The path to the location on the deployment client where the deployment
  server installs the apps.
* If you leave this value unset or empty, the deployment server uses the
  'repositoryLocation' path instead.
* You can override this setting at the [serverClass:<name>] level.
* This setting is useful only with complex deployment strategies, for
  example, tiered deployment strategies.
* Default: $SPLUNK_HOME/etc/apps, the live
  configuration directory for a Splunk Enterprise instance.

tmpFolder = <path>
* The path to the working folder used by the deployment server.
* Default: $SPLUNK_HOME/var/run/tmp

continueMatching = <boolean>
* Controls how configuration is layered across classes and
  server-specific settings.
* A value of "true" means configuration lookups continue matching server
  classes, beyond the first match.
* A value of "false" means only the first match is used.
* Matching is done in the order in which server classes are defined.
* A serverClass can override this setting and stop the matching.
* You can override this setting at the serverClass level.
* Default: true

endpoint = <URL template string>
* The endpoint from which a deployment client can download content.
* The deployment client knows how to substitute values for variables in
  the Uniform Resource Locator (URL).
* You can supply any custom URL here, as long as it uses the specified
  variables.
* You do not need to specify this setting unless you have a very specific
  need, for example, to acquire deployment application files from a
  third-party web server for extremely large environments.
* You can override this setting at the serverClass level.
* Default: $deploymentServerUri$/services/streams/deployment
  ?name=$tenantName$:$serverClassName$:$appName$

filterType = whitelist|blacklist
* A value of "whitelist" indicates a filtering strategy that pulls in a
  subset:
  * Items are considered to not match the stanza by default.
  * Items that match any whitelist entry, and do not match any blacklist
    entry, are considered to match the stanza.
  * Items that match any blacklist entry are not considered to match the
    stanza, regardless of whitelist.
* A value of "blacklist" indicates a filtering strategy that rules out a
  subset:
  * Items are considered to match the stanza by default.
  * Items that match any blacklist entry, and do not match any whitelist
    entry, are considered to not match the stanza.
  * Items that match any whitelist entry are considered to match the
    stanza.
* In brief:
  * whitelist: default no-match
  * blacklist: default match
* You can override this setting at the serverClass level and the
  serverClass:app level.
* Default: whitelist
* Caution: Starting from Splunk Enterprise version 9.4.3, the implicit
  default value for 'filterType' at the app level changed from "blacklist"
  to "whitelist". This change affects matching behavior when 'filterType'
  is not explicitly set at the app level. See the examples below for
  migration guidance.
* The 'filterType' setting is inherited between configuration levels. If
  you set 'filterType' at the [global] level, it applies to serverClass
  and app levels unless explicitly overridden.

# filterType behavior truth tables

# When filterType = whitelist (Default-Deny):
#   | Blacklist match | Whitelist match | Agent matched |
#   |-----------------|-----------------|---------------|
#   | No              | No              | No            |
#   | Yes             | No              | No            |
#   | No              | Yes             | Yes           |
#   | Yes             | Yes             | No            |
#
#   Rule: Agent must be whitelisted and not blacklisted
#   Formula: (agent in whitelist) and (agent not in blacklist)

# When filterType = blacklist (Default-Allow):
#   | Blacklist match | Whitelist match | Agent matched |
#   |-----------------|-----------------|---------------|
#   | No              | No              | Yes           |
#   | Yes             | No              | No            |
#   | No              | Yes             | Yes           |
#   | Yes             | Yes             | Yes           |
#
#   Rule: Matches all agents unless blacklisted
#   Formula: (agent in whitelist) or (agent not in blacklist)

# Key differences between the tables:
# * Row 1 (neither matched): whitelist mode denies, blacklist mode allows
# * Row 4 (both matched): whitelist mode denies, blacklist mode allows

whitelist.<n> = <clientName> | <IP address> | <hostname> | <instanceId>
blacklist.<n> = <clientName> | <IP address> | <hostname> | <instanceId>
* 'n' is an unsigned integer. The sequence can start at any value and can
  be non-consecutive.
* The value of this setting is matched against several items in order:
    * Any clientName specified by the client in its deploymentclient.conf file
    * The IP address of the connected client
    * The hostname of the connected client, as provided by reverse DNS lookup
    * The hostname of the client, as provided by the client
    * For Splunk Enterprise version later than 6.4, the instanceId of the client.
      This is a GUID string, for example: 'ffe9fe01-a4fb-425e-9f63-56cc274d7f8b'.
* All of these can be used with wildcards. The asterisk character (*) matches
  any sequence of characters. For example:
    * Match a network range: 10.1.1.*
    * Match a domain: *.splunk.com
* You can override this setting at the serverClass level and the
  serverClass:app level.
* By default, there are no whitelist or blacklist entries.
* These patterns are PCRE regular expressions, with the following aids for
  easier entry:
    * You can specify '.' to mean '\.'
    * You can specify '*' to mean '.*'
* Matches are always case-insensitive; you do not need to specify the '(?i)' prefix.

# Example with filterType=whitelist:
#     whitelist.0=*.splunk.com
#     blacklist.0=printer.splunk.com
#     blacklist.1=scanner.splunk.com
# This causes all hosts in splunk.com, except 'printer' and 'scanner', to
# match this server class.

# Example with filterType=blacklist:
#     blacklist.0=*
#     whitelist.0=*.web.splunk.com
#     whitelist.1=*.linux.splunk.com
# This causes only the 'web' and 'linux' hosts to match the server class.
# No other hosts match.

# You can also use deployment client machine types (hardware type of host
# machines) to match deployment clients.
# This filter is used only if match of a client could not be decided using
# the whitelist/blacklist filters. The value of each machine type is
# designated by the hardware platform itself; a few common ones are:
#   linux-x86_64, windows-intel, linux-i686, freebsd-i386,
    darwin-i386, sunos-sun4u.
# The method for finding it varies by platform; once a deployment client is
# connected to the deployment server, however, you can determine the value of a
# deployment client's machine type with this Splunk CLI command on the
# deployment server:
#       ./splunk list deploy-clients
# The "utsname" values in the output are the respective deployment
# clients' machine types.

# Note: Atomic override behavior for whitelist/blacklist

# When you override one filter type (whitelist or blacklist) at a child level
# (serverClass level or app level), you must explicitly define both whitelist
# and blacklist to avoid implicitly clearing the other one. The whitelist and
# blacklist settings operate as an atomic pair.

# Example: Correct override:
# [global]
# whitelist.0=*
# blacklist.0=maintenance.ops.example.com

# [serverClass:MyClass]
# Correct: Define both when overriding
# whitelist.0=*.ops.example.com
# blacklist.0=maintenance.ops.example.com

# Example: Incorrect override (inherited blacklist is cleared):
# [global]
# whitelist.0=*
# blacklist.0=maintenance.ops.example.com

# [serverClass:MyClass]
# Incorrect action: Defining only whitelist clears inherited 
# blacklist, maintenance.ops.example.com will now be included
# whitelist.0=*.ops.example.com

# Caution: Filter-triggered atomic override (level-dependent behavior)
# The following filters have different behavior depending on the level:
#   * machineTypesFilter
#   * packageTypesFilter  
#   * updaterRunningFilter
#
# At the app level:
#   Defining any of these filters triggers an atomic override that clears
#   both whitelist and blacklist inherited from the parent serverClass.
#   You must explicitly define whitelist and/or blacklist at the app level,
#   or no agents will match (due to empty whitelist in default whitelist mode).
#
# At the serverClass level:
#   Defining any of these filters doesn't clear whitelist and blacklist
#   inherited from the global level. The inherited filters remain in effect.
#
# At the global level:
#   These three filters have no effect. They are only operational at the
#   serverClass or app level.

# Example: Filter-triggered override pitfall:
# [serverClass:sc]
# whitelist.0=*

# [serverClass:sc:app:app1]
# Wrong: This clears inherited whitelist.0=* from serverClass
# App will not deploy to any agent unless you add whitelist here
# machineTypesFilter = linux-x86_64

# Example: Correct filter-triggered override:
# [serverClass:sc]
# whitelist.0=*

# [serverClass:sc:app:app1]
# Correct: Explicitly set whitelist when using machineTypesFilter
# whitelist.0=*
# machineTypesFilter = linux-x86_64

# Alternative: Use filterType=blacklist:
# [serverClass:sc]
# whitelist.0=*

# [serverClass:sc:app:app1]
# Correct: filterType=blacklist provides default-allow behavior
# filterType = blacklist
# machineTypesFilter = linux-x86_64

whitelist.from_pathname = <pathname>
blacklist.from_pathname = <pathname>
* As an alternative to a series of (whitelist|blacklist).<n>, you can
  import the <clientName>, <IP address>, and <hostname> list from
  <pathname> that is either a plain text file or a comma-separated values
  (CSV) file.
* You can use this setting in conjunction with
  (whitelist|blacklist).select_field, (whitelist|blacklist).where_field,
  and (whitelist|blacklist).where_equals.
* If used by itself, <pathname> specifies a plain text file where one
  <clientName>, <IP address>, or <hostname> is given per line.
* If used in conjunction with select_field, where_field, and
  where_equals, <pathname> specifies a CSV file.
* The <pathname> is relative to $SPLUNK_HOME.
* You can also use this setting in conjunction with
  (whitelist|blacklist).<n> to specify additional values, but there is
  no direct relation between them.
* At most one from_pathname can be given per stanza.

whitelist.select_field = <field name> | <positive integer>
blacklist.select_field = <field name> | <positive integer>
* Specifies which field of the CSV file contains the <clientName>, <IP address>,
  or <hostname> either by field name or number.
* If <field name> is given, the first line of the CSV file must be a
  header line that contains the names of all the fields and the <field
  name> must specify which field contains the values to be used. Field
  names are case-sensitive.
* If you provide a <positive integer>, it specifies the column number,
  starting at 1, of the field that contains the values to use. In this
  case, the first line of the CSV file must not be a header line.
* You must use this setting in conjunction with
  (whitelist|blacklist).from_pathname.
* You can use this setting in conjunction with
  (whitelist|blacklist).where_field and (whitelist|blacklist).where_equals.
* At most one select_field can be given per stanza.

whitelist.where_field = <field name> | <positive integer>
blacklist.where_field = <field name> | <positive integer>
* Specifies that only a subset of values are to be selected from
  (whitelist|blacklist).select_field.
* Specifies which field of the CSV file contains values to be compared against
  for equality with the (whitelist|blacklist).where_equals values.
* Like (whitelist|blacklist).select_field, the field can be specified by
  either name or number. However, select_field and where_field must be
  specified the same way, either both by name or both by number.
* You must use this setting in conjunction with
  (whitelist|blacklist).select_field and (whitelist|blacklist).where_equals.
* At most one where_field may be given per stanza.

whitelist.where_equals = <comma-separated list>
blacklist.where_equals = <comma-separated list>
* Specifies the value(s) that the value of (whitelist|blacklist).where_field
  must equal in order to be selected via (whitelist|blacklist).select_field.
* If more than one value is specified, separated by commas, the value of
  (whitelist|blacklist).where_field can equal any one of the values.
* Each value is a PCRE regular expression with the following aids for easier
  entry:
    * You can specify '.' to mean '\.'
    * You can specify '*' to mean '.*'
* Matches are always case-insensitive; you do not need to specify the
  '(?i)' prefix.
* You must use this setting in conjunction with
  (whitelist|blacklist).select_field and (whitelist|blacklist).where_field.
* At most one where_equals can be given per stanza.

restartSplunkWeb = <boolean>
* Determines whether Splunk Web restarts on the client after app updates.
* A value of "true" means Splunk Web restarts on the client when a member
  app or a directly configured app is updated.
* A value of "false" means Splunk Web does not restart after app updates.
* You can override this setting at the serverClass level and the
  serverClass:app level.
* Default: false

restartSplunkd = <boolean>
* A value of "true" means splunkd restarts on the client when a member app
  or a directly configured app is updated.
* A value of "false" means splunkd does not restart after app updates.
* You can override this setting at the serverClass level and the
  serverClass:app level.
* Default: false

issueReload = <boolean>
* Determines whether the client reloads internal processors after app
  updates.
* A value of "true" means the client triggers a reload of internal
  processors when a member app or a directly configured app is updated.
* A value of "false" means the client does not reload internal processors
  after app updates. The app is not immediately active upon deployment.
* Default: false

restartIfNeeded = <boolean>
* Determines whether the client automatically restarts if an app reload
  fails.
* This setting is valid only on forwarders that are newer than version 6.4.
* A value of "true" means that when 'issueReload' also has a value of
  "true" and an updated app is deployed, the client attempts to reload the
  app. If the reload fails, the client restarts automatically.
* A value of "false" means the client does not automatically restart after
  a failed reload attempt.
* Default: false

stateOnClient = enabled|disabled|noop
* A value of "enabled" sets the application state to enabled on the
  client, regardless of state on the deployment server.
* A value of "disabled" sets the application state to disabled on the
  client, regardless of state on the deployment server.
* A value of "noop" means the state on the client is the same as the
  state on the deployment server.
* You can override this setting at the serverClass level and the
  serverClass:app level.
* Default: enabled

precompressBundles = <boolean>
* Determines whether the deployment server pre-compresses app bundles.
* A value of "true" means the deployment server generates both .bundle and
  .bundle.gz files. The pre-compressed files offer improved performance
  because the deployment server is not required to compress bundles on the
  fly for each client.
* A value of "false" means the deployment server generates only .bundle
  files and compresses them on demand.
* This setting is beneficial only if there is no SSL
  compression in use and the client has support for HTTP compression.
* Deployment Server / server.conf
  * allowSslCompression = false
  * useHTTPServerCompression = true
* Deployment Client / server.conf
  * useHTTPClientCompression = true
* This setting is inherited and available up to the serverClass level,
  not the app level. Apps that belong to server classes that require
  precompression are compressed, even if they belong to a server class
  that does not require precompression.
* Default: true

cronSchedule = <string>
* The cron schedule that is used to reload this serverclass in the
  following format:
  * "<minute> <hour> <day of month> <month> <day of week>"
* Special characters are acceptable. You can use combinations of "*",
  ",", "/", and "-" to specify wildcards, separate values, ranges of
  values, and step values. For example:
  * Run reload at midnight from Monday to Friday: 0 0 * * 1-5
  * Run reload at midnight on December 1: 0 0 1 12 *
  * Run reload every hour at hh:03, hh:23, hh:43: 03,23,43 * * * *
* This setting is available only at the serverclass level.
* You must set 'cronSchedule' in order to run reload jobs automatically
  rather than manually.
* No default.

#################################################
########### SECOND LEVEL: serverClass ###########
#################################################

[serverClass:<serverClassName>]
* This stanza defines a server class. A server class is a collection of
  applications; an application can belong to multiple server classes.
* serverClassName is a unique name that is assigned to this server class.
* A server class can override all inheritable settings in the [global]
  stanza.
* A server class name can only contain: letters, numbers, spaces,
  underscores, dashes, dots, tildes, and the '@' symbol. It is
  case-sensitive.

machineTypesFilter = <comma-separated list>
* Filters deployment clients based on the hardware type of the host machine.
* Optional.
* Caution: Defining 'machineTypesFilter' at the app level triggers an atomic
  override that clears both 'whitelist' and 'blacklist' inherited from the
  parent serverClass. You must explicitly define 'whitelist' and/or
  'blacklist' at the app level where you define 'machineTypesFilter', or
  agents will not match.
* At the serverClass level, defining 'machineTypesFilter' doesn't clear
  'whitelist' and 'blacklist' inherited from the global level.
* This filter has no effect when defined at the global level.
* Boolean OR logic is employed: a match against any element in the list
  constitutes a match.
* This filter is used in boolean AND logic with 'whitelist' and
  'blacklist' filters. Only clients that match the 'whitelist' or
  'blacklist' filters and that match this 'machineTypesFilter' setting
  are included.
  * In other words, the match is an intersection of the matches for the
    'whitelist' or 'blacklist' filters and the matches for
    'machineTypesFilter'.
* You can override this setting at the serverClass and serverClass:app
  levels.
* These patterns are Perl Compatible Regular Expression (PCRE) regular
  expressions, with the following aids for easier entry:
  * You can specify '.' to mean '\.'
  * You can specify '*' to mean '.*'
* Matches are always case-insensitive; you do not need to specify the
  '(?i)' prefix.
* No default.

packageTypesFilter = <comma-separated list>
* Filters deployment clients based on the package type of the client.
* Optional.
* Caution: Defining 'packageTypesFilter' at the app level triggers an atomic
  override that clears both 'whitelist' and 'blacklist' inherited from the
  parent serverClass. You must explicitly define 'whitelist' and/or
  'blacklist' at the app level where you define 'packageTypesFilter', or
  agents will not match.
* At the serverClass level, defining 'packageTypesFilter' doesn't clear
  'whitelist' and 'blacklist' inherited from the global level.
* This filter has no effect when defined at the global level.
* Boolean OR logic is employed: a match against any element in the list
  constitutes a match.
* This filter is used in boolean AND logic with 'whitelist' and
  'blacklist' filters. Only clients that match the 'whitelist' or
  'blacklist' filters and that match this 'packageTypesFilter' setting
  are included.
  * In other words, the match is an intersection of the matches for the
    'whitelist' or 'blacklist' filters and the matches for
    'packageTypesFilter'.
* You can override this setting at the serverClass and serverClass:app
  levels.
* These patterns are Perl Compatible Regular Expression (PCRE) regular
  expressions, with the following aids for easier entry:
  * You can specify '.' to mean '\.'
  * You can specify '*' to mean '.*'
* Matches are always case-insensitive; you do not need to specify the
  '(?i)' prefix.
* No default.

updaterRunningFilter = <boolean>
* Filters deployment clients based on whether the self-updater process is
  running on the host.
* Caution: Defining 'updaterRunningFilter' at the app level triggers an
  atomic override that clears both 'whitelist' and 'blacklist' inherited
  from the parent serverClass. You must explicitly define 'whitelist'
  and/or 'blacklist' at the app level where you define
  'updaterRunningFilter', or agents will not match.
* At the serverClass level, defining 'updaterRunningFilter' doesn't clear
  'whitelist' and 'blacklist' inherited from the global level.
* This filter has no effect when defined at the global level.
* This filter is used in boolean AND logic with 'whitelist' and
  'blacklist' filters. Only clients that match the 'whitelist' or
  'blacklist' filters and that match this 'updaterRunningFilter' setting
  are included.
  * In other words, the match is an intersection of the matches for the
    'whitelist' or 'blacklist' filters and the matches for
    'updaterRunningFilter'.
* The self-updater is a process that must be installed separately to
  upgrade the deployment client. This setting is applicable only if the
  self-updater is installed.
* A value of "true" means only the clients with the self-updater running
  on the host are included.
* A value of "false" means only the clients without the self-updater
  running on the host are included.
* You can override this setting at the serverClass level and the
  serverClass:app level.
* No default.

# Note:
# The following settings are all described in detail in the
# previous [global] section. They can be used in the serverClass stanza to
# override the global setting.
continueMatching = <boolean>
endpoint = <URL template string>
excludeFromUpdate = <comma-separated list>
filterType = whitelist|blacklist
whitelist.<n> = <clientName> | <IP address> | <hostname>
blacklist.<n> = <clientName> | <IP address> | <hostname>
restartSplunkWeb = <boolean>
restartSplunkd = <boolean>
issueReload = <boolean>
restartIfNeeded = <boolean>
stateOnClient = enabled|disabled|noop
repositoryLocation = <path>
targetRepositoryLocation = <path>
cronSchedule = <string>

########################################
########### THIRD LEVEL: app ###########
########################################

[serverClass:<server class name>:app:<app name>]
* This stanza maps an application, which must already exist in
  'repositoryLocation', to the specified server class.
* server class name is the server class to which this content is added.
* app name can be '*' or the name of an app:
  * The value '*' refers to all content in 'repositoryLocation', adding
    it to this serverClass. The '*' stanza cannot be mixed with named
    stanzas for a given server class.
  * The name of an app explicitly adds the app to a server class.
    Typically apps are named by the folders that contain them.
  * An application name, if it is not the special '*' sign explained
    directly above, can only contain: letters, numbers, spaces,
    underscores, dashes, dots, tildes, and the '@' symbol. It is
    case-sensitive.

# Note: App-level 'filterType' default change
# Starting from Splunk Enterprise version 9.4.3, the implicit default value
# for 'filterType' at the app level changed from "blacklist" (default-allow)
# to "whitelist" (default-deny). This change means:
#
# * If you define a blacklist at the app level without defining 'filterType'
#   or 'whitelist', no agents will be matched in version 
#   9.4.3 and later (agents will not match the empty whitelist). 
#
# * If you define machineTypesFilter, packageTypesFilter, or 
#   updaterRunningFilter at the app level, you must also explicitly define
#   'whitelist' or 'filterType=blacklist' to match agents.
#
# * Migration: Review existing app-level stanzas that use blacklist or
#   additional filters without explicit whitelist. Add 'whitelist.0=*' or
#   'filterType=blacklist' as needed.

appFile = <file name>
* In cases where the app name is different from the file or directory
  name, you can use this setting to specify the file name.
* Supported formats are directories, .tar files, and .tgz files.
* No default.

# Note: The following settings may override settings at the global or
  serverClass levels.
issueReload = <boolean>
restartIfNeeded = <boolean>
excludeFromUpdate = <comma-separated list>
filterType = whitelist|blacklist
whitelist.<n> = <clientName> | <IP address> | <hostname>
blacklist.<n> = <clientName> | <IP address> | <hostname>
machineTypesFilter = <comma-separated list>
packageTypesFilter = <comma-separated list>
updaterRunningFilter = <boolean>
stateOnClient = enabled|disabled|noop
