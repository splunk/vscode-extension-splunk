#   Version 7.3.0
#
# This file contains possible attributes and values you can use to configure
# distributed search.
#
# To set custom configurations, place a distsearch.conf in
# $SPLUNK_HOME/etc/system/local/.  For examples, see distsearch.conf.example.
# You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles
#
# These attributes are all configured on the search head, with the exception of
# the optional attributes listed under the SEARCH HEAD BUNDLE MOUNTING OPTIONS
# heading, which are configured on the search peers.

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#   * You can also define global settings outside of any stanza, at the top of
#     the file.
#   * Each conf file should have at most one default stanza. If there are
#     multiple default stanzas, attributes are combined. In the case of
#     multiple definitions of the same attribute, the last definition in the
#     file wins.
#   * If an attribute is defined at both the global level and in a specific
#     stanza, the value in the specific stanza takes precedence.

[distributedSearch]
* Set distributed search configuration options under this stanza name.
* Follow this stanza name with any number of the following attribute/value
  pairs.
* If you do not set any attribute, Splunk software uses the default value
  (if there is one listed).

disabled = <boolean>
* Toggle distributed search off ("true") and on ("false").
* Default: false (distributed search is enabled by default)

heartbeatMcastAddr = <IP address>
* DEPRECATED.

heartbeatPort = <port>
* DEPRECATED.

ttl = <integer>
* DEPRECATED.

heartbeatFrequency = <integer>
* DEPRECATED.

statusTimeout = <integer>
* Set connection timeout when gathering a search peer's basic
  info (/services/server/info).
* Increasing this value on the Distributed Monitoring Console (DMC) can result
  in fewer peers showing up as "Down" in /services/search/distributed/peers/.
* Note: Read/write timeouts are automatically set to twice this value.
* Default: 10

removedTimedOutServers = <boolean>
* This setting is no longer supported, and will be ignored.

checkTimedOutServersFrequency = <integer>
* This setting is no longer supported, and will be ignored.

autoAddServers = <boolean>
* DEPRECATED.

bestEffortSearch = <boolean>
* This setting determines whether a search peer that's missing the
  knowledge bundle participates in the search.
* If set to "true", the peer participates in the search even if it
  doesn't have the knowledge bundle. The peers that don't have any
  common bundles are simply not searched.
* Default: false

skipOurselves = <boolean>
* DEPRECATED.

servers = <comma-separated list>
* An initial list of servers.
* Each member of this list must be a valid URI in the format of
  scheme://hostname:port

disabled_servers = <comma-separated list>
* A list of disabled search peers. Peers in this list are not monitored
  or searched.
* Each member of this list must be a valid URI in the format of
  scheme://hostname:port

quarantined_servers = <comma-separated list>
* A list of quarantined search peers.
* Each member of this list must be a valid URI in the format of
  scheme://hostname:port
* The admin might quarantine peers that seem unhealthy and are degrading search
  performance of the whole deployment.
* Quarantined peers are monitored but not searched by default.
* A user might use the splunk_server arguments to target a search
  to quarantined peers at the risk of slowing the search.
* When you quarantine a peer, any real-time searches that are running are NOT
  restarted. Currently running real-time searches continue to return results
  from the quarantined peers. Any real-time searches started after the peer
  has been quarantined will not contact the peer.
* Whenever a quarantined peer is excluded from search, appropriate warnings
  are displayed in the search.log and in the Job Inspector.

useDisabledListAsBlacklist = <boolean>
* Whether or not the search head treats the 'disabled_servers' setting as
  a blacklist.
* If set to “true”, search peers that appear in both the 'servers'
  and 'disabled_servers' lists are disabled and do not participate in search.
* If set to “false”, search peers that appear in both lists are enabled
  and participate in search.
* Default: false

shareBundles = <boolean>
* Indicates whether this server will use bundle replication to share search-time
  configurations with search peers.
