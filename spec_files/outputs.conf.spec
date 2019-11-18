#   Version 7.3.0
#
# Forwarders require outputs.conf. Splunk instances that do not forward
# do not use it. Outputs.conf determines how the forwarder sends data to
# receiving Splunk instances, either indexers or other forwarders.
#
# To configure forwarding, create an outputs.conf file in
# $SPLUNK_HOME/etc/system/local/. For examples of its use, see
# outputs.conf.example.
#
# You must restart Splunk software to enable configurations.
#
# To learn more about configuration files (including precedence) see the topic
# "About Configuration Files" in the Splunk Documentation set.
#
# To learn more about forwarding, see the topic "About forwarding and
# receiving data" in the Splunk Enterprise Forwarding manual.

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#   * You can also define global settings outside of any stanza, at the top
#     of the file.
#   * Each conf file should have at most one default stanza. If there are
#     multiple default stanzas, settings are combined. In the case of
#     multiple definitions of the same setting, the last definition in the
#     file wins.
#   * If an setting is defined at both the global level and in a specific
#     stanza, the value in the specific stanza takes precedence.
#   * Do not use the 'sslPassword', 'socksPassword', or 'token' settings
#     to set passwords in this stanza as they may remain readable to
#     attackers, specify these settings in the [tcpout] stanza instead.

####
# TCP Output stanzas
####

# There are three levels of TCP Output stanzas:
# * Global: [tcpout]
# * Target group: [tcpout:<target_group>]
# * Single server: [tcpout-server://<ip address>:<port>]
#
# Settings at more specific levels override settings at higher levels. For
# example, an setting set for a single server overrides the value of that
# setting, if any, set at that server's target group stanza. See the
# online documentation on configuring forwarders for details.
#
# This spec file first describes the three levels of stanzas (and any
# settings unique to a particular level). It then describes the optional
# settings, which you can set at any of the three levels.


#----TCP Output Global Configuration -----
# You can overwrite the global configurations specified here in the
# [tcpout] stanza in stanzas for specific target groups, as described later.
# You can only set the 'defaultGroup' and 'indexAndForward' settings
# here, at the global level.
#
# Starting with version 4.2, the [tcpout] stanza is no longer required.

[tcpout]

defaultGroup = <target_group>, <target_group>, ...
* A comma-separated list of one or more target group names, specified later
  in [tcpout:<target_group>] stanzas.
* The forwarder sends all data to the specified groups.
* If you don't want to forward data automatically, don't set this setting.
* Can be overridden by an inputs.conf '_TCP_ROUTING' setting, which in turn
  can be overridden by a props.conf or transforms.conf modifier.
* Starting with version 4.2, this setting is no longer required.

indexAndForward = <boolean>
* Set to "true" to index all data locally, in addition to forwarding it.
* This is known as an "index-and-forward" configuration.
* This setting is only available for heavy forwarders.
* This setting is only available at the top level [tcpout] stanza. It
  cannot be overridden in a target group.
* Default: false

#----Target Group Configuration -----

# If you specify multiple servers in a target group, the forwarder
# performs auto load-balancing, sending data alternately to each available
# server in the group. For example, assuming you have three servers
# (server1, server2, server3) and autoLBFrequency=30, the forwarder sends
# all data to server1 for 30 seconds, then it sends all data to server2 for
# the next 30 seconds, then all data to server3 for the next 30 seconds,
# finally cycling back to server1.
#
# You can have as many target groups as you want.
# If you specify more than one target group, the forwarder sends all data
# to each target group. This is known as "cloning" the data.
#
# NOTE: A target group stanza name cannot contain spaces or colons.
# Splunk software ignores target groups whose stanza names contain
# spaces or colons.

[tcpout:<target_group>]

server = [<ip>|<servername>]:<port>, [<ip>|<servername>]:<port>, ...
* A comma-separated list of one or more systems to send data to over a
  TCP socket.
* Required if the 'indexerDiscovery' setting is not set.
* Typically used to specify receiving Splunk systems, although you can use
  it to send data to non-Splunk systems (see the 'sendCookedData' setting).
* For each system you list, the following information is required:
  * The IP address or server name where one or more systems are listening.
  * The port on which the syslog server is listening.

blockWarnThreshold = <integer>
* The output pipeline send failure count threshold after which a
  failure message appears as a banner in Splunk Web.
* Optional.
* To disable Splunk Web warnings on blocked output queue conditions, set this
  to a large value (for example, 2000000).
* Default: 100

indexerDiscovery = <name>
* The name of the master node to use for indexer discovery.
* Instructs the forwarder to fetch the list of indexers from the master node
  specified in the corresponding [indexer_discovery:<name>] stanza.
* No default.

token = <string>
* The access token for receiving data.
* If you configured an access token for receiving data from a forwarder,
  Splunk software populates that token here.
* If you configured a receiver with an access token and that token is not
  specified here, the receiver rejects all data sent to it.
* This setting is optional.
* No default.

#----Single server configuration-----

# You can define specific configurations for individual indexers on a
# server-by-server basis. However, each server must also be part of a
# target group.