* If set to "false", the search head assumes that all the search peers can
  access the correct bundles via shared storage and have configured the
  options listed under the "SEARCH HEAD BUNDLE MOUNTING OPTIONS" heading.
* Default: true

useSHPBundleReplication =[true|false|always]
* Whether the search heads in the pool compete with each other to decide which
  one handles the bundle replication (every time bundle replication needs
  to happen), or whether each of them individually replicates the bundles.
* This setting is only relevant in search head pooling environments.
* When set to "always" and you have configured mounted bundles, use the
  search head pool GUID rather than each individual server name to identify
  bundles (and search heads to the remote peers).
* Default: true

trySSLFirst = <boolean>
* This setting is no longer supported, and will be ignored.

peerResolutionThreads = <integer>
* This setting is no longer supported, and will be ignored.

defaultUriScheme = [http|https]
* The default URI scheme to use if you add a new peer without specifying
  a scheme for the URI to its management port.
* Default: https

serverTimeout = <integer>
* This setting is no longer supported, and will be ignored.
* It has been replaced by the following settings:
  'connectionTimeout', 'sendTimeout', 'receiveTimeout'.

connectionTimeout = <integer>
* The maximum amount of time to wait, in seconds, when the search head
  is attempting to establish a connection to the search peer.

sendTimeout = <integer>
* The maximum amount of time to wait, in seconds, when the search head
  is attempting to write or send data to a search peer.

receiveTimeout = <integer>
* The maximum amount of time to wait, in seconds, when the search head
  is attempting to read or receive data from a search peer.

authTokenConnectionTimeout = <integer>
* The maximum amount of time to wait, in seconds, for the search head
  to connect to a remote search peer when reading its authentication token.
* Fractional seconds are allowed (for example, 10.5 seconds).
* Default: 5

authTokenSendTimeout = <integer>
* The maximum amount of time to wait, in seconds, for the search head
  to send a request to a remote peer when getting its authentication token.
* Fractional seconds are allowed (for example, 10.5 seconds).
* Default: 10

authTokenReceiveTimeout = <integer>
* The maximum amount of time to wait, in seconds, for the search head to
  receive a response from a remote peer when getting its authentication token.
* Fractional seconds are allowed (for example, 10.5 seconds).
* Default: 10

bcs = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* A string that represents the URL for the Bucket Catalog Service.
* Optional.
* There is no default.

bcsPath = <path>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Default: /bcs/v1/buckets

#******************************************************************************
# DISTRIBUTED SEARCH KEY PAIR GENERATION OPTIONS
#******************************************************************************

[tokenExchKeys]

certDir = <directory>
* This directory contains the local Splunk Enterprise instance's distributed
  search key pair.
* This directory also contains the public keys of servers that distribute
  searches to this Splunk Enterprise instance.
* Default: $SPLUNK_HOME/etc/auth/distServerKeys

publicKey = <string>
* The name of the public key file for this Splunk Enterprise instance.
* Default: trusted.pem

privateKey = <string>
* The name of private key file for this Splunk Enterprise instance.
* Default: private.pem

genKeyScript = <string>
* The command used to generate the two files above.
* Default: $SPLUNK_HOME/bin/splunk, createssl, audit-keys

#******************************************************************************
# REPLICATION SETTING OPTIONS
#******************************************************************************

[replicationSettings]

connectionTimeout = <integer>
* The maximum amount of time to wait, in seconds, before a search head's initial
  connection to a peer times out.
* Default: 60

sendRcvTimeout = <integer>
* The maximum amount of time to wait, in seconds, when a search head is sending
  a full replication to a peer.
* Default: 60

replicationThreads = <positive integer>|auto
* The maximum number of threads to use when performing bundle replication
  to peers.
* If set to "auto", the peer auto-tunes the number of threads it uses for
  bundle replication.
    * If the peer has 3 or fewer CPUs, it allocates 2 threads.
    * If the peer has 4-7 CPUs, it allocates up to '# of CPUs - 2' threads.
    * If the peer has 8-15 CPUs, it allocates up to '# of CPUs - 3' threads.
    * If the peer has 16 or more CPUs, it allocates up to
      '# of CPUs - 4' threads.
* Default: 5

maxMemoryBundleSize = <integer>
* The maximum size, in megabytes, of bundles to hold in memory.
* If a bundle is larger than this value, Splunk software reads and encodes
  the bundle on the fly for each peer on which the replication is taking place.
* Default: 10

maxBundleSize = <integer>
* The maximum bundle size, in megabytes, for which replication can occur.
* If a bundle is larger than this value, bundle replication does not occur and
  Splunk logs an error message.
* Default: 2048 (2GB)

concerningReplicatedFileSize = <integer>
* The maximum allowable file size, in megabytes, within a bundle.
* Any individual file within a bundle that is larger than this value
  triggers a splunkd.log message.
* Where possible, avoid replicating such files by customizing your blacklists.
* Default: 500

excludeReplicatedLookupSize = <integer>
* The maximum allowable lookup file size, in megabytes, during knowledge
  bundle replication.
* Any lookup file larger than this value is excluded from the knowledge bundle
  that the search head replicates to its search peers.
* When this value is set to "0", this feature is disabled. All file sizes
  are included.
* Default: 0

allowStreamUpload = [auto|true|false]
* Whether to enable streaming bundle replication for peers.
* If set to "auto", search heads use streaming bundle replication when
  connecting to peers with a complete implementation of this feature
  (Splunk Enterprise 6.0 or higher).
* If set to "true", search heads use streaming bundle replication when
  connecting to peers with a complete or experimental implementation
  of this feature (Splunk Enterprise 4.2.3 or higher).
* If set to "false", streaming bundle replication is never used.
* Whatever the value of this setting, streaming bundle replication is
  not used for peers that completely lack support for this feature.
* Default: auto

allowSkipEncoding = <boolean>
* Whether to skip over URL-encoded bundled data on upload.
* Default: true

allowDeltaUpload = <boolean>
* Whether to enable delta-based bundle replication.
* Delta-based replication keeps the bundle compact, with the search head only
  replicating the changed portion of the bundle to its search peers.
* Default: true

sanitizeMetaFiles = <boolean>
* Whether to sanitize or filter *.meta files before replication.
* Use this setting to avoid unnecessary replications triggered by
  writes to *.meta files that have no real effect on search behavior.
* The types of stanzas that "survive" filtering are configured via the
  replicationSettings:refineConf stanza.
* The filtering process removes comments and cosmetic white space.
* Default: true

################################################################
# RFS (AKA S3/REMOTE FILE SYSTEM) REPLICATION-SPECIFIC SETTINGS
################################################################

enableRFSReplication = <boolean>
* Currently not supported. This setting is related to a feature that is
  still under development.
* If set to "true", remote file system bundle replication is enabled.
* When search heads generate bundles, these bundles are uploaded to
  the configured remote file system.
* When search heads delete their old bundles, they subsequently
  attempt to delete the bundle from the configured remote file system.
* Required on search heads.
* Default: false

enableRFSMonitoring = <boolean>
* Currently not supported. This setting is related to a feature that is
  still under development.
* If set to "true", remote file system bundle monitoring is enabled.
* Search peers periodically monitor the configured remote file system
  and download any bundles that they do not have on disk.
* Required on search peers.
* Default: false

rfsMonitoringPeriod = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* The amount of time, in seconds, that a search peer waits between polling
  attempts. You must also configure this setting on search heads, whether or
  not the 'enableRFSMonitoring' setting is enabled on them.
* For search heads when the 'rfsSyncReplicationTimeout' setting is set to
  "auto", this setting automatically adapts the 'rfsSyncReplicationTimeout'
  setting to the monitoring frequency of the search peers.
* If you set this value to less than "60", it automatically defaults to 60.
* Default: 60