[tcpout-server://<ip address>:<port>]
* Optional. There is no requirement to have a [tcpout-server] stanzas.

#####
#TCPOUT SETTINGS
#####

# These settings are optional and can appear in any of the three stanza levels.

[tcpout<any of above>]

#----General Settings----

sendCookedData = <boolean>
* Whether or not to send processed or unprocessed data to the receiving server.
* If set to "true", events are cooked (have been processed by Splunk software).
* If set to "false", events are raw and untouched prior to sending.
* Set to "false" if you are sending events to a third-party system.
* Default: true

heartbeatFrequency = <integer>
* How often (in seconds) to send a heartbeat packet to the receiving server.
* This setting is a mechanism for the forwarder to know that the receiver
  (indexer) is alive. If the indexer does not send a return packet to the
  forwarder, the forwarder declares the receiver unreachable and does not
  forward data to it.
* The forwarder only sends heartbeats if the 'sendCookedData' setting
  is set to "true".
* Default: 30

blockOnCloning = <boolean>
* Whether or not the TcpOutputProcessor should wait until at least one
  of the cloned output groups receives events before attempting to send
  more events.
* If set to "true", the TcpOutputProcessor blocks until at least one of the
  cloned groups receives events. It does not drop events when all the
  cloned groups are down.
* If set to "false", the TcpOutputProcessor drops events when all the
  cloned groups are down and all queues for the cloned groups are full.
  When at least one of the cloned groups is up and queues are not full,
  the events are not dropped.
* Default: true

blockWarnThreshold = <integer>
* The output pipeline send failure count threshold, after which a
  failure message appears as a banner in Splunk Web.
* To disable Splunk Web warnings on blocked output queue conditions, set this
  to a large value (for example, 2000000).
* This setting is optional.
* Default: 100

compressed = <boolean>
* If set to "true", the receiver communicates with the forwarder in
  compressed format.
* If set to "true", you do not need to set the 'compressed' setting to "true"
  in the inputs.conf file on the receiver for compression
  of data to occur.
* This setting applies to non-SSL forwarding only. For SSL forwarding,
  Splunk software uses the 'useClientSSLCompression' setting.
* Default: false

negotiateProtocolLevel = <unsigned integer>
* When setting up a connection to an indexer, Splunk software tries to
  negotiate the use of the Splunk forwarder protocol with the
  specified feature level based on the value of this setting.
* If set to a lower value than the default, this setting denies the
  use of newer forwarder protocol features when it negotiates a connection.
  This might impact indexer efficiency.
* Default (if 'negotiateNewProtocol' is "true"): 1
* Default (if 'negotiateNewProtocol' is not "true"): 0

negotiateNewProtocol = <boolean>
* The default value of the 'negotiateProtocolLevel' setting.
* DEPRECATED. Set 'negotiateProtocolLevel' instead.
* Default: true

channelReapInterval = <integer>
* How often, in milliseconds, channel codes are reaped, or made
  available for re-use.
* This value sets the minimum time between reapings. In practice,
  consecutive reapings might be separated by greater than the number of
  milliseconds specified here.
* Default: 60000 (1 minute)

channelTTL = <integer>
* How long, in milliseconds, a channel can remain "inactive" before
  it is reaped, or before its code is made available for reuse by a
  different channel.
* Default: 300000 (5 minutes)

channelReapLowater = <integer>
* If the number of active channels is greater than 'channelReapLowater',
  Splunk software reaps old channels to make their channel codes available
  for reuse.
* If the number of active channels is less than 'channelReapLowater',
  Splunk software does not reap channels, no matter how old they are.
* This value essentially determines how many active-but-old channels Splunk
  software keeps "pinned" in memory on both sides of a
  Splunk-to-Splunk connection.
* A non-zero value helps ensure that Splunk software does not waste network
  resources by "thrashing" channels in the case of a forwarder sending
  a trickle of data.
* Default: 10

socksServer = [<ip>|<servername>]:<port>
* The IP address or servername of the Socket Secure version 5 (SOCKS5) server.
* Required.
* This setting specifies the port on which the SOCKS5 server is listening.
* After you configure and restart the forwarder, it connects to the SOCKS5
  proxy host, and optionally authenticates to the server on demand if
  you provide credentials.
* NOTE: Only SOCKS5 servers are supported.
* No default.

socksUsername = <username>
* The SOCKS5 username to use when authenticating against the SOCKS5 server.
* Optional.

socksPassword = <password>
* The SOCKS5 password to use when authenticating against the SOCKS5 server.
* Optional.

socksResolveDNS = <boolean>
* Whether or not the forwarder should rely on the SOCKS5 proxy server Domain
  Name Server (DNS) to resolve hostnames of indexers in the output group it is
  forwarding data to.
* If set to "true", the forwarder sends the hostnames of the indexers to the
  SOCKS5 server, and lets the SOCKS5 server do the name resolution. It
  does not attempt to resolve the hostnames on its own.
* If set to "false", the forwarder attempts to resolve the hostnames of the
  indexers through DNS on its own.
* Optional.
* Default: false

#----Queue Settings----

maxQueueSize = [<integer>|<integer>[KB|MB|GB]|auto]
* The maximum size of the forwarder output queue.
* The size can be limited based on the number of entries, or on the total
  memory used by the items in the queue.
* If specified as a lone integer (for example, "maxQueueSize=100"),
  the 'maxQueueSize' setting indicates the maximum count of queued items.
* If specified as an integer followed by KB, MB, or GB
  (for example, maxQueueSize=100MB), the 'maxQueueSize' setting indicates
  the maximum random access memory (RAM) size of all the items in the queue.
* If set to "auto", this setting configures a value for the output queue
  depending on the value of the 'useACK' setting:
  * If 'useACK' is set to "false", the output queue uses 500KB.
  * If 'useACK' is set to "true", the output queue uses 7MB.
* If you enable indexer acknowledgment by configuring the 'useACK'
  setting to "true", the forwarder creates a wait queue where it temporarily
  stores data blocks while it waits for indexers to acknowledge the receipt
  of data it previously sent.
  * The forwarder sets the wait queue size to triple the value of what
    you set for 'maxQueueSize.'
  * For example, if you set "maxQueueSize=1024KB" and "useACK=true",
    then the output queue is 1024KB and the wait queue is 3072KB.
  * Although the wait queue and the output queue sizes are both controlled
    by this setting, they are separate.
  * The wait queue only exists if 'useACK' is set to "true".
* Limiting the queue sizes by quantity is historical. However,
  if you configure queues based on quantity, keep the following in mind:
  * Queued items can be events or blocks of data.
    * Non-parsing forwarders, such as universal forwarders, send
      blocks, which can be up to 64KB.
    * Parsing forwarders, such as heavy forwarders, send events, which
      are the size of the events. Some events are as small as
      a few hundred bytes. In unusual cases (data dependent), you might
      arrange to produce events that are multiple megabytes.
* Default: auto
  * if 'useACK' is set to "true" and this setting is set to "auto", then
    the output queue is 7MB and the wait queue is 21MB.

dropEventsOnQueueFull = <integer>
* The number of seconds to wait before the output queue throws out all
  new events until it has space.
* If set to a positive number, the queue waits 'dropEventsonQueueFull'
  seconds before throwing out all new events.
* If set to -1 or 0, the output queue blocks when it is full. This further
  blocks events up the processing chain.
* If any target group queue is blocked, no more data reaches any other
  target group.
* Using auto load-balancing is the best way to minimize this condition.
  In this case, multiple receivers must be down (or jammed up) before
  queue blocking can occur.
* CAUTION: DO NOT SET THIS TO A POSITIVE INTEGER IF YOU ARE
  MONITORING FILES.
* Default: -1

dropClonedEventsOnQueueFull = <integer>
* The amount of time, in seconds, to wait before dropping events from
  the group.
* If set to a positive number, the queue does not block completely, but
  waits up to 'dropClonedEventsOnQueueFull' seconds to queue events to a
  group.
  * If it cannot queue to a group for more than 'dropClonedEventsOnQueueFull'
    seconds, it begins dropping events from the group. It makes sure that at
    least one group in the cloning configuration can receive events.
  * The queue blocks if it cannot deliver events to any of the cloned groups.
* If set to -1, the TcpOutputProcessor ensures that each group
  receives all of the events. If one of the groups is down, the
  TcpOutputProcessor blocks everything.
* Default: 5

#######
# Backoff Settings When Unable To Send Events to Indexer
# The settings in this section determine forwarding behavior when there are
# repeated failures in sending events to an indexer ("sending failures").
#######

maxFailuresPerInterval = <integer>
* The maximum number of failures allowed per interval before a forwarder
  applies backoff (stops sending events to the indexer for a specified
  number of seconds). The interval is defined in the 'secsInFailureInterval'
  setting.
* Default: 2

secsInFailureInterval = <integer>
* The number of seconds contained in a failure interval.
* If the number of write failures to the indexer exceeds
  'maxFailuresPerInterval' in the specified 'secsInFailureInterval' seconds,
  the forwarder applies backoff.
* The backoff time period range is 1-10 * 'autoLBFrequency'.
* Default: 1

backoffOnFailure = <positive integer>
* The number of seconds a forwarder backs off, or stops sending events,
  before attempting to make another connection with the indexer.
* Default: 30

maxConnectionsPerIndexer = <integer>
* The maximum number of allowed connections per indexer.
* In the presence of failures, the maximum number of connection attempts
  per indexer at any point in time.
* Default: 2

connectionTimeout = <integer>
* The time to wait, in seconds, for a forwarder to establish a connection
  with an indexer.
* The connection times out if an attempt to establish a connection
  with an indexer does not complete in 'connectionTimeout' seconds.
* Default: 20

readTimeout = <integer>
* The time to wait, in seconds, for a forwarder to read from a socket it has
  created with an indexer.
* The connection times out if a read from a socket does not complete in
  'readTimeout' seconds.
* This timeout is used to read acknowledgment when indexer acknowledgment is
  enabled (when you set 'useACK' to "true").
* Default: 300 seconds (5 minutes)

writeTimeout = <integer>
* The time to wait, in seconds, for a forwarder to complete a write to a
  socket it has created with an indexer.
* The connection times out if a write to a socket does not finish in
  'writeTimeout' seconds.
* Default: 300 seconds (5 minutes)

tcpSendBufSz = <integer>
* The size of the TCP send buffer, in bytes.
* Only use this setting if you are a TCP/IP expert.
* Useful to improve throughput with small events, like Windows events.
* Default: the system default

ackTimeoutOnShutdown = <integer>
* The time to wait, in seconds, for the forwarder to receive indexer
  acknowledgments during a forwarder shutdown.
* The connection times out if the forwarder does not receive indexer
  acknowledgements (ACKs) in 'ackTimeoutOnShutdown' seconds during
  forwarder shutdown.
* Default: 30 seconds

dnsResolutionInterval = <integer>
* The base time interval, in seconds, at which indexer Domain Name Server
  (DNS) names are resolved to IP addresses.
* This is used to compute runtime dnsResolutionInterval as follows:
  Runtime interval =
   'dnsResolutionInterval' + (number of indexers in server settings - 1) * 30.
* The DNS resolution interval is extended by 30 seconds for each additional
  indexer in the server setting.
* Default: 300 seconds (5 minutes)

forceTimebasedAutoLB = <boolean>
* Forces existing data streams to switch to a newly elected indexer every
  auto load balancing cycle.
* On universal forwarders, use the 'EVENT_BREAKER_ENABLE' and
  'EVENT_BREAKER' settings in props.conf rather than 'forceTimebasedAutoLB'
  for improved load balancing, line breaking, and distribution of events.
* Default: false

#----Index Filter Settings.
# These settings are only applicable under the global [tcpout] stanza.
# This filter does not work if it is created under any other stanza.

forwardedindex.<n>.whitelist = <regex>
forwardedindex.<n>.blacklist = <regex>
* These filters determine which events get forwarded to the index,
  based on the indexes the events are targeted to.
* An ordered list of whitelists and blacklists, which together
  decide if events are forwarded to an index.
* The order is determined by <n>. <n> must start at 0 and continue with
  positive integers, in sequence. There cannot be any gaps in the sequence.
  * For example:
    forwardedindex.0.whitelist, forwardedindex.1.blacklist,
    forwardedindex.2.whitelist, ...
* The filters can start from either whitelist or blacklist. They are tested
  from forwardedindex.0 to forwardedindex.<max>.
* If both forwardedindex.<n>.whitelist and forwardedindex.<n>.blacklist are
  present for the same value of n, then forwardedindex.<n>.whitelist is
  honored. forwardedindex.<n>.blacklist is ignored in this case.
* In general, you do not need to change these filters from their default
  settings in $SPLUNK_HOME/system/default/outputs.conf.
* Filtered out events are not indexed if you do not enable local indexing.

forwardedindex.filter.disable = <boolean>
* Whether or not index filtering is active.
* If set to "true", disables index filtering. Events for all indexes are then
  forwarded.
* Default: false

#----Automatic Load-Balancing
# Automatic load balancing is the only way to forward data.
# Round-robin method of load balancing is no longer supported.

autoLBFrequency = <integer>
* The amount of time, in seconds, that a forwarder sends data to an indexer
  before redirecting outputs to another indexer in the pool.
* Use this setting when you are using automatic load balancing of outputs
  from universal forwarders (UFs).
* Every 'autoLBFrequency' seconds, a new indexer is selected randomly from the
  list of indexers provided in the server setting of the target group
  stanza.
* Default: 30

autoLBVolume = <integer>
* The volume of data, in bytes, to send to an indexer before a new indexer
  is randomly selected from the list of indexers provided in the server
  setting of the target group stanza.
* This setting is closely related to the 'autoLBFrequency' setting.
  The forwarder first uses 'autoLBVolume' to determine if it needs to
  switch to another indexer. If the 'autoLBVolume' is not reached,
  but the 'autoLBFrequency' is, the forwarder switches to another
  indexer as the forwarding target.
* A non-zero value means that volume-based forwarding is active.
* 0 means the volume-based forwarding is not active.
* Default: 0

#----Secure Sockets Layer (SSL) Settings----

# To set up SSL on the forwarder, set the following setting/value pairs.
# If you want to use SSL for authentication, add a stanza for each receiver
# that must be certified.

useSSL = <true|false|legacy>
* Whether or not the forwarder uses SSL to connect to the receiver, or relies
  on the 'clientCert' setting to be active for SSL connections.
* You do not need to set 'clientCert' if 'requireClientCert' is set to
  "false" on the receiver.
* If set to "true", then the forwarder uses SSL to connect to the receiver.
* If set to "false", then the forwarder does not use SSL to connect to the
  receiver.
* If set to "legacy", then the forwarder uses the 'clientCert' property to
  determine whether or not to use SSL to connect.
* Default: legacy

sslPassword = <password>
* The password associated with the Certificate Authority certficate (CAcert).
* The default Splunk CAcert uses the password "password".
* No default.

clientCert = <path>
* The full path to the client SSL certificate in Privacy Enhanced Mail (PEM)
  format.
* If you have not set 'useSSL', then this connection uses SSL if and only if
  you specify this setting with a valid client SSL certificate file.
* No default.

sslCertPath = <path>
* The full path to the client SSL certificate.
* DEPRECATED.
* Use the 'clientCert' setting instead.

cipherSuite = <string>
* The specified cipher string for the input processors.
* This setting ensures that the server does not accept connections using weak
  encryption protocols.
* The default can vary. See the 'cipherSuite' setting in
  $SPLUNK_HOME/etc/system/default/outputs.conf for the current default.

sslCipher = <string>
* The specified cipher string for the input processors.
* DEPRECATED.
* Use the 'cipherSuite' setting instead.

ecdhCurves = <comma-separated list>
* A list of Elliptic Curve-Diffie-Hellmann curves to use for ECDH
  key negotiation.
* The curves should be specified in the order of preference.
* The client sends these curves as a part of an SSL Client Hello.
* The server supports only the curves specified in the list.
* Splunk software only supports named curves that have been specified
  by their SHORT names.
* The list of valid named curves by their short and long names can be obtained
  by running this CLI command:
  $SPLUNK_HOME/bin/splunk cmd openssl ecparam -list_curves
* Example setting: "ecdhCurves = prime256v1,secp384r1,secp521r1"
* The default can vary. See the 'ecdhCurves' setting in
  $SPLUNK_HOME/etc/system/default/outputs.conf for the current default.

sslRootCAPath = <path>
* The full path to the root Certificate Authority (CA) certificate store.
* DEPRECATED.
* Use the 'server.conf/[sslConfig]/sslRootCAPath' setting instead.
* Used only if 'sslRootCAPath' in server.conf is not set.
* The <path> must refer to a Privacy Enhanced Mail (PEM) format file
  containing one or more root CA certificates concatenated together.
* No default.

sslVerifyServerCert = <boolean>
* Serves as an additional step for authenticating your indexers.
* If "true", ensure that the server you are connecting to has a valid
  SSL certificate. Note that certificates with the same Common Name as
  the CA's certificate will fail this check.
* Both the common name and the alternate name of the server are then checked
  for a match.
* Default: false

tlsHostname = <string>
* A Transport Layer Security (TLS) extension that allows sending an identifier
  with SSL Client Hello.
* Default: empty string

sslCommonNameToCheck = <commonName1>, <commonName2>, ...
* Checks the Common Name of the server's certificate against the names listed here.
* The Common Name identifies the host name associated with the certificate.
  For example, example www.example.com or example.com
* If there is no match, assume that Splunk software is not authenticated
  against this server.
* You must set the 'sslVerifyServerCert' setting to "true" for this setting
  to work.
* This setting is optional.
* Default: empty string (no common name checking).

sslAltNameToCheck = <alternateName1>, <alternateName2>, ...
* Checks the alternate name of the server's certificate against the names listed here.
* If there is no match, assume that Splunk software is not authenticated
  against this server.
* You must set the 'sslVerifyServerCert' setting to "true" for this setting to work.
* This setting is optional.
* Default: no alternate name checking

useClientSSLCompression = <boolean>
* Enables compression on SSL.
* Default: The value of 'server.conf/[sslConfig]/useClientSSLCompression'

sslQuietShutdown = <boolean>
* Enables quiet shutdown mode in SSL.
* Default: false

sslVersions = <comma-separated list>
* A comma-separated list of SSL versions to support.
* The versions available are "ssl3", "tls1.0", "tls1.1", and "tls1.2"
* The special version "*" selects all supported versions. The version "tls"
  selects all versions tls1.0 or newer
* If you prefix a version with "-", it is removed from the list.
* SSLv2 is always disabled; "-ssl2" is accepted in the version list, but
  does nothing.
* When 'appServerPorts'="0" only supported values are "all", "ssl3, tls"
  and "tls"
* When configured in FIPS mode, "ssl3" is always disabled regardless
  of this configuration.
* The default can vary. See the 'sslVersions' setting in
  $SPLUNK_HOME/etc/system/default/outputs.conf for the current default.

#----Indexer Acknowledgment ----
# Indexer acknowledgment ensures that forwarded data is reliably delivered
# to the receiver.
#
# If the receiver is an indexer, it indicates that the indexer has received
# the data, indexed it, and written it to the file system. If the receiver
# is an intermediate forwarder, it indicates that the intermediate forwarder
# has successfully forwarded the data to the terminating indexer and has
# received acknowledgment from that indexer.
#
# Indexer acknowledgment is a complex feature that requires
# careful planning. Before using it, read the online topic describing it in
# the Splunk Enterprise Distributed Deployment manual.

useACK = <boolean>
* Whether or not to use indexer acknowledgment.
* Indexer acknowledgment is an optional capability on forwarders that helps
  prevent loss of data when sending data to an indexer.
* When set to "true", the forwarder retains a copy of each sent event
  until the receiving system sends an acknowledgment.
  * The receiver sends an acknowledgment when it has fully handled the event
    (typically when it has written it to disk in indexing).
  * If the forwarder does not receive an acknowledgment, it resends the data
    to an alternative receiver.
  * NOTE: The maximum memory used for the outbound data queues increases
    significantly by default (500KB -> 28MB) when the 'useACK' setting is
    enabled. This is intended for correctness and performance.
* When set to "false", the forwarder considers the data fully processed
  when it finishes writing it to the network socket.
* You can configure this setting at the [tcpout] or [tcpout:<target_group>]
  stanza levels. You cannot set it for individual servers at the
  [tcpout-server: ...] stanza level.
* Default: false

############
#----Syslog output----
############
# The syslog output processor is not available for universal or light
# forwarders.

# The following configuration is used to send output using syslog.

[syslog]

defaultGroup = <target_group>, <target_group>, ...

# For the following settings, see the [syslog:<target_group>] stanza.

type = [tcp|udp]
priority = <<integer>> | NO_PRI
maxEventSize = <integer>

[syslog:<target_group>]

#----REQUIRED SETTINGS----
# The following settings are required for a syslog output group.

server = [<ip>|<servername>]:<port>
* The IP address or servername where the syslog server is running.
* Required.
* This setting specifies the port on which the syslog server listens.
* Default: 514

#----OPTIONAL SETTINGS----

# The following are optional settings for syslog output:

type = [tcp|udp]
* The network protocol to use.
* Default: udp

priority = <<integer>>|NO_PRI
* The priority value included at the beginning of each syslog message.
* The priority value ranges from 0 to 191 and is made up of a Facility
  value and a Level value.
* Enclose the priority value in "<>" delimeters. For example, specify a
  priority of 34 as follows: <34>
* The integer must be one to three digits in length.
* The value you enter appears in the syslog header.
* The value mimics the number passed by a syslog interface call. See the
  *nix man page for syslog for more information.
* Calculate the priority value as follows: Facility * 8 + Severity
  For example, if Facility is 4 (security/authorization messages)
  and Severity is 2 (critical conditions), the priority will be
  (4 * 8) + 2 = 34. Set the setting to <34>.
* If you do not want to add a priority value, set the priority to "<NO_PRI>".
* The table of facility and severity (and their values) is located in
  RFC3164. For example, http://www.ietf.org/rfc/rfc3164.txt section 4.1.1
* The table is reproduced briefly below. Some values are outdated.
  Facility:
     0 kernel messages
     1 user-level messages
     2 mail system
     3 system daemons
     4 security/authorization messages
     5 messages generated internally by syslogd
     6 line printer subsystem
     7 network news subsystem
     8 UUCP subsystem
     9 clock daemon
    10 security/authorization messages
    11 FTP daemon
    12 NTP subsystem
    13 log audit
    14 log alert
    15 clock daemon
    16 local use 0  (local0)
    17 local use 1  (local1)
    18 local use 2  (local2)
    19 local use 3  (local3)
    20 local use 4  (local4)
    21 local use 5  (local5)
    22 local use 6  (local6)
    23 local use 7  (local7)
  Severity:
    0  Emergency: system is unusable
    1  Alert: action must be taken immediately
    2  Critical: critical conditions
    3  Error: error conditions
    4  Warning: warning conditions
    5  Notice: normal but significant condition
    6  Informational: informational messages
    7  Debug: debug-level messages
* Default: <13> (Facility of "user" and Severity of "Notice")

syslogSourceType = <string>
* Specifies an additional rule for handling data, in addition to that
  provided by the 'syslog' source type.
* This string is used as a substring match against the sourcetype key. For
  example, if the string is set to "syslog", then all sourcetypes
  containing the string 'syslog' receive this special treatment.
* To match a sourcetype explicitly, use the pattern
  "sourcetype::sourcetype_name".
    * Example: syslogSourceType = sourcetype::apache_common
* Data that is "syslog" or matches this setting is assumed to already be in
  syslog format.
* Data that does not match the rules has a header, optionally a timestamp
  (if defined in 'timestampformat'), and a hostname added to the front of
  the event. This is how Splunk software causes arbitrary log data to match syslog expectations.
* No default.

timestampformat = <format>
* If specified, Splunk software prepends formatted timestamps to events
  forwarded to syslog.
* As above, this logic is only applied when the data is not syslog, or the
  type specified in the 'syslogSourceType' setting, because it is assumed
  to already be in syslog format.
* If the data is not in syslog-compliant format and you do not specify a
 'timestampformat', the output will not be RFC3164-compliant.
* The format is a strftime (string format time)-style timestamp formatting
  string. This is the same implementation used in the 'eval' search command,
  Splunk logging, and other places in splunkd.
  * For example: %b %e %H:%M:%S for RFC3164-compliant output
    * %b - Abbreviated month name (Jan, Feb, ...)
    * %e - Day of month
    * %H - Hour
    * %M - Minute
    * %s - Second
* For a more exhaustive list of the formatting specifiers, refer to the
  online documentation.
* Do not put the string in quotes.
* No default. No timestamp is added to the front of events.

maxEventSize = <integer>
* The maximum size of an event, in bytes, that Splunk software will transmit.
* All events exceeding this size are truncated.
* Optional.
* Default: 1024

#---- Routing Data to Syslog Server -----
# To route data to syslog servers:
# 1) Decide which events to route to which servers.
# 2) Edit the props.conf, transforms.conf, and outputs.conf files on the
#    forwarders.

# Edit $SPLUNK_HOME/etc/system/local/props.conf and set a TRANSFORMS-routing
# setting as shown below.
#
# [<spec>]
# TRANSFORMS-routing=<unique_stanza_name>

* <spec> can be:
  * <sourcetype>, the source type of an event
  * host::<host>, where <host> is the host for an event
  * source::<source>, where <source> is the source for an event

* Use the <unique_stanza_name> when creating your entry in transforms.conf.

# Edit $SPLUNK_HOME/etc/system/local/transforms.conf and set rules to match
# your props.conf stanza:
#
#  [<unique_stanza_name>]
#  REGEX = <your_regex>
#  DEST_KEY = _SYSLOG_ROUTING
#  FORMAT = <unique_group_name>

* Set <unique_stanza_name> to match the name you created in props.conf.
* Enter the regex rules in 'REGEX' to determine which events get
  conditionally routed.
* Set 'DEST_KEY' to "_SYSLOG_ROUTING" to send events via syslog.
* Set 'FORMAT' to match the syslog group name you create in outputs.conf.

####
#----IndexAndForward Processor-----
####

# The IndexAndForward processor determines the default behavior for indexing
# data on a Splunk instance. It has the "index" property, which determines
# whether indexing occurs.
#
# When Splunk is not configured as a forwarder, 'index' is set to "true".
# That is, the Splunk instance indexes data by default.
#
# When Splunk is configured as a forwarder, the processor sets 'index' to
# "false". That is, the Splunk instance does not index data by default.
#
# The IndexAndForward processor has no effect on the universal forwarder,
# which can never index data.
#
# If the [tcpout] stanza configures the indexAndForward setting, the value
# of that setting overrides the default value of 'index'. However, if you
# set 'index' in the [indexAndForward] stanza described below, it
# supersedes any value set in [tcpout].

[indexAndForward]

index = <boolean>
* Turns indexing on or off on a Splunk instance.
* If set to "true", the Splunk instance indexes data.
* If set to "false", the Splunk instance does not index data.
* The default can vary. It depends on whether the Splunk
  instance is configured as a forwarder, and whether it is
  modified by any value configured for the indexAndForward
  setting in [tcpout].

selectiveIndexing = <boolean>
* Whether or not to index specific events that have the
  '_INDEX_AND_FORWARD_ROUTING' setting configured.
* If set to "true", you can choose to index only specific events that have
  the '_INDEX_AND_FORWARD_ROUTING' setting configured.
* Configure the '_INDEX_AND_FORWARD_ROUTING' setting in inputs.conf as:
  [<input_stanza>]
  _INDEX_AND_FORWARD_ROUTING = local
* Default: false

[indexer_discovery:<name>]

pass4SymmKey = <string>
* The security key used to communicate between the cluster master
  and the forwarders.
* This value must be the same for all forwarders and the master node.
* You must explicitly set this value for each forwarder.
* If you specify a password here, you must also specify the same password
  on the master node identified by the 'master_uri' setting.

send_timeout = <seconds>
* Low-level timeout for sending messages to the master node.
* Fractional seconds are allowed (for example, 60.95 seconds).
* Default: 30

rcv_timeout = <seconds>
* Low-level timeout for receiving messages from the master node.
* Fractional seconds are allowed (for example, 60.95 seconds).
* Default: 30

cxn_timeout = <seconds>
* Low-level timeout for connecting to the master node.
* Fractional seconds are allowed (for example, 60.95 seconds).
* Default: 30

master_uri = <uri>
* The URI and management port of the cluster master used in indexer discovery.
* For example, https://SplunkMaster01.example.com:8089

####
# Remote Queue Output
####

[remote_queue:<name>]

* This section explains possible settings for configuring a remote queue.
* Each remote_queue stanza represents an individually configured remote
  queue output.

remote_queue.* = <string>
* A way to pass configuration information to a remote storage system.
* Optional.
* With remote queues, communication between the forwarder and the remote queue
  system might require additional configuration, specific to the type of remote
  queue. You can pass configuration information to the storage system by
  specifying this settings through the following schema:
  remote_queue.<scheme>.<config-variable> = <value>.
  For example:
  remote_queue.sqs.access_key = ACCESS_KEY

remote_queue.type = sqs|kinesis
* Currently not supported. This setting is related to a feature that is
  still under development.
* Required.
* Specifies the remote queue type, either SQS or Kinesis.

compressed = <boolean>
* See the description for TCPOUT SETTINGS in outputs.conf.spec.

negotiateProtocolLevel = <unsigned integer>
* See the description for TCPOUT SETTINGS in outputs.conf.spec.

channelReapInterval = <integer>
* See the description for TCPOUT SETTINGS in outputs.conf.spec.

channelTTL = <integer>
* See the description for TCPOUT SETTINGS in outputs.conf.spec.

channelReapLowater = <integer>
* See the description for TCPOUT SETTINGS in outputs.conf.spec.

concurrentChannelLimit = <unsigned integer>
* See the description for [splunktcp] in inputs.conf.spec.

####
# Simple Queue Service (SQS) specific settings
####

remote_queue.sqs.access_key = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The access key to use when authenticating with the remote queue
  system that supports the SQS API.
* If not specified, the forwarder looks for the environment variables
  AWS_ACCESS_KEY_ID or AWS_ACCESS_KEY (in that order). If the environment
  variables are not set and the forwarder is running on EC2, the forwarder
  attempts to use the secret key from the IAM (Identity and Access
  Management) role.
* Default: not set

remote_queue.sqs.secret_key = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Specifies the secret key to use when authenticating with the remote queue
  system supporting the SQS API.
* If not specified, the forwarder looks for the environment variables
  AWS_SECRET_ACCESS_KEY or AWS_SECRET_KEY (in that order). If the environment
  variables are not set and the forwarder is running on EC2, the forwarder
  attempts to use the secret key from the IAM (Identity and Access
  Management) role.
* Default: not set

remote_queue.sqs.auth_region = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The authentication region to use when signing the requests while interacting
  with the remote queue system supporting the Simple Queue Service (SQS) API.
* If not specified and the forwarder is running on EC2, the auth_region is
  constructed automatically based on the EC2 region of the instance where the
  the forwarder is running.
* Default: not set

remote_queue.sqs.endpoint = <URL>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The URL of the remote queue system supporting the Simple Queue Service (SQS) API.
* Use the scheme, either http or https, to enable or disable SSL connectivity
  with the endpoint.
* If not specified, the endpoint is constructed automatically based on the
  auth_region as follows: https://sqs.<auth_region>.amazonaws.com
* If specified, the endpoint must match the effective auth_region, which is
  either a value specified via the 'remote_queue.sqs.auth_region' setting
  or a value constructed automatically based on the EC2 region of the
  running instance.
* Example: https://sqs.us-west-2.amazonaws.com/

remote_queue.sqs.message_group_id = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Specifies the Message Group ID for Amazon Web Services Simple Queue Service
  (SQS) First-In, First-Out (FIFO) queues.
* Setting a Message Group ID controls how messages within an AWS SQS queue are
  processed.
* For information on SQS FIFO queues and how messages in those queues are
  processed, see "Recommendations for FIFO queues" in the AWS SQS Developer
  Guide.
* If you configure this setting, Splunk software assumes that the SQS queue is
  a FIFO queue, and that messages in the queue should be processed first-in,
  first-out.
* Otherwise, Splunk software assumes that the SQS queue is a standard queue.
* Can be between 1-128 alphanumeric or punctuation characters.
* NOTE: FIFO queues must have Content-Based De-duplication enabled.
* Default: not set

remote_queue.sqs.retry_policy = max_count|none
* Sets the retry policy to use for remote queue operations.
* Optional.
* A retry policy specifies whether and how to retry file operations that fail
  for those failures that might be intermittent.
* Retry policies:
  + "max_count": Imposes a maximum number of times a queue operation is
    retried upon intermittent failure. Set max_count with the
    'max_count.max_retries_per_part' setting.
  + "none": Do not retry file operations upon failure.
* Default: max_count

remote_queue.sqs.max_count.max_retries_per_part = <unsigned integer>
* When the 'remote_queue.sqs.retry_policy' setting is "max_count", sets the
  maximum number of times a queue operation will be retried upon intermittent
  failure.
* Optional.
* Default: 9

remote_queue.sqs.timeout.connect = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Sets the connection timeout, in milliseconds, to use when interacting with
  the SQS for this queue.
* Default: 5000

remote_queue.sqs.timeout.read = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Sets the read timeout, in milliseconds, to use when interacting with the
  SQS for this queue.
* Default: 60000

remote_queue.sqs.timeout.write = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Sets the write timeout, in milliseconds, to use when interacting with
  the SQS for this queue.
* Default: 60000

remote_queue.sqs.large_message_store.endpoint = <URL>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The URL of the remote storage system supporting the S3 API.
* Use the scheme, either http or https, to enable or disable SSL connectivity
  with the endpoint.
* If not specified, the endpoint is constructed automatically based on the
  auth_region as follows: https://s3-<auth_region>.amazonaws.com
* If specified, the endpoint must match the effective auth_region, which is
  either a value specified via 'remote_queue.sqs.auth_region' or a value
  constructed automatically based on the EC2 region of the running instance.
* Example: https://s3-us-west-2.amazonaws.com/
* Default: not set

remote_queue.sqs.large_message_store.path = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The remote storage location where messages larger than the underlying
  queue's maximum message size will reside.
* The format for this value is: <scheme>://<remote-location-specifier>
  * The "scheme" identifies a supported external storage system type.
  * The "remote-location-specifier" is an external system-specific string for
    identifying a location inside the storage system.
* The following external systems are supported:
  * Object stores that support AWS's S3 protocol. These stores use the scheme
    "s3". For example, "path=s3://mybucket/some/path".
* If not specified, the queue drops messages exceeding the underlying queue's
  maximum message size.
* Default: not set

remote_queue.sqs.send_interval = <number><unit>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The interval that the remote queue output processor waits for data to
  arrive before sending a partial batch to the remote queue.
* Examples: 30s, 1m
* Default: 30s

remote_queue.sqs.max_queue_message_size = <integer>[KB|MB|GB]
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The maximum message size to which events are batched for upload to
  the remote queue.
* Specify this value as an integer followed by KB, MB, or GB (for example,
  10MB is 10 megabytes)
* Queue messages are sent to the remote queue when the next event processed
  would otherwise result in a message exceeding the maximum message size.
* The maximum value for this setting is 5GB.
* Default: 10MB

remote_queue.sqs.enable_data_integrity_checks = <boolean>
* If "true", Splunk software sets the data checksum in the metadata field of
  the HTTP header during upload operation to S3.
* The checksum is used to verify the integrity of the data on uploads.
* Default: false

remote_queue.sqs.enable_signed_payloads  = <boolean>
* If "true", Splunk software signs the payload during upload operation to S3.
* This setting is valid only for remote.s3.signature_version = v4
* Default: true

####
# Kinesis specific settings
####

remote_queue.kinesis.access_key = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Specifies the access key to use when authenticating with the remote queue
  system supporting the Kinesis API.
* If not specified, the forwarder looks for the environment variables
  AWS_ACCESS_KEY_ID or AWS_ACCESS_KEY (in that order). If the environment
  variables are not set and the forwarder is running on EC2, the forwarder
  attempts to use the secret key from the IAM role.
* Default: not set

remote_queue.kinesis.secret_key = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Specifies the secret key to use when authenticating with the remote queue
  system supporting the Kinesis API.
* If not specified, the forwarder looks for the environment variables
  AWS_SECRET_ACCESS_KEY or AWS_SECRET_KEY (in that order). If the environment
  variables are not set and the forwarder is running on EC2, the forwarder
  attempts to use the secret key from the IAM role.
* Default: not set

remote_queue.kinesis.auth_region = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The authentication region to use when signing the requests when interacting
  with the remote queue system supporting the Kinesis API.
* If not specified and the forwarder is running on EC2, the auth_region is
  constructed automatically based on the EC2 region of the instance where the
  the forwarder is running.
* Default: not set

remote_queue.kinesis.endpoint = <URL>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The URL of the remote queue system supporting the Kinesis API.
* Use the scheme, either http or https, to enable or disable SSL connectivity
  with the endpoint.
* If not specified, the endpoint is constructed automatically based on the
  auth_region as follows: https://kinesis.<auth_region>.amazonaws.com
* If specified, the endpoint must match the effective auth_region, which is
  either a value specified via the 'remote_queue.kinesis.auth_region' setting
  or a value constructed automatically based on the EC2 region of the running instance.
* Example: https://kinesis.us-west-2.amazonaws.com/

remote_queue.kinesis.enable_data_integrity_checks = <boolean>
* If "true", Splunk software sets the data checksum in the metadata field
  of the HTTP header during upload operation to S3.
* The checksum is used to verify the integrity of the data on uploads.
* Default: false

remote_queue.kinesis.enable_signed_payloads  = <boolean>
* If "true", Splunk software signs the payload during upload operation to S3.
* This setting is valid only for remote.s3.signature_version = v4
* Default: true

remote_queue.kinesis.retry_policy = max_count|none
* Sets the retry policy to use for remote queue operations.
* Optional.
* A retry policy specifies whether and how to retry file operations that fail
  for those failures that might be intermittent.
* Retry policies:
  + "max_count": Imposes a maximum number of times a queue operation is
    retried upon intermittent failure. Specify the max_count with the
    'max_count.max_retries_per_part' setting.
  + "none": Do not retry file operations upon failure.
* Default: max_count

remote_queue.kinesis.max_count.max_retries_per_part = <unsigned integer>
* When the 'remote_queue.kinesis.retry_policy' setting is max_count,
  sets the maximum number of times a queue operation is retried
  upon intermittent failure.
* Optional.
* Default: 9

remote_queue.kinesis.timeout.connect = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Sets the connection timeout, in milliseconds, to use when interacting with
  Kinesis for this queue.
* Default: 5000

remote_queue.kinesis.timeout.read = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Sets the read timeout, in milliseconds, to use when interacting with Kinesis
  for this queue.
* Default: 60000

remote_queue.kinesis.timeout.write = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* Sets the write timeout, in milliseconds, to use when interacting with
  Kinesis for this queue.
* Default: 60000

remote_queue.kinesis.large_message_store.endpoint = <URL>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The URL of the remote storage system supporting the S3 API.
* Use the scheme, either http or https, to enable or disable SSL connectivity
  with the endpoint.
* If not specified, the endpoint is constructed automatically based on the
  auth_region as follows: https://s3-<auth_region>.amazonaws.com
* If specified, the endpoint must match the effective auth_region, which is
  either a value specified via 'remote_queue.kinesis.auth_region' or a value
  constructed automatically based on the EC2 region of the running instance.
* Example: https://s3-us-west-2.amazonaws.com/
* Default: not set

remote_queue.kinesis.large_message_store.path = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The remote storage location where messages larger than the underlying
  queue's maximum message size will reside.
* The format for this setting is: <scheme>://<remote-location-specifier>
  * The "scheme" identifies a supported external storage system type.
  * The "remote-location-specifier" is an external system-specific string for
    identifying a location inside the storage system.
* The following external systems are supported:
   * Object stores that support AWS's S3 protocol. These stores use the
     scheme "s3".
     For example, "path=s3://mybucket/some/path".
* If not specified, the queue drops messages exceeding the underlying queue's
  maximum message size.
* Default: not set

remote_queue.kinesis.send_interval = <number><unit>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The interval that the remote queue output processor waits for data to
  arrive before sending a partial batch to the remote queue.
* For example, 30s, 1m
* Default: 30s

remote_queue.kinesis.max_queue_message_size = <integer>[KB|MB|GB]
* Currently not supported. This setting is related to a feature that is
  still under development.
* Optional.
* The maximum message size to which events are batched for upload to the remote
  queue.
* Specify this value as an integer followed by KB or MB (for example, 500KB
  is 500 kilobytes).
* Queue messages are sent to the remote queue when the next event processed
  would otherwise result in the message exceeding the maximum message size.
* The maximum value for this setting is 5GB.
* Default: 10MB