rfsSyncReplicationTimeout = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* The amount of time, in seconds, that a search head waits for synchronous
  replication to complete. Only applies to RFS bundle replication.
* The default value is computed from the 'rfsMonitoringPeriod' setting.
  For example, (rfsMonitoringPeriod + 60) * 5, where 60 is the non-configurable
  polling interval from search heads to search peers, and 5 is an
  arbitrary multiplier.
* If you do not modify the 'rfsMonitoringPeriod' setting, the default
  value is 600.
* Default: auto

path = <path>
* Currently not supported. This setting is related to a feature that is
  still under development.
* The remote storage location where bundles reside.
* Required.
* The format for this attribute is: <scheme>://<remote-location-specifier>
  * The "scheme" identifies a supported external storage system type.
  * The "remote-location-specifier" is an external system-specific string
    for identifying a location inside the storage system.
* The following external systems are supported:
  * Object stores that support AWS's S3 protocol. These use the scheme "s3".
    Example: "path=s3://mybucket/some/path"
  * POSIX file system, potentially a remote file system mounted over NFS.
    These use the scheme "file".
    Example: "path=file:///mnt/cheap-storage/some/path"

remote.s3.endpoint = <URL>
* Currently not supported. This setting is related to a feature that is
  still under development.
* The URL of the remote storage system supporting the S3 API.
* The protocol, http or https, can be used to enable or disable SSL
  connectivity with the endpoint.
* If not specified and the indexer is running on EC2, the endpoint is
  constructed automatically based on the EC2 region of the instance where
  the indexer is running, as follows: https://s3-<region>.amazonaws.com
* Example: https://s3-us-west-2.amazonaws.com

remote.s3.encryption = [sse-s3|none]
* Currently not supported. This setting is related to a feature that is
  still under development.
* Specifies the schema to use for Server-Side Encryption (SSE) for data at rest.
* sse-s3: See:
  http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html
* none: Server-side encryption is disabled. Data is stored unencrypted on the
  remote storage.
* Optional.
* Default: none

[replicationSettings:refineConf]

replicate.<conf_file_name> = <boolean>
* Controls whether Splunk software replicates a particular type of
  *.conf file, along with any associated permissions in *.meta files.
* These settings on their own do not cause files to be replicated. You must
  still whitelist a file (via the 'replicationWhitelist' setting) in order for
  it to be eligible for inclusion via these settings.
* In a sense, these settings constitute another level of filtering that applies
  specifically to *.conf files and stanzas with *.meta files.
* Default: false

#******************************************************************************
# REPLICATION WHITELIST OPTIONS
#******************************************************************************

[replicationWhitelist]

<name> = <whitelist_pattern>
* Controls Splunk software's search-time configuration replication from
  search heads to search peers.
* Only files that match a whitelist entry are replicated.
* Conversely, files that do not match a whitelist entry are not replicated.
* Only files located under $SPLUNK_HOME/etc will ever be replicated in this way.
  * The regex is matched against the file name, relative to $SPLUNK_HOME/etc.
    Example: For a file "$SPLUNK_HOME/etc/apps/fancy_app/default/inputs.conf",
             this whitelist should match "apps/fancy_app/default/inputs.conf"
  * Similarly, the etc/system files are available as system/...
    User-specific files are available as users/username/appname/...
* The 'name' element is generally descriptive, with one exception:
  If <name> begins with "refine.", files whitelisted by the given pattern will
  also go through another level of filtering configured in the
  [replicationSettings:refineConf] stanza.
* The whitelist_pattern is the Splunk style pattern matching, which is
  primarily regex-based with special local behavior for '...' and '*'.
  * '...' matches anything, while '*' matches anything besides
    directory separators. See props.conf.spec for more detail on these.
  * Note: '.' will match a literal dot, not any character.
* These lists are applied globally across all configuration data, not to any
  particular application, regardless of where they are defined. Be careful to
  pull in only your intended files.

#******************************************************************************
# REPLICATION BLACKLIST OPTIONS
#******************************************************************************

[replicationBlacklist]

<name> = <blacklist_pattern>
* All comments from the replication whitelist notes above also apply here.
* Replication blacklist takes precedence over the whitelist, meaning that a
  file that matches both the whitelist and the blacklist is NOT replicated.
* Use this setting to prevent unwanted bundle replication in two common
  scenarios:
    * Very large files which part of an application might not want to be
      replicated, especially if they are not needed on search nodes.
    * Frequently updated files (for example, some lookups) will trigger
      retransmission of all search head data.
* These lists are applied globally across all configuration data. Especially
  for blacklisting, be sure to constrain your blacklist to match only data
  that your application does not need.

#******************************************************************************
# BUNDLE ENFORCER WHITELIST OPTIONS
#******************************************************************************

[bundleEnforcerWhitelist]

<name> = <whitelist_pattern>
* Peers use this setting to make sure knowledge bundles sent by search heads and
  masters do not contain alien files.
* If this stanza is empty, the receiver accepts the bundle unless it contains
  files matching the rules specified in the [bundleEnforcerBlacklist] stanza.
  Hence, if both [bundleEnforcerWhitelist] and [bundleEnforcerBlacklist] are
  empty (which is the default), then the receiver accepts all bundles.
* If this stanza is not empty, the receiver accepts the bundle only if it
  contains only files that match the rules specified here but not those in the
  [bundleEnforcerBlacklist] stanza.
* All rules are regular expressions.
* No default.

#******************************************************************************
# BUNDLE ENFORCER BLACKLIST OPTIONS
#******************************************************************************

[bundleEnforcerBlacklist]

<name> = <blacklist_pattern>
* Peers use this setting to make sure knowledge bundle sent by search heads and
  masters do not contain alien files.
* This list overrides the [bundleEnforceWhitelist] stanza above. This means that
  the receiver removes the bundle if it contains any file that matches the
  rules specified here even if that file is allowed by [bundleEnforcerWhitelist].
* If this stanza is empty, then only [bundleEnforcerWhitelist] matters.
* No default.

#******************************************************************************
# SEARCH HEAD BUNDLE MOUNTING OPTIONS
# Configure these settings on the search peers only, and only if you also
# configure shareBundles=false in the [distributedSearch] stanza on the search
# head. Use these settings to access bundles that are not replicated. The search
# peers use a shared
# storage mount point to access the search head bundles ($SPLUNK_HOME/etc).
#******************************************************************************

[searchhead:<searchhead-splunk-server-name>]
* <searchhead-splunk-server-name> is the name of the related search head
  installation.
* The server name is located in server.conf: serverName = <name>

mounted_bundles = <boolean>
* Determines whether the bundles belonging to the search head specified in the
  stanza name are mounted.
* You must set this value to "true" to use mounted bundles.
* Default: false

bundles_location = <path>
* The path to where the search head's bundles are mounted.
* This path must be the mount point on the search peer, not on the search head.
* The path should point to a directory that is equivalent to $SPLUNK_HOME/etc/.
* The path must contain at least the following subdirectories: system, apps,
  users


#******************************************************************************
# DISTRIBUTED SEARCH GROUP DEFINITIONS
# These settings are the definitions of the distributed search groups. A search
# group is a set of search peers as identified by thier host:management-port. A
# search can be directed to a search group using the splunk_server_group argument.
# The search is dispatched to only the members of the group.
#******************************************************************************

[distributedSearch:<splunk-server-group-name>]
* <splunk-server-group-name> is the name of the Splunk server group that is
  defined in this stanza

servers = <comma-separated list>
* A list of search peers that are members of this group.
* The list must use peer identifiers (i.e. hostname:port).

default = <boolean>
* Whether or not this group is the default group of peers against which all
  searches are run, unless a server group is not explicitly specified.
