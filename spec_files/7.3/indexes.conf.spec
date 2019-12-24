#   Version 7.3.0
#
# This file contains all possible options for an indexes.conf file.  Use
# this file to configure Splunk's indexes and their properties.
#
# There is an indexes.conf in $SPLUNK_HOME/etc/system/default/.  To set
# custom configurations, place an indexes.conf in
# $SPLUNK_HOME/etc/system/local/. For examples, see indexes.conf.example.
# You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see
# the documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles
#
# CAUTION:  You can drastically affect your Splunk installation by changing
# these settings.  Consult technical support
# (http://www.splunk.com/page/submit_issue) if you are not sure how to
# configure this file.
#
# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#   * You can also define global settings outside of any stanza, at the top
#     of the file.
#   * Each conf file should have at most one default stanza. If there are
#     multiple default stanzas, settings are combined. In the case of
#     multiple definitions of the same setting, the last definition in the
#     file wins.
#   * If a setting is defined at both the global level and in a specific
#     stanza, the value in the specific stanza takes precedence.

sync = <nonnegative integer>
* The index processor syncs events every 'sync' number of events.
* Set to 0 to disable.
* Highest legal value is 32767.
* Default: 0

defaultDatabase = <index name>
* If an index is not specified during search, Splunk software
  searches the default index.
* The specified index displays as the default in Splunk Manager settings.
* Default: main

bucketMerging = <boolean>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Set to true to enable bucket merging service on all indexes
* You can override this value on a per-index basis.
* Default: false

bucketMerge.minMergeSizeMB = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Minimum cumulative bucket sizes to merge.
* You can override this value on a per-index basis.
* Default: 750

bucketMerge.maxMergeSizeMB = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Maximum cumulative bucket sizes to merge.
* You can override this value on a per-index basis.
* Default: 1000

bucketMerge.maxMergeTimeGapSecs = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Maximum allowed time gap, in seconds, between buckets about to be merged.
* You can override this value on a per-index basis.
* Default: 7776000 (90 days).

queryLanguageDefinition = <path to file>
* DO NOT EDIT THIS SETTING. SERIOUSLY.
* The path to the search language definition file.
* Default: $SPLUNK_HOME/etc/searchLanguage.xml.

lastChanceIndex = <index name>
* An index that receives events that are otherwise not associated
  with a valid index.
* If you do not specify a valid index with this setting, such events are
  dropped entirely.
* Routes the following kinds of events to the specified index:
  * events with a non-existent index specified at an input layer, like an
    invalid "index" setting in inputs.conf
  * events with a non-existent index computed at index-time, like an invalid
    _MetaData:Index value set from a "FORMAT" setting in transforms.conf
* You must set 'lastChanceIndex' to an existing, enabled index.
  Splunk software cannot start otherwise.
* If set to "default", then the default index specified by the
  'defaultDatabase' setting is used as a last chance index.
* Default: empty string

malformedEventIndex = <index name>
* An index to receive malformed events.
* If you do not specify a valid index with this setting, or Splunk software
  cannot use the index specified in the 'defaultDatabase' setting,
  such events are dropped entirely.
* Routes the following kinds of events to the specified index:
    * events destined for read-only indexes
    * log events destined for datatype=metric indexes
    * log events with invalid raw data values, like all-whitespace raw
    * metric events destined for datatype=event indexes
    * metric events with invalid metric values, like non-numeric values
    * metric events lacking required attributes, like metric name
* Malformed events may be modified in order to make them suitable for
  indexing, as well as to aid in debugging.
* A high volume of malformed events can affect search performance against
  the specified index; for example, malformed metric events can lead to an
  excessive number of Strings.data entries
* <index name> must refer to an existing, enabled index. Splunk software
  does not start if this is not the case.
* If set to "default", the indexer places malformed events in the index
  specified by the 'defaultDatabase' setting
* Default: empty string

memPoolMB = <positive integer>|auto
* Determines how much memory is given to the indexer memory pool. This
  restricts the number of outstanding events in the indexer at any given
  time.
* Must be greater than 0; maximum value is 1048576 (which corresponds to 1 TB)
* Setting this too high can cause splunkd memory usage to increase
  significantly.
* Setting this too low can degrade splunkd indexing performance.
* Setting this to "auto" or an invalid value causes splunkd to autotune
  the value as follows:
    * System Memory Available less than ... | 'memPoolMB'
                   1 GB                     |    64  MB
                   2 GB                     |    128 MB
                   8 GB                     |    128 MB
                   8 GB or higher           |    512 MB
* Only set this value if you are an expert user or have been advised to by
  Splunk Support.
* CAUTION: CARELESSNESS IN SETTING THIS CAN LEAD TO PERMANENT BRAIN DAMAGE OR
  LOSS OF JOB.
* Default: auto

indexThreads = <nonnegative integer>|auto
* Determines the number of threads to use for indexing.
* Must be at least 1 and no more than 16.
* This value should not be set higher than the number of processor cores in
  the machine.
* If splunkd is also doing parsing and aggregation, the number should be set
  lower than the total number of processors minus two.
* Setting this to "auto" or an invalid value will cause Splunk to autotune
  this setting.
* Only set this value if you are an expert user or have been advised to by
  Splunk Support.
* CAUTION: CARELESSNESS IN SETTING THIS CAN LEAD TO PERMANENT BRAIN DAMAGE OR
  LOSS OF JOB.
* Default: auto

rtRouterThreads = 0|1
* Set to "1" if you expect to use non-indexed real time searches regularly. Index
  throughput drops rapidly if there are a handful of these running concurrently
  on the system.
* If you are not sure what "indexed vs non-indexed" real time searches are, see
  README of indexed_realtime* settings in limits.conf
* NOTE: This is not a boolean value. Acceptable values are "0" and "1" ONLY.
  At the present time, you can only create a single real-time thread per
  pipeline set.

rtRouterQueueSize = <positive integer>
* This setting is only valid if 'rtRouterThreads' != 0
* This queue sits between the indexer pipeline set thread (producer) and the
  'rtRouterThread'
* Changing the size of this queue can impact real-time search performance.
* Default: 10000

selfStorageThreads = <positive integer>
* Specifies the number of threads used to transfer data to customer-owned remote
  storage.
* The threads are created on demand when any index is configured with
  self storage options.
* Default: 2

assureUTF8 = <boolean>
* Verifies that all data retrieved from the index is proper by validating
  all the byte strings.
  * This does not ensure all data will be emitted, but can be a workaround
    if an index is corrupted in such a way that the text inside it is no
    longer valid utf8.
* Will degrade indexing performance when enabled (set to true).
* Can only be set globally, by specifying in the [default] stanza.
* Default: false

enableRealtimeSearch = <boolean>
* Enables real-time searches.
* Default: true

suppressBannerList = <comma-separated list of strings>
* suppresses index missing warning banner messages for specified indexes
* Default: empty string

maxRunningProcessGroups = <positive integer>
* splunkd runs helper child processes like "splunk-optimize",
  "recover-metadata", etc. This setting limits how many child processes
  can run at any given time.
* This maximum applies to all of splunkd, not per index. If you have N
  indexes, there will be at most 'maxRunningProcessGroups' child processes,
  not N * 'maxRunningProcessGroups' processes.
* Must maintain maxRunningProcessGroupsLowPriority < maxRunningProcessGroups
* This is an advanced setting; do NOT set unless instructed by Splunk
  Support.
* Highest legal value is 4294967295.
* Default: 8

maxRunningProcessGroupsLowPriority = <positive integer>
* Of the 'maxRunningProcessGroups' helper child processes, at most
  'maxRunningProcessGroupsLowPriority' may be low-priority
  (for example, "fsck") ones.
* This maximum applies to all of splunkd, not per index. If you have N
  indexes, there will be at most 'maxRunningProcessGroupsLowPriority'
  low-priority child processes, not N * 'maxRunningProcessGroupsLowPriority'
  processes.
* There must always be fewer 'maxRunningProcessGroupsLowPriority' child
  processes than there are 'maxRunningProcessGroups' child processes.
* This is an advanced setting; do NOT set unless instructed by Splunk
  Support.
* Highest legal value is 4294967295.
* Default: 1

bucketRebuildMemoryHint = <positive integer>[KB|MB|GB]|auto
* A suggestion for the bucket rebuild process for the size, in bytes,
  of the tsidx file it will try to build.
* Larger files use more memory in a rebuild, but rebuilds fail if there is
  not enough memory.
* Smaller files make the rebuild take longer during the final optimize step.
* NOTE: This value is not a hard limit on either rebuild memory usage or
  tsidx size.
* This is an advanced setting, do NOT set this unless instructed by Splunk
  Support.
* If set to "auto", the bucket rebuild process tunes the setting based on
  the amount of physical RAM on the machine:
  *  less than 2GB RAM = 67108864 (64MB) tsidx
  *  2GB to 8GB RAM = 134217728 (128MB) tsidx
  *  more than 8GB RAM = 268435456 (256MB) tsidx
* If not set to "auto", then you must set this setting between 16MB and 1GB.
* A value may be specified using a size suffix: "16777216" or "16MB" are
  equivalent.
* Inappropriate use of this setting causes splunkd to not start if
  rebuild is required.
* Highest legal value (in bytes) is 4294967295.
* Default: auto

inPlaceUpdates = <boolean>
* Whether or not splunkd writes metadata updates to .data files in place.
* Intended for advanced debugging of metadata issues.
* If set to "true", metadata updates are written to the .data files directly.
* If set to "false", metadata updates are written to a temporary file and
  then moved into place.
* Configuring this setting to "false" (to use a temporary file) affects
  indexing performance, particularly with large numbers of hosts, sources,
  or sourcetypes (~1 million, across all indexes.)
* This is an advanced setting; do NOT set unless instructed by Splunk
  Support
* Default: true

serviceInactiveIndexesPeriod = <positive integer>
* How frequently, in seconds, inactive indexes are serviced.
* An inactive index is an index that has not been written to for a period
  greater than the value of 'serviceMetaPeriod'.  The inactive state is not
  affected by whether the index is being read from.
* The highest legal value is 4294967295.
* Default: 60

serviceOnlyAsNeeded = <boolean>
* DEPRECATED; use 'serviceInactiveIndexesPeriod' instead.
* Causes index service (housekeeping tasks) overhead to be incurred only
  after index activity.
* Indexer module problems may be easier to diagnose when this optimization
  is disabled (set to false).
* Default: true

serviceSubtaskTimingPeriod = <positive integer>
* Subtasks of indexer service task will be timed on every Nth execution,
  where N = value of this setting, in seconds.
* Smaller values give greater accuracy; larger values lessen timer
  overhead.
* Timer measurements are found in metrics.log, marked
  "group=subtask_seconds, task=indexer_service"
* Highest legal value is 4294967295
* Configure a value for this setting that divides evenly into the value for
  the 'rotatePeriodInSecs' setting where possible.
* Default: 30

processTrackerServiceInterval = <nonnegative integer>
* How often, in seconds, the indexer checks the status of the child OS
  processes it has launched to see if it can launch new processes for queued
  requests.
* If set to 0, the indexer checks child process status every second.
* Highest legal value is 4294967295.
* Default: 15

maxBucketSizeCacheEntries = <nonnegative integer>
* This value is no longer needed. Its value is ignored.

tsidxStatsHomePath = <string>
* An absolute path that specifies where the indexer creates namespace data
  with the 'tscollect' command.
* If the directory does not exist, the indexer attempts to create it.
* Optional.
* NOTE: The "$SPLUNK_DB" directory must be writable.
* Default: $SPLUNK_DB/tsidxstats

hotBucketTimeRefreshInterval = <positive integer>
* How often each index refreshes the available hot bucket times
  used by the 'indexes' REST endpoint.
* A refresh occurs every N times service is performed for each index.
  * For busy indexes, this is a multiple of seconds.
  * For idle indexes, this is a multiple of the second-long-periods in
    which data is received.
* This setting is only intended to relax the frequency of these refreshes in
  the unexpected case that it adversely affects performance in unusual
  production scenarios.
* This time is tracked on a per-index basis, and thus can be adjusted
  on a per-index basis if needed.
* If you want the index information to be refreshed with
  every service (and accept minor performance overhead), set to 1.
* Default: 10 (services).

#**************************************************************************
# PER INDEX OPTIONS
# These options may be set under an [<index>] entry.
#
# Index names must consist of only numbers, lowercase letters, underscores,
# and hyphens. They cannot begin with an underscore or hyphen, or contain
# the word "kvstore".
#**************************************************************************

disabled = <boolean>
* Toggles your index entry off and on.
* Set to "true" to disable an index.
* Default: false

deleted = true
* If present, means that this index has been marked for deletion: if splunkd
  is running, deletion is in progress; if splunkd is stopped, deletion
  re-commences on startup.
* Do NOT manually set, clear, or modify the value of this setting.
* CAUTION: Seriously: LEAVE THIS SETTING ALONE.
* No default.

homePath = <string>
* An absolute path that contains the hot and warm buckets for the index.
* Best practice is to specify the path with the following syntax:
     homePath = $SPLUNK_DB/$_index_name/db
  At runtime, splunkd expands "$_index_name" to the name of the index. For example,
  if the index name is "newindex", homePath becomes
     "$SPLUNK_DB/newindex/db".
* Splunkd keeps a file handle open for warmdbs at all times.
* May contain a volume reference (see volume section below) in place of $SPLUNK_DB.
* CAUTION: The parent path "$SPLUNK_DB/$_index_name/" must be writable.
* Required. Splunkd does not start if an index lacks a valid 'homePath'.
* You must restart splunkd after changing this setting for the changes to take effect.
* Avoid the use of other environment variables in index paths, aside from the possible
  exception of SPLUNK_DB.
  * As an exception, SPLUNK_DB is explicitly managed by the software,
    so most possible downsides here do not exist.
  * Environment variables can be different from launch to launch of the
    software, causing severe problems with management of indexed data,
    including:
    * Data in the prior location is not searchable.
    * The indexer might not be able to write to the new location, causing outages
      or data loss.
    * Writing to a new, unexpected location could lead to disk space exhaustion
      causing additional operational problems.
    * Recovery from such a scenario requires manual intevention and bucket
      renaming, especially difficult in an index cluster environment.
    * In all circumstances, Splunk Diag, the diagnostic tool that Splunk Support
      uses, has no way to determine the correct values for the environment
      variables, and cannot reliably operate. You might need to manually acquire
      information about your index buckets in troubleshooting scenarios.
  * Volumes provide a more appropriate way to control the
    storage location for indexes.
* No default.

coldPath = <string>
* An absolute path that contains the colddbs for the index.
* Beat practice is to specify the path with the following syntax:
     coldPath = $SPLUNK_DB/$_index_name/colddb
  At runtime, splunkd expands "$_index_name" to the name of the index. For example,
  if the index name is "newindex", 'coldPath'
  becomes "$SPLUNK_DB/newindex/colddb".
* Cold databases are opened as needed when searching.
* May contain a volume reference (see volume section below) in place of $SPLUNK_DB.
* Path must be writable.
* Required. Splunkd does not start if an index lacks a valid 'coldPath'.
* You must restart splunkd after changing this setting for the changes to
  take effect. Reloading the index configuration does not suffice.
* Avoid using environment variables in index paths, aside from the
  possible exception of $SPLUNK_DB. See 'homePath' for additional
  information as to why.
* Remote-storage-enabled indexes do not cycle buckets from homePath to coldPath.
  However, if buckets already reside in 'coldPath' for a
  non-remote-storage-enabled index, and that index is later enabled for remote
  storage, those buckets will be searchable and will have their life cycle
  managed.

thawedPath = <string>
* An absolute path that contains the thawed (resurrected) databases for the
  index.
* May NOT contain a volume reference.
* Path must be writable.
* Required. Splunkd does not start if an index lacks a valid thawedPath.
* You must restart splunkd after changing this setting for the changes to
  take effect. Reloading the index configuration does not suffice.
* Avoid the use of environment variables in index paths, aside from the
  exception of SPLUNK_DB. See 'homePath' for additional information as
  to why.

bloomHomePath = <string>
* The location where the bloomfilter files for the index are stored.
* If specified, 'bloomHomePath' must be defined in terms of a volume definition
  (see volume section below).
* If 'bloomHomePath' is not specified, the indexer stores bloomfilter files
  for the index inline, inside index bucket directories.
* Path must be writable.
* You must restart splunkd after changing this setting for the
  changes to take effect. Reloading the index configuration does
  not suffice.
* Avoid the use of environment variables in index paths, aside from the
  exception of SPLUNK_DB.  See 'homePath' for additional information
  as to why.
* CAUTION: Do not set this setting on indexes that have been
  configured to use remote storage with the "remotePath" setting.

createBloomfilter = <boolean>
* Whether or not to create bloomfilter files for the index.
* If set to "true", the indexer creates bloomfilter files.
* If set to "false", the indexer does not create bloomfilter files.
* You must set to "true" for remote storage enabled indexes.
* CAUTION: Do not set this setting to "false" on indexes that have been
  configured to use remote storage with the "remotePath" setting.
* Default: true

summaryHomePath = <string>
* An absolute path where transparent summarization results for data in this
  index should be stored.
* This value must be different for each index and may be on any disk drive.
* Best practice is to specify the path with the following syntax:
     summaryHomePath = $SPLUNK_DB/$_index_name/summary
  At runtime, splunkd expands "$_index_name" to the name of the index.
  For example, if the index name is "newindex", summaryHomePath becomes
  "$SPLUNK_DB/newindex/summary".
* May contain a volume reference (see volume section below) in place of $SPLUNK_DB.
* Volume reference must be used if you want to retain data based on data size.
* Path must be writable.
* If not specified, splunkd creates a directory 'summary' in the same
  location as 'homePath'.
  * For example, if 'homePath' is "/opt/splunk/var/lib/splunk/index1/db",
    then 'summaryHomePath' must be "/opt/splunk/var/lib/splunk/index1/summary".
* The parent path must be writable.
* You must not set this setting for remote storage enabled indexes.
* You must restart splunkd after changing this setting for the
  changes to take effect. Reloading the index configuration does
  not suffice.
* Avoid the use of environment variables in index paths, aside from the
  exception of SPLUNK_DB. See 'homePath' for additional
  information as to why.
* Default: not set

tstatsHomePath = <string>
* Location where data model acceleration TSIDX data for this index should be stored.
* Required.
* MUST be defined in terms of a volume definition (see volume section below)
* Path must be writable.
* You must not set this setting for remote storage enabled indexes.
* You must restart splunkd after changing this setting for the
  changes to take effect. Reloading the index configuration does
  not suffice.
* Default: volume:_splunk_summaries/$_index_name/datamodel_summary,
  where "$_index_name" is runtime-expanded to the name of the index

remotePath = <root path for remote volume, prefixed by a URI-like scheme>
* Optional.
* Presence of this setting means that this index uses remote storage, instead
  of the local file system, as the main repository for bucket storage. The
  index processor works with a cache manager to fetch buckets locally, as
  necessary, for searching and to evict them from local storage as space fills
  up and they are no longer needed for searching.
* This setting must be defined in terms of a storageType=remote volume
  definition. See the volume section below.
* The path portion that follows the volume reference is relative to the path
  specified for the volume. For example, if the path for a volume "v1" is
  "s3://bucket/path" and 'remotePath' is "volume:v1/idx1", then the fully
  qualified path is "s3://bucket/path/idx1". The rules for resolving the
  relative path with the absolute path specified in the volume can vary
  depending on the underlying storage type.
* If 'remotePath' is specified, the 'coldPath' and 'thawedPath' settings are
  ignored. However, you must still specify them.

maxBloomBackfillBucketAge = <nonnegative integer>[smhd]|infinite
* If a (warm or cold) bucket with no bloomfilter is older than this,
  splunkd does not create a bloomfilter for that bucket.
* When set to 0, splunkd never backfills bloomfilters.
* When set to "infinite", splunkd always backfills bloomfilters.
* NOTE: If 'createBloomfilter' is set to "false", bloomfilters are never
  backfilled regardless of the value of this setting.
* The highest legal value in computed seconds is 2 billion, or 2000000000, which
  is approximately 68 years.
* Default: 30d

hotlist_recency_secs = <unsigned integer>
* The cache manager attempts to defer bucket eviction until the interval
  between the bucket's latest time and the current time exceeds this setting.
* Default: the global setting under server.conf/[cachemanager].

hotlist_bloom_filter_recency_hours = <unsigned integer>
* The cache manager attempts to defer eviction of the non-journal and non-tsidx
  bucket files, such as the bloomfilter file, until the interval between the
  bucket's latest time and the current time exceeds this setting.
* Default: the global setting under server.conf/[cachemanager].

enableOnlineBucketRepair = <boolean>
* Controls asynchronous "online fsck" bucket repair, which runs concurrently
  with splunkd.
* When enabled, you do not have to wait until buckets are repaired, to start
  splunkd.
* When enabled, you might observe a slight degradation in performance.
* You must set to "true" for remote storage enabled indexes.
* Default: true

enableDataIntegrityControl = <boolean>
* Whether or not splunkd computes hashes on rawdata slices and stores the hashes
  for future data integrity checks.
* If set to "true", hashes are computed on the rawdata slices.
* If set to "false", no hashes are computed on the rawdata slices.
* Default: false

maxWarmDBCount = <nonnegative integer>
* The maximum number of warm buckets.
* Warm buckets are located in the 'homePath' for the index.
* If set to zero, splunkd does not retain any warm buckets
  It rolls the buckets to cold as soon as it is able.
* Splunkd ignores this setting on remote storage enabled indexes.
* Highest legal value is 4294967295.
* Default: 300

maxTotalDataSizeMB = <nonnegative integer>
* The maximum size of an index, in megabytes.
* If an index grows larger than the maximum size, splunkd freezes the oldest
  data in the index.
* This setting only applies to hot, warm, and cold buckets. It does
  not apply to thawed buckets.
* CAUTION: This setting takes precedence over other settings like
  'frozenTimePeriodInSecs' with regard to data retention. If the index
  grows beyond 'maxTotalDataSizeMB' megabytes before
  'frozenTimePeriodInSecs' seconds have passed, data could prematurely
  roll to frozen. As the default policy for rolling data to frozen is
  deletion, unintended data loss could occur.
* Splunkd ignores this setting on remote storage enabled indexes.
* Highest legal value is 4294967295
* Default: 500000

maxGlobalRawDataSizeMB = <nonnegative integer>
* The maximum amount of cumulative raw data (in MB) allowed in a remote
  storage-enabled index.
* This setting is available for both standalone indexers and indexer clusters.
  In the case of indexer clusters, the raw data size is calculated as the total
  amount of raw data ingested for the index, across all peer nodes.
* When the amount of uncompressed raw data in an index exceeds the value of this
  setting, the bucket containing the oldest data is frozen.
* For example, assume that the setting is set to 500 and the indexer cluster
  has already ingested 400MB of raw data into the index, across all peer nodes.
  If the cluster ingests an additional amount of raw data greater than 100MB in
  size, the cluster freezes the oldest buckets, until the size of raw data
  reduces to less than or equal to 500MB.
* This value applies to warm and cold buckets. It does not
  apply to hot or thawed buckets.
* The maximum allowable value is 4294967295.
* Default: 0 (no limit to the amount of raw data in an index.)

maxGlobalDataSizeMB = <nonnegative integer>
* The maximum size, in megabytes, for all warm buckets in a SmartStore
  index on a cluster.
* This setting includes the sum of the size of all buckets that reside on
  remote storage, along with any buckets that have recently rolled from hot
  to warm on a peer node and are awaiting upload to remote storage.
* If the total size that the warm buckets of an index occupy exceeds
  'maxGlobalDataSizeMB', the oldest bucket in the index is frozen. For
  example, assume that 'maxGlobalDataSizeMB' is set to 5000 for an index,
  and the index's warm buckets occupy 4800 MB. If a 750 MB hot bucket then
  rolls to warm, the index size now exceeds 'maxGlobalDataSizeMB', triggering
  bucket freezing. The cluster freezes the oldest buckets on the index,
  until the total warm bucket size falls below 'maxGlobalDataSizeMB'.
* The size calculation for this setting applies on a per-index basis.
* The calculation applies across all peers in the cluster.
* The calculation includes only one copy of each bucket. If a duplicate
  copy of a bucket exists on a peer node, the size calculation does not
  include it. For example, if the bucket exists on both remote storage and
  on a peer node's local cache, the calculation ignores the copy
  on local cache.
* The calculation includes only the size of the buckets themselves. It does not
  include the size of any associated files, such as report acceleration
  or data model acceleration summaries.
* The highest legal value is 4294967295.
* Default: 0 (No limit to the space that an index's warm buckets can occupy.)

rotatePeriodInSecs = <positive integer>
* Controls the service period (in seconds): how often splunkd performs
  certain housekeeping tasks. Among these tasks are:
  * Check if a new hot DB needs to be created.
  * Check if there are any cold DBs that should be frozen.
  * Check whether buckets need to be moved out of hot and cold DBs, due to
    respective size constraints (i.e., homePath.maxDataSizeMB and
    coldPath.maxDataSizeMB)
* This value becomes the default value of the 'rotatePeriodInSecs' setting
  for all volumes (see 'rotatePeriodInSecs' in the Volumes section)
* The highest legal value is 4294967295.
* Default: 60

frozenTimePeriodInSecs = <nonnegative integer>
* The number of seconds after which indexed data rolls to frozen.
* If you do not specify a 'coldToFrozenScript', data is deleted when rolled to
  frozen.
* NOTE: Every event in a bucket must be older than 'frozenTimePeriodInSecs'
  seconds before the bucket rolls to frozen.
* The highest legal value is 4294967295.
* Default: 188697600 (6 years).

warmToColdScript = <script path>
* Specifies a script to run when moving data from warm to cold.
* This setting is supported for backwards compatibility with versions
  older than 4.0. Migrating data across filesystems is now handled natively
  by splunkd.
* If you specify a script here, the script becomes responsible for moving
  the event data, and Splunk-native data migration is not used.
* The script must accept two arguments:
  * First: the warm directory (bucket) to be rolled to cold.
  * Second: the destination in the cold path.
* Searches and other activities are paused while the script is running.
* Contact Splunk Support (http://www.splunk.com/page/submit_issue) if you
  need help configuring this setting.
* The script must be in $SPLUNK_HOME/bin or a subdirectory thereof.
* Splunkd ignores this setting for remote storage enabled indexes.
* Default: empty

coldToFrozenScript = <path to script interpreter> <path to script>
* Specifies a script to run when data is to leave the splunk index system.
  * Essentially, this implements any archival tasks before the data is
    deleted out of its default location.
* Add "$DIR" (including quotes) to this setting on Windows (see below
  for details).
* Script Requirements:
  * The script must accept one argument:
    * An absolute path to the bucket directory to archive.
  * Your script should work reliably.
    * If your script returns success (0), Splunk completes deleting
      the directory from the managed index location.
    * If your script return failure (non-zero), Splunk leaves the bucket
      in the index, and tries calling your script again several minutes later.
    * If your script continues to return failure, this will eventually cause
      the index to grow to maximum configured size, or fill the disk.
  * Your script should complete in a reasonable amount of time.
    * If the script stalls indefinitely, it will occupy slots.
    * This script should not run for long as it would occupy
      resources which will affect indexing.
* If the string $DIR is present in this setting, it will be expanded to the
  absolute path to the directory.
* If $DIR is not present, the directory will be added to the end of the
  invocation line of the script.
  * This is important for Windows.
    * For historical reasons, the entire string is broken up by
      shell-pattern expansion rules.
    * Since Windows paths frequently include spaces, and the Windows shell
      breaks on space, the quotes are needed for the script to understand
      the directory.
* If your script can be run directly on your platform, you can specify just
  the script.
  * Examples of this are:
    * .bat and .cmd files on Windows
    * scripts set executable on UNIX with a #! shebang line pointing to a
      valid interpreter.
* You can also specify an explicit path to an interpreter and the script.
    * Example:  /path/to/my/installation/of/python.exe path/to/my/script.py
* This setting must not be used on remote storage enabled indexes.
* Splunk software ships with an example archiving script in that you SHOULD
  NOT USE $SPLUNK_HOME/bin called coldToFrozenExample.py
  * DO NOT USE the example for production use, because:
    * 1 - It will be overwritten on upgrade.
    * 2 - You should be implementing whatever requirements you need in a
          script of your creation. If you have no such requirements, use
          'coldToFrozenDir'
* Example configuration:
  * If you create a script in bin/ called our_archival_script.py, you could use:
    UNIX:
        coldToFrozenScript = "$SPLUNK_HOME/bin/python" \
          "$SPLUNK_HOME/bin/our_archival_script.py"
    Windows:
        coldToFrozenScript = "$SPLUNK_HOME/bin/python" \
          "$SPLUNK_HOME/bin/our_archival_script.py" "$DIR"
* The example script handles data created by different versions of Splunk
  differently. Specifically, data from before version 4.2 and after version 4.2
  are handled differently. See "Freezing and Thawing" below:
* The script must be in $SPLUNK_HOME/bin or a subdirectory thereof.
* No default.

coldToFrozenDir = <path to frozen archive>
* An alternative to a 'coldToFrozen' script - this setting lets you
  specify a destination path for the frozen archive.
* Splunk software automatically puts frozen buckets in this directory
* For information on how buckets created by different versions are
  handled, see "Freezing and Thawing" below.
* If both 'coldToFrozenDir' and 'coldToFrozenScript' are specified,
  'coldToFrozenDir' takes precedence
* You must restart splunkd after changing this setting. Reloading the
  configuration does not suffice.
* May NOT contain a volume reference.
* This setting must not be used on remote storage enabled indexes.

# Freezing and Thawing (this should move to web docs
4.2 and later data:
  * To archive: remove files except for the rawdata directory, since rawdata
    contains all the facts in the bucket.
  * To restore: run splunk rebuild <bucket_dir> on the archived bucket, then
    atomically move the bucket to thawed for that index
4.1 and earlier data:
  * To archive: gzip the .tsidx files, as they are highly compressible but
    cannot be recreated
  * To restore: unpack the tsidx files within the bucket, then atomically
    move the bucket to thawed for that index

compressRawdata = true|false
* This setting is ignored. The splunkd process always compresses raw data.

maxConcurrentOptimizes = <nonnegative integer>
* The number of concurrent optimize processes that can run against a hot
  bucket.
* This number should be increased if:
  * There are always many small tsidx files in the hot bucket.
  * After rolling, there are many tsidx files in warm or cold buckets.
* You must restart splunkd after changing this setting. Reloading the
  configuration does not suffice.
* The highest legal value is 4294967295.
* Default: 6

maxDataSize = <positive integer>|auto|auto_high_volume
* The maximum size, in megabytes, that a hot bucket can reach before splunkd
  triggers a roll to warm.
* Specifying "auto" or "auto_high_volume" will cause Splunk to autotune this
  setting (recommended).
* You should use "auto_high_volume" for high-volume indexes (such as the
  main index); otherwise, use "auto". A "high volume index" would typically
  be considered one that gets over 10GB of data per day.
* "auto_high_volume" sets the size to 10GB on 64-bit, and 1GB on 32-bit
  systems.
* Although the maximum value you can set this is 1048576 MB, which
  corresponds to 1 TB, a reasonable number ranges anywhere from 100 to
  50000. Before proceeding with any higher value, please seek approval of
  Splunk Support.
* If you specify an invalid number or string, maxDataSize will be auto
  tuned.
* NOTE: The maximum size of your warm buckets may slightly exceed
  'maxDataSize', due to post-processing and timing issues with the rolling
  policy.
* For remote storage enabled indexes, consider setting this value to "auto"
  (750MB) or lower.
* Default: "auto" (sets the size to 750 megabytes.)

rawFileSizeBytes = <positive integer>
* Deprecated in version 4.2 and later. Splunkd ignores this value.
* Rawdata chunks are no longer stored in individual files.
* If you really need to optimize the new rawdata chunks (highly unlikely),
  configure the 'rawChunkSizeBytes' setting.

rawChunkSizeBytes = <positive integer>
* Target uncompressed size, in bytes, for individual raw slices in the rawdata
  journal of the index.
* This is an advanced setting. Do not change it unless a Splunk Support
  professional asks you to.
* If you specify "0", 'rawChunkSizeBytes' is set to the default value.
* NOTE: 'rawChunkSizeBytes' only specifies a target chunk size. The actual
  chunk size may be slightly larger by an amount proportional to an
  individual event size.
* You must restart splunkd after changing this setting. Reloading the
  configuration does not suffice.
* The highest legal value is 18446744073709551615
* Default: 131072 (128 kilobytes).

minRawFileSyncSecs = <nonnegative decimal>|disable
* How frequently splunkd forces a filesystem sync while compressing journal
  slices. During this interval, uncompressed slices are left on disk even
  after they are compressed. Splunkd then forces a filesystem sync of the
  compressed journal and remove the accumulated uncompressed files.
* If you specify "0", splunkd forces a filesystem sync after every slice
  completes compressing.
* If you specify "disable", syncing is disabled entirely; uncompressed
  slices are removed as soon as compression is complete.
* Some filesystems are very inefficient at performing sync operations, so
  only enable this if you are sure you need it.
* You must restart splunkd after changing this setting. Reloading the
  configuration does not suffice.
* No exponent may follow the decimal.
* The highest legal value is 18446744073709551615.
* Default: "disable"

maxMemMB = <nonnegative integer>
* The amount of memory, in megabytes, to allocate for indexing.
* This amount of memory will be allocated PER INDEX THREAD, or, if
  indexThreads is set to 0, once per index.
* CAUTION: Calculate this number carefully. splunkd crashes if you set
  this number to higher than the amount of memory available.
* The default is recommended for all environments.
* The highest legal value is 4294967295.
* Default: 5

maxHotSpanSecs = <positive integer>
* Upper bound of timespan of hot/warm buckets, in seconds.
* This is an advanced setting that should be set
  with care and understanding of the characteristics of your data.
* Splunkd applies this limit per ingestion pipeline. For more
  information about multiple ingestion pipelines, see
  'parallelIngestionPipelines' in the server.conf.spec file.
* With N parallel ingestion pipelines, each ingestion pipeline writes to
  and manages its own set of hot buckets, without taking into account the state
  of hot buckets managed by other ingestion pipelines. Each ingestion pipeline
  independently applies this setting only to its own set of hot buckets.
* If you set 'maxHotBuckets' to 1, splunkd attempts to send all
  events to the single hot bucket and does not enforce 'maxHotSpanSeconds'.
* If you set this setting to less than 3600, it will be automatically
  reset to 3600.
* NOTE: If you set this setting to too small a value, splunkd can generate
  a very large number of hot and warm buckets within a short period of time.
* The highest legal value is 4294967295.
* NOTE: the bucket timespan snapping behavior is removed from this setting.
  See the 6.5 spec file for details of this behavior.
* Default: 7776000 (90 days).

maxHotIdleSecs = <nonnegative integer>
* How long, in seconds, that a hot bucket can remain in hot status without
  receiving any data.
* If a hot bucket receives no data for more than 'maxHotIdleSecs' seconds,
  splunkd rolls the bucket to warm.
* This setting operates independently of 'maxHotBuckets', which can also cause
  hot buckets to roll.
* A value of 0 turns off the idle check (equivalent to infinite idle time).
* The highest legal value is 4294967295
* Default: 0

maxHotBuckets = <positive integer>
* Maximum number of hot buckets that can exist per index.
* When 'maxHotBuckets' is exceeded, Splunk rolls the least recently used (LRU)
  hot bucket to warm.
* Both normal hot buckets and quarantined hot buckets count towards this
  total.
* This setting operates independently of maxHotIdleSecs, which can also
  cause hot buckets to roll.
* NOTE: Splunkd applies this limit per ingestion pipeline. For more
  information about multiple ingestion pipelines, see
  'parallelIngestionPipelines' in the server.conf.spec file.
* With N parallel ingestion pipelines, the maximum number of hot buckets across
  all of the ingestion pipelines is N * 'maxHotBuckets', but only
  'maxHotBuckets' for each ingestion pipeline. Each ingestion pipeline
  independently writes to and manages up to 'maxHotBuckets' number of hot
  buckets. As a consequence of this, when multiple ingestion pipelines are
  used, there may be multiple (dependent on number of ingestion pipelines
  configured) hot buckets with events with overlapping time ranges.
* The highest legal value is 4294967295
* Default: 3

minHotIdleSecsBeforeForceRoll = <nonnegative integer>|auto
* When there are no existing hot buckets that can fit new events because of
  their timestamps and the constraints on the index (refer to 'maxHotBuckets',
  'maxHotSpanSecs' and 'quarantinePastSecs'), if any hot bucket has been idle
  (not receiving any data) for 'minHotIdleSecsBeforeForceRoll' seconds,
  a new bucket is created to receive these new events and the
  idle bucket is rolled to warm.
* If no hot bucket has been idle for 'minHotIdleSecsBeforeForceRoll' seconds,
  or if 'minHotIdleSecsBeforeForceRoll' has been set to 0, then a best fit
  bucket is chosen for these new events from the existing set of hot buckets.
* This setting operates independently of 'maxHotIdleSecs', which causes hot
  buckets to roll after they have been idle for 'maxHotIdleSecs' seconds,
  regardless of whether new events can fit into the existing hot buckets or not
  due to an event timestamp. 'minHotIdleSecsBeforeForceRoll', on the other hand,
  controls a hot bucket roll only under the circumstances when the timestamp
  of a new event cannot fit into the existing hot buckets given the other
  setting constraints on the system (such as 'maxHotBuckets',
  'maxHotSpanSecs', and 'quarantinePastSecs').
* If you specify "auto", splunkd autotunes this setting.
  The value begins at 600 and automatically adjusts upwards for
  optimal performance. Specifically, the value increases when a hot bucket rolls
  due to idle time with a significantly smaller size than 'maxDataSize'. As a
  consequence, the outcome might be fewer buckets, though these buckets might
  span wider earliest-latest time ranges of events.
* If you specify a value of "0", splunkd turns off the idle check
  (this is equivalent to infinite idle time).
* Setting this to zero means that splunkd never rolls a hot bucket as a
  consequence of an event not fitting into an existing hot bucket due to the
  constraints of other settings. Instead, it finds a best fitting
  bucket to accommodate that event.
* The highest legal value is 4294967295.
* NOTE: If you configure this setting, there is a chance that this could
  lead to frequent hot bucket rolls to warm, depending on the value. If your
  index contains a large number of buckets whose size on disk falls
  considerably short of the size specified in 'maxDataSize', and if the reason
  for the roll of these buckets is due to "caller=lru", then configuring the
  setting value to a larger value or to zero might reduce the frequency of hot
  bucket rolls (see the "auto" value above). You can check splunkd.log for a
  message like the following for rolls due to this setting:
    INFO  HotBucketRoller - finished moving hot to warm
      bid=_internal~0~97597E05-7156-43E5-85B1-B0751462D16B idx=_internal
      from=hot_v1_0 to=db_1462477093_1462477093_0 size=40960 caller=lru
      maxHotBuckets=3, count=4 hot buckets,evicting_count=1 LRU hots
* Default: "auto"

splitByIndexKeys = <comma separated list>
* By default, splunkd splits buckets by time ranges with each bucket having its
  earliest and latest time.
* If one or several keys are provided, splunkd splits buckets by the index key,
  or a combination of the index keys if more than one key is provided. The
  buckets will no longer be split by time ranges.
* Valid values are: host, sourcetype, source, metric_name
* This setting only applies to metric indexes.
* If not set, splunkd splits buckets by time span.
* Default: empty string (no key).

quarantinePastSecs = <positive integer>
* Determines what constitutes an anomalous past timestamp for quarantining
  purposes.
* If an event has a timestamp of 'quarantinePastSecs' older than the
  current time ("now"), the indexer puts that event in the quarantine bucket.
* This is a mechanism to prevent the main hot buckets from being polluted
  with fringe events.
* The highest legal value is 4294967295
* Default: 77760000 (900 days).

quarantineFutureSecs = <positive integer>
* Determines what constitutes an anomalous future timestamp for quarantining
  purposes.
* If an event has a timestamp of 'quarantineFutureSecs' newer than the
  current time ("now"), the indexer puts that event in the quarantine bucket.
* This is a mechanism to prevent the main hot buckets from being polluted with
  fringe events.
* The highest legal value is 4294967295
* Default: 2592000 (30 days).

maxMetaEntries = <nonnegative integer>
* The maximum number of unique lines in .data files in a bucket, which
  might help to reduce memory consumption
* If this value is exceeded, a hot bucket is rolled to prevent further increase
* If your buckets are rolling due to Strings.data hitting this limit, the
  culprit might be the 'punct' field in your data. If you do not use 'punct',
  it might be best to simply disable this (see props.conf.spec)
  * NOTE: since at least 5.0.x, large strings.data from usage of punct are rare.
* There is a delta between when 'maxMetaEntries' is exceeded and splunkd rolls
  the bucket.
* This means a bucket might end up with more lines than specified in
  'maxMetaEntries', but this is not a major concern unless that excess
  is significant.
* If set to 0, splunkd ignores this setting (it is treated as infinite)
* Highest legal value is 4294967295.
* No default.

syncMeta = <boolean>
* Whether or not splunkd calls a sync operation before the file descriptor
  is closed on metadata file updates.
* When set to "true", splunkd calls a sync operation before it closes the
  file descriptor on metadata file updates.
* This functionality was introduced to improve integrity of metadata files,
  especially in regards to operating system crashes/machine failures.
* NOTE: Do not change this setting without the input of a Splunk support
  professional.
* You must restart splunkd after changing this setting. Reloading the
  configuration does not suffice.
* Default: true

serviceMetaPeriod = <positive integer>
* Defines how frequently, in seconds, that metadata is synced to disk.
* You might want to set this to a higher value if the sum of your metadata
  file sizes is larger than many tens of megabytes, to avoid the hit on I/O
  in the indexing fast path.
* The highest legal value is 4294967295
* Default: 25

partialServiceMetaPeriod = <positive integer>
* The amount of time, in seconds, that splunkd syncs metadata for records that
  can be synced efficiently in place without requiring a full rewrite of the
  metadata file.
* Related to 'serviceMetaPeriod'. Records that require a full rewrite of the
  metadata file are synced every 'serviceMetaPeriod' seconds.
* If you set this to 0, the feature is turned off, and 'serviceMetaPeriod'
  is the only time when metadata sync happens.
* If the value of 'partialServiceMetaPeriod' is greater than
  the value of 'serviceMetaPeriod', this setting has no effect.
* Splunkd ignores this setting if 'serviceOnlyAsNeeded' = "true" (the default).
* The highest legal value is 4294967295.
* Default: 0 (disabled).

throttleCheckPeriod = <positive integer>
* How frequently, in seconds, that splunkd checks for index throttling
  conditions.
* NOTE: Do not change this setting unless a Splunk Support
  professional asks you to.
* The highest legal value is 4294967295.
* Default: 15

maxTimeUnreplicatedWithAcks = <nonnegative decimal>
* How long, in seconds, that events can remain in an unacknowledged state
  within a raw slice.
* This value is important if you have enabled indexer acknowledgment on
  forwarders by configuring the 'useACK' setting in outputs.conf and
  have enabled replication through indexer clustering.
* This is an advanced setting. Confirm that you understand the settings
  on all your forwarders before changing it.
    * Do not exceed the ack timeout configured on any forwarders.
    * Set to a number that is at most half of the minimum value of that timeout.
  Review the 'readTimeout' setting in the [tcpout] stanza in outputs.conf.spec
  for information about the ack timeout.
* Configuring this setting to 0 disables the check. Do not do this.
* The highest legal value is 2147483647.
* Default: 60

maxTimeUnreplicatedNoAcks = <nonnegative decimal>
* How long, in seconds, that events can remain in a raw slice.
* This setting is important only if replication is enabled for this index,
  otherwise it is ignored.
* If there are any acknowledged events that share this raw slice, this setting
  does not apply. Instead, splunkd uses the value in the
  'maxTimeUnreplicatedWithAcks' setting.)
* The highest legal value is 2147483647.
* Configuring this setting to 0 disables the check.
* Do not configure this setting on remote storage enabled indexes.
* NOTE: Take care and understand the consequences before changing this setting.
* Default: 300

isReadOnly = <boolean>
* Whether or not the index is read-only.
* If you set to "true", no new events can be added to the index, but the
  index is still searchable.
* You must restart splunkd after changing this setting. Reloading the
  index configuration does not suffice.
* Do not configure this setting on remote storage enabled indexes.
* Default: false

homePath.maxDataSizeMB = <nonnegative integer>
* Specifies the maximum size of 'homePath' (which contains hot and warm
  buckets).
* If this size is exceeded, splunkd moves buckets with the oldest value
  of latest time (for a given bucket) into the cold DB until homePath is
  below the maximum size.
* If you set this setting to 0, or do not set it, splunkd does not constrain the
  size of 'homePath'.
* The highest legal value is 4294967295.
* Splunkd ignores this setting for remote storage enabled indexes.
* Default: 0

coldPath.maxDataSizeMB = <nonnegative integer>
* Specifies the maximum size of 'coldPath' (which contains cold buckets).
* If this size is exceeded, splunkd freezes buckets with the oldest value
  of latest time (for a given bucket) until coldPath is below the maximum
  size.
* If you set this setting to 0, or do not set it, splunkd does not constrain the
  size of 'coldPath'.
* If splunkd freezes buckets due to enforcement of this setting, and
  'coldToFrozenScript' and/or 'coldToFrozenDir' archiving settings are also
  set on the index, these settings are used.
* Splunkd ignores this setting for remote storage enabled indexes.
* The highest legal value is 4294967295.
* Default: 0

disableGlobalMetadata = <boolean>
* NOTE: This option was introduced in version 4.3.3, but as of 5.0 it
  is obsolete and splunkd ignores it if you set it.
* It used to disable writing to the global metadata. In 5.0,  global metadata
  was removed.

repFactor = 0|auto
* Valid only for indexer cluster peer nodes.
* Determines whether an index gets replicated.
* Configuring this setting to 0 turns off replication for this index.
* Configuring to "auto" turns on replication for this index.
* You must configure this setting to the same value on all peer nodes.
* Default: 0

minStreamGroupQueueSize = <nonnegative integer>
* Minimum size of the queue that stores events in memory before committing
  them to a tsidx file.
* As splunkd operates, it continually adjusts this size internally. Splunkd
  could decide to use a small queue size and thus generate tiny tsidx files
  under certain unusual circumstances, such as file system errors.  The
  danger of a very low minimum is that it can generate very tiny tsidx files
  with one or very few events, making it impossible for splunk-optimize to
  catch up and optimize the tsidx files into reasonably sized files.
* Do not configure this setting unless a Splunk Support professional
  asks you to.
* The highest legal value is 4294967295.
* Default: 2000

streamingTargetTsidxSyncPeriodMsec = <nonnegative integer>
* The amount of time, in milliseconds, that splunkd forces a sync
  of tsidx files on streaming targets.
* This setting is needed for multisite clustering where streaming targets
  might be primary.
* If you configure this setting to 0, syncing of tsidx files on
  streaming targets does not occur.
* No default.

journalCompression = gzip|lz4|zstd
* The compression algorthm that splunkd should use for the rawdata journal
  file of new index buckets.
* This setting does not have any effect on already created buckets. There is
  no problem searching buckets that are compressed with different algorithms.
* "zstd" is only supported in Splunk Enterprise version 7.2.x and higher. Do
  not enable that compression format if you have an indexer cluster where some
  indexers run an earlier version of Splunk Enterprise.
* Default: gzip

enableTsidxReduction = <boolean>
* Whether or not the tsidx reduction capability is enabled.
* By enabling this setting, you turn on the tsidx reduction capability.
  This causes the indexer to reduce the tsidx files of buckets when the
  buckets reach the age specified  by 'timePeriodInSecBeforeTsidxReduction'.
* CAUTION: Do not set this setting to "true" on indexes that have been
  configured to use remote storage with the "remotePath" setting.
* Default: false

tsidxWritingLevel = [1|2|3]
* Enables various performance and space-saving improvements for tsidx files.
* For deployments that do not have multi-site index clustering enabled,
    set this to the highest value possible for all your indexes.
  * For deploments that have multi-site index clustering, only set
    this to the highest level possible AFTER all your indexers in the
    cluster have been upgraded to the latest code level.
  * Do not configure indexers with different values for 'tsidxWritingLevel'
    as downlevel indexers cannot read tsidx files created from uplevel peers.
  * The higher settings take advantage of newer tsidx file formats for
    metrics and log events that decrease storage cost and increase performance
* Default: 1

suspendHotRollByDeleteQuery = <boolean>
* Whether or not splunkd rolls hot buckets upon running of the "delete"
  search command, or waits to roll them for other reasons.
* When the "delete" search command is run, all buckets that contain data
  to be deleted are marked for updating of their metadata files. The indexer
  normally first rolls any hot buckets as rolling must precede the metadata
  file updates.
* When 'suspendHotRollByDeleteQuery' is set to "true", the rolling of hot
  buckets for the "delete" command is suspended. The hot buckets, although
  marked, do not roll immediately, but instead wait to roll in response to
  the same circumstances operative for any other hot buckets; for example,
  due to reaching a limit set by 'maxHotBuckets', 'maxDataSize', etc. When
  these hot buckets finally roll, their metadata files are then updated.
* Default: false

tsidxReductionCheckPeriodInSec = <positive integer>
* The amount of time, in seconds, between service runs to reduce the tsidx
  files for any buckets that have reached the age specified by
  'timePeriodInSecBeforeTsidxReduction'.
* Default: 600

timePeriodInSecBeforeTsidxReduction = <positive integer>
* The amount of time, in seconds, that a bucket can age before it
  becomes eligible for tsidx reduction.
* The bucket age is the difference between the current time
  and the timestamp of the bucket's latest event.
* When this time difference is exceeded, a bucket becomes eligible
  for tsidx reduction.
* Default: 604800

datatype = <event|metric>
* Determines whether the index stores log events or metric data.
* If set to "metric", the indexer optimizes the index to store metric
  data which can be  queried later only using the 'mstats' operator,
  as searching metric data is different from traditional log events.
* Use the "metric" data type only for metric sourcetypes like statsd.
* Optional.
* Default: event

#**************************************************************************
# PER PROVIDER FAMILY OPTIONS
# A provider family is a way of collecting properties that are common to
# multiple providers. There are no properties that can only be used in a
# provider family, and not in a provider. If the same property is specified
# in a family, and in a provider belonging to that family, then the latter
# value "wins".
#
# All family stanzas begin with "provider-family:". For example:
# [provider-family:family_name]
# vix.mode=stream
# vix.command = java
# vix.command.arg.1 = -Xmx512m
# ....
#**************************************************************************

#**************************************************************************
# PER PROVIDER OPTIONS
# These options affect External Resource Providers (ERPs). All provider stanzas
# begin with "provider:". For example:
#   [provider:provider_name]
#   vix.family                  = hadoop
#   vix.env.JAVA_HOME           = /path/to/java/home
#   vix.env.HADOOP_HOME         = /path/to/hadoop/client/libraries
#
# Each virtual index must reference a provider.
#**************************************************************************
vix.family = <family>
* A provider family to which this provider belongs.
* The only family available by default is "hadoop". Others may be added.

vix.mode = stream|report
* Usually specified at the family level.
* Typically should be "stream".
* In general, do not use "report" without consulting Splunk Support.

vix.command = <command>
* The command to be used to launch an external process for searches on this
  provider.
* Usually specified at the family level.

vix.command.arg.<N> = <argument>
* The Nth argument to the command specified by vix.command.
* Usually specified at the family level, but frequently overridden at the
  provider level, for example to change the jars used depending on the
  version of Hadoop to which a provider connects.

vix.<property name> = <property value>
* All such properties will be made available as "configuration properties" to
  search processes on this provider.
* For example, if this provider is in the Hadoop family, the configuration
  property "mapreduce.foo = bar" can be made available to the Hadoop
  via the property "vix.mapreduce.foo = bar".

vix.env.<env var name> = <env var variable>
* Will create an environment variable available to search processes on this
  provider.
* For example, to set the JAVA_HOME variable to "/path/java" for search
  processes on this provider, use "vix.env.JAVA_HOME = /path/java".

#**************************************************************************
# PER PROVIDER OPTIONS -- HADOOP
# These options are specific to ERPs with the Hadoop family.
# NOTE: Many of these properties specify behavior if the property is not
#       set. However, default values set in system/default/indexes.conf
#       take precedence over the "unset" behavior.
#**************************************************************************

vix.javaprops.<JVM system property name> = <value>
* All such properties will be used as Java system properties.
* For example, to specify a Kerberos realm (say "foo.com") as a Java
  system property, use the property
  "vix.javaprops.java.security.krb5.realm = foo.com".

vix.mapred.job.tracker = <logical name or server:port>
* In high-availability mode, use the logical name of the Job Tracker.
* Otherwise, should be set to server:port for the single Job Tracker.
* Note: this property is passed straight to Hadoop. Not all such properties
  are documented here.

vix.fs.default.name = <logical name or hdfs://server:port>
* In high-availability mode, use the logical name for a list of Name Nodes.
* Otherwise, use the URL for the single Name Node.
* Note: this property is passed straight to Hadoop. Not all such properties
  are documented here.

vix.splunk.setup.onsearch = true|false
* Whether to perform setup (install & bundle replication) on search.
* Default: false

vix.splunk.setup.package = current|<path to file>
* Splunk .tgz package to install and use on data nodes
  (in vix.splunk.home.datanode).
* Uses the current install if set to value 'current' (without quotes).

vix.splunk.home.datanode = <path to dir>
* Path to where splunk should be installed on datanodes/tasktrackers, i.e.
  SPLUNK_HOME.
* Required.

vix.splunk.home.hdfs = <path to dir>
* Scratch space for this Splunk instance on HDFS
* Required.

vix.splunk.search.debug = true|false
* Whether to run searches against this index in debug mode. In debug mode,
  additional information is logged to search.log.
* Optional.
* Default: false

vix.splunk.search.recordreader = <list of classes>
* Comma separated list of data preprocessing classes.
* Each such class must extend BaseSplunkRecordReader and return data to be
  consumed by Splunk as the value.

vix.splunk.search.splitter = <class name>
* Set to override the class used to generate splits for MR jobs.
* Classes must implement com.splunk.mr.input.SplitGenerator.
* Unqualified classes will be assumed to be in the package com.splunk.mr.input.
* May be specified in either the provider stanza, or the virtual index stanza.
* To search Parquet files, use ParquetSplitGenerator.
* To search Hive files, use HiveSplitGenerator.

vix.splunk.search.mr.threads = <postive integer>
* Number of threads to use when reading map results from HDFS
* Numbers less than 1 will be treated as 1.
* Numbers greater than 50 will be treated as 50.
* Default: 10

vix.splunk.search.mr.maxsplits = <positive integer>
* Maximum number of splits in an MR job.
* Default: 10000

vix.splunk.search.mr.minsplits = <positive integer>
* Number of splits for first MR job associated with a given search.
* Default: 100

vix.splunk.search.mr.splits.multiplier = <decimal greater than or equal to 1.0>
* Factor by which the number of splits is increased in consecutive MR jobs for
  a given search, up to the value of maxsplits.
* Default: 10

vix.splunk.search.mr.poll = <positive integer>
* Polling period for job status, in milliseconds.
* Default: 1000 (1 second).

vix.splunk.search.mr.mapper.output.replication = <positive integer>
* Replication level for mapper output.
* Default: 3

vix.splunk.search.mr.mapper.output.gzlevel = <integer between 0 and 9, inclusive>
* The compression level used for the mapper output.
* Default: 2

vix.splunk.search.mixedmode = <boolean>
* Whether mixed mode execution is enabled.
* Default: true

vix.splunk.search.mixedmode.maxstream = <nonnegative integer>
* Maximum number of bytes to stream during mixed mode.
* Value = 0 means there's no stream limit.
* Will stop streaming after the first split that took the value over the limit.
* Default: 10737418240 (10 GB).

vix.splunk.jars = <list of paths>
* Comma delimited list of Splunk dirs/jars to add to the classpath in the
  Search Head and MR.

vix.env.HUNK_THIRDPARTY_JARS = <list of paths>
* Comma delimited list of 3rd-party dirs/jars to add to the classpath in the
  Search Head and MR.

vix.splunk.impersonation = true|false
* Enable/disable user impersonation.

vix.splunk.setup.bundle.replication = <positive integer>
* Set custom replication factor for bundles on HDFS.
* Must be an integer between 1 and 32767.
* Increasing this setting may help performance on large clusters by decreasing
  the average access time for a bundle across Task Nodes.
* Optional.
* If not set, the default replication factor for the file-system applies.

vix.splunk.setup.bundle.max.inactive.wait = <positive integer>
* A positive integer represent a time interval in seconds.
* While a task waits for a bundle being replicated to the same node by another
  task, if the bundle file is not modified for this amount of time, the task
  will begin its own replication attempt.
* Default: 5

vix.splunk.setup.bundle.poll.interval = <positive integer>
* A positive number, representing a time interval in milliseconds.
* While a task waits for a bundle to be installed by another task on the same
  node, it will check once per interval whether that installation is complete.
* Default: 100

vix.splunk.setup.bundle.setup.timelimit = <positive integer>
* A positive number, representing a time duration in milliseconds.
* A task will wait this long for a bundle to be installed before it quits.
* Default: 20000 (20 seconds).

vix.splunk.setup.package.replication = true|false
* Set custom replication factor for the Splunk package on HDFS. This is the
  package set in the property vix.splunk.setup.package.
* Must be an integer between 1 and 32767.
* Increasing this setting may help performance on large clusters by decreasing
  the average access time for the package across Task Nodes.
* Optional. If not set, the default replication factor for the file-system
  will apply.

vix.splunk.setup.package.max.inactive.wait = <positive integer>
* A positive integer represent a time interval in seconds.
* While a task waits for a Splunk package being replicated to the same node by
  another task, if the package file is not modified for this amount of time,
  the task will begin its own replication attempt.
* Default: 5

vix.splunk.setup.package.poll.interval = <positive integer>
* A positive number, representing a time interval in milliseconds.
* While a task waits for a Splunk package to be installed by another task on
  the same node, it will check once per interval whether that installation is
  complete.
* Default: 100

vix.splunk.setup.package.setup.timelimit = <positive integer>
* A positive number, representing a time duration in milliseconds.
* A task will wait this long for a Splunk package to be installed before it quits.
* Default: 20000 (20 seconds).

vix.splunk.setup.bundle.reap.timelimit = <positive integer>
* Specific to Hunk provider
* For bundles in the working directory on each data node, this property controls
  how old they must be before they are eligible for reaping.
* Unit is milliseconds
* Values larger than 86400000 will be treated as if set to 86400000.
* Default: 86400000 (24 hours).

vix.splunk.search.column.filter = <boolean>
* Enables/disables column filtering. When enabled, Hunk will trim columns that
  are not necessary to a query on the Task Node, before returning the results
  to the search process.
* Should normally increase performance, but does have its own small overhead.
* Works with these formats: CSV, Avro, Parquet, Hive.
* Default: true

#
# Kerberos properties
#

vix.kerberos.principal = <kerberos principal name>
* Specifies principal for Kerberos authentication.
* Should be used with vix.kerberos.keytab and either
  1) vix.javaprops.java.security.krb5.realm and
     vix.javaprops.java.security.krb5.kdc, or
  2) security.krb5.conf

vix.kerberos.keytab = <kerberos keytab path>
* Specifies path to keytab for Kerberos authentication.
* See usage note with vix.kerberos.principal.


#
# The following properties affect the SplunkMR heartbeat mechanism. If this
# mechanism is turned on, the SplunkMR instance on the Search Head updates a
# heartbeat file on HDFS. Any MR job spawned by report or mix-mode searches
# checks the heartbeat file. If it is not updated for a certain time, it will
# consider SplunkMR to be dead and kill itself.
#

vix.splunk.heartbeat = <boolean>
* Turn on/off heartbeat update on search head, and checking on MR side.
* Default: true

vix.splunk.heartbeat.path = <path on HDFS>
* Path to heartbeat file.
* If not set, defaults to <vix.splunk.home.hdfs>/dispatch/<sid>/

vix.splunk.heartbeat.interval = <positive integer>
* The frequency, in milliseconds, with which the Heartbeat will be updated
  on the Search Head.
* Minimum value is 1000. Smaller values will cause an exception to be thrown.
* Default: 6000 (6 seconds).

vix.splunk.heartbeat.threshold = <positive integer>
* The number of times the MR job will detect a missing heartbeat update before
  it considers SplunkMR dead and kills itself.
* Default: 10

## The following sections are specific to data input types.

#
# Sequence file
#

vix.splunk.search.recordreader.sequence.ignore.key = <boolean>
* When reading sequence files, if this key is enabled, events will be expected
  to only include a value. Otherwise, the expected representation is
  key+"\t"+value.
* Default: true

#
# Avro
#

vix.splunk.search.recordreader.avro.regex = <regex>
* Regex that files must match in order to be considered avro files.
* Optional.
* Default: \.avro$

#
# Parquet
#

vix.splunk.search.splitter.parquet.simplifyresult = <boolean>
* If enabled, field names for map and list type fields will be simplified by
  dropping intermediate "map" or "element" subfield names. Otherwise, a field
  name will match parquet schema completely.
* May be specified in either the provider stanza or in the virtual index stanza.
* Default: true

#
# Hive
#

vix.splunk.search.splitter.hive.ppd = <boolean>
* Enable or disable Hive ORC Predicate Push Down.
* If enabled, ORC PPD will be applied whenever possible to prune unnecessary
  data as early as possible to optimize the search.
* May be specified in either the provider stanza or in the virtual index stanza.
* Default: true

vix.splunk.search.splitter.hive.fileformat = textfile|sequencefile|rcfile|orc
* Format of the Hive data files in this provider.
* May be specified in either the provider stanza or in the virtual index stanza.
* Default: "textfile".

vix.splunk.search.splitter.hive.dbname = <DB name>
* Name of Hive database to be accessed by this provider.
* Optional.
* May be specified in either the provider stanza or in the virtual index stanza.
* Default: "default".

vix.splunk.search.splitter.hive.tablename = <table name>
* Table accessed by this provider.
* Required property.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.columnnames = <list of column names>
* Comma-separated list of file names.
* Required if using Hive, not using metastore.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.columntypes = string:float:int # COLON separated list of column types, required
* Colon-separated list of column- types.
* Required if using Hive, not using metastore.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.serde = <SerDe class>
* Fully-qualified class name of SerDe.
* Required if using Hive, not using metastore, and if specified in creation of Hive table.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.serde.properties = <list of key-value pairs>
* Comma-separated list of "key=value" pairs.
* Required if using Hive, not using metastore, and if specified in creation of Hive table.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.fileformat.inputformat = <InputFormat class>
* Fully-qualified class name of an InputFormat to be used with Hive table data.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.rowformat.fields.terminated = <delimiter>
* Will be set as the Hive SerDe property "field.delim".
* Optional.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.rowformat.escaped = <escape char>
* Will be set as the Hive SerDe property "escape.delim".
* Optional.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.rowformat.lines.terminated = <delimiter>
* Will be set as the Hive SerDe property "line.delim".
* Optional.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.rowformat.mapkeys.terminated  = <delimiter>
* Will be set as the Hive SerDe property "mapkey.delim".
* Optional.
* May be specified in either the provider stanza or in the virtual index stanza.

vix.splunk.search.splitter.hive.rowformat.collectionitems.terminated = <delimiter>
* Will be set as the Hive SerDe property "colelction.delim".
* Optional.
* May be specified in either the provider stanza or in the virtual index stanza.

#
# Archiving
#

vix.output.buckets.max.network.bandwidth = 0|<bits per second>
* Throttles network bandwidth to <bits per second>
* Set at provider level. Applied to all virtual indexes using a provider
  with this setting.
* Default: 0 (no throttling).

#**************************************************************************
# PER VIRTUAL INDEX OPTIONS
# These options affect virtual indexes. Like indexes, these options may
# be set under an [<virtual-index>] entry.
#
# Virtual index names have the same constraints as normal index names.
#
# Each virtual index must reference a provider. I.e:
# [virtual_index_name]
# vix.provider = <provider_name>
#
# All configuration keys starting with "vix." will be passed to the
# external resource provider (ERP).
#**************************************************************************

vix.provider = <provider_name>
* Name of the external resource provider to use for this virtual index.

#**************************************************************************
# PER VIRTUAL INDEX OPTIONS -- HADOOP
# These options are specific to ERPs with the Hadoop family.
#**************************************************************************

#
# The vix.input.* configurations are grouped by an id.
# Inputs configured via the UI always use '1' as the id.
# In this spec we'll use 'x' as the id.
#

vix.input.x.path = <path>
* Path in a hadoop filesystem (usually HDFS or S3).
* May contain wildcards.
* Checks the path for data recursively when ending with '...'
* Can extract fields with ${field}. I.e: "/data/${server}/...", where server
  will be extracted.
* May start with a schema.
  * The schema of the path specifies which hadoop filesystem implementation to
    use. Examples:
    * hdfs://foo:1234/path, will use a HDFS filesystem implementation
    * s3a://s3-bucket/path, will use a S3 filesystem implementation

vix.input.x.accept = <regex>
* Specifies a whitelist regex.
* Only files within the location given by matching vix.input.x.path, whose
  paths match this regex, will be searched.

vix.input.x.ignore = <regex>
* Specifies a blacklist regex.
* Searches will ignore paths matching this regex.
* These matches take precedence over vix.input.x.accept matches.

vix.input.x.required.fields = <comma separated list of fields>
* Fields that will be kept in search results even if the field is not
  required by the search

# Earliest time extractions - For all 'et' settings, there's an equivalent 'lt' setting.
vix.input.x.et.regex = <regex>
* Regex extracting earliest time from vix.input.x.path

vix.input.x.et.format = <java.text.SimpleDateFormat date pattern>
* Format of the extracted earliest time.
* See documentation for java.text.SimpleDateFormat

vix.input.x.et.offset = <seconds>
* Offset in seconds to add to the extracted earliest time.

vix.input.x.et.timezone = <java.util.SimpleTimeZone timezone id>
* Timezone in which to interpret the extracted earliest time.
* Examples: "America/Los_Angeles" or "GMT-8:00"

vix.input.x.et.value = mtime|<epoch time in milliseconds>
* Sets the earliest time for this virtual index.
* Can be used instead of extracting times from the path via vix.input.x.et.regex
* When set to "mtime", uses the file modification time as the earliest time.

# Latest time extractions - See "Earliest time extractions"

vix.input.x.lt.regex = <regex>
* Latest time equivalent of vix.input.x.et.regex

vix.input.x.lt.format = <java.text.SimpleDateFormat date pattern>
* Latest time equivalent of vix.input.x.et.format

vix.input.x.lt.offset = <seconds>
* Latest time equivalent of vix.input.x.et.offset

vix.input.x.lt.timezone = <java.util.SimpleTimeZone timezone id>
* Latest time equivalent of vix.input.x.et.timezone

vix.input.x.lt.value = <mod time>
* Latest time equivalent of vix.input.x.et.value

#
# Archiving
#

vix.output.buckets.path = <hadoop path>
* Path to a hadoop filesystem where buckets will be archived

vix.output.buckets.older.than = <integer>
* The age of a bucket, in seconds, before it is archived.
* The age of a bucket is determined by the the earliest _time field of
  any event in the bucket.

vix.output.buckets.from.indexes = <comma separated list of splunk indexes>
* List of (non-virtual) indexes that will get archived to this (virtual) index.

vix.unified.search.cutoff_sec = <seconds>
* Window length before present time that configures where events are retrieved
  for unified search
* Events from now to now-cutoff_sec will be retrieved from the splunk index
  and events older than cutoff_sec will be retrieved from the archive index

#**************************************************************************
# PER VIRTUAL INDEX OR PROVIDER OPTIONS -- HADOOP
# These options can be set at either the virtual index level or provider
# level, for the Hadoop ERP.
#
# Options set at the virtual index level take precedence over options set
# at the provider level.
#
# Virtual index level prefix:
# vix.input.<input_id>.<option_suffix>
#
# Provider level prefix:
# vix.splunk.search.<option_suffix>
#**************************************************************************

# The following options are just defined by their <option_suffix>

#
# Record reader options
#

recordreader.<name>.<conf_key> = <conf_value>
* Sets a configuration key for a RecordReader with <name> to <conf_value>

recordreader.<name>.regex = <regex>
* Regex specifying which files this RecordReader can be used for.

recordreader.journal.buffer.size = <bytes>
* Buffer size used by the journal record reader

recordreader.csv.dialect = default|excel|excel-tab|tsv
* Set the csv dialect for csv files
* A csv dialect differs on delimiter_char, quote_char and escape_char.
* Here is a list of how the different dialects are defined in order delim,
  quote, and escape:
  * default   = ,  " \
  * excel     = ,  " "
  * excel-tab = \t " "
  * tsv       = \t " \

#
# Splitter options
#

splitter.<name>.<conf_key> = <conf_value>
* Sets a configuration key for a split generator with <name> to <conf_value>
* See comment above under "PER VIRTUAL INDEX OR PROVIDER OPTIONS". This means
  that the full format is:
   vix.input.N.splitter.<name>.<conf_key> (in a vix stanza)
   vix.splunk.search.splitter.<name>.<conf_key> (in a provider stanza)

splitter.file.split.minsize = <integer>
* Minimum size, in bytes, for file splits.
* Default: 1

splitter.file.split.maxsize = <integer>
* Maximum size, in bytes, for file splits.
* Default: Long.MAX_VALUE

#**************************************************************************
# Dynamic Data Self Storage settings.
# This section describes settings that affect the archiver-
# optional and archiver-mandatory settings only.
#
# As the first step in the Dynamic Data Self Storage feature, it allows users
# to move their data from Splunk indexes to customer-owned external storage
# in AWS S3 when the data reaches the end of the retention period. Note that
# only the raw data and delete marker files are transferred to the external
# storage.
#
# Future development may include the support for storage hierarchies and the
# automation of data rehydration.
#
# For example, use the following settings to configure Dynamic Data Self Storage.
#   archiver.selfStorageProvider     = S3
#   archiver.selfStorageBucket       = mybucket
#   archiver.selfStorageBucketFolder = folderXYZ
#**************************************************************************
archiver.selfStorageProvider = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Specifies the storage provider for Self Storage.
* Optional. Only required when using Self Storage.
* The only supported provider is S3. More providers will be added in the future
for other cloud vendors and other storage options.

archiver.selfStorageBucket = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Specifies the destination bucket for Self Storage.
* Optional. Only required when using Self Storage.

archiver.selfStorageBucketFolder = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Specifies the folder on the destination bucket for Self Storage.
* Optional.
* If not specified, data is uploaded to the root path in the destination bucket.

#**************************************************************************
# Dynamic Data Archive lets you move your data from your Splunk Cloud indexes to a
# storage location. You can configure Splunk Cloud to automatically move the data
# in an index when the data reaches the end of the Splunk Cloud retention period
# you configure. In addition, you can restore your data to Splunk Cloud if you need
# to perform some analysis on the data.
# For each index, you can use Dynamic Data Self Storage or Dynamic Data Archive,
# but not both.
#
# For example, use the following settings to configure Dynamic Data Archive.
#   archiver.coldStorageProvider        = Glacier
#   archiver.coldStorageRetentionPeriod = 365
#**************************************************************************
archiver.coldStorageProvider = <string>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Specifies the storage provider for Dynamic Data Archive.
* Optional. Only required when using Dynamic Data Archive.
* The only supported provider is Glacier. More providers will be added in the
  future for other cloud vendors and other storage options.

archiver.coldStorageRetentionPeriod = <unsigned integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* Defines how long Splunk will maintain data in days, including the
  archived period.
* Optional. Only required when using Dynamic Data Archive.
* Must be greater than 0

archiver.enableDataArchive = <boolean>
* Currently not supported. This setting is related to a feature that is
  still under development.
* If set to true, Dynamic Data Archiver is enabled for the index.
* Default: false

archiver.maxDataArchiveRetentionPeriod = <nonnegative integer>
* Currently not supported. This setting is related to a feature that is
  still under development.
* The maximum total time in seconds, that data for the specified index is
  maintained by Splunk, including the archived period.
* The archiver.maxDataArchiveRetentionPeriod controls the maximum value of the
  coldStorageRetentionPeriod. coldStorageRetentionPeriod cannot exceed this
  value.
* Default: 0

#**************************************************************************
# Volume settings.  This section describes settings that affect the volume-
# optional and volume-mandatory settings only.
#
# All volume stanzas begin with "volume:". For example:
#   [volume:volume_name]
#   path = /foo/bar
#
# These volume stanzas can then be referenced by individual index
# settings, e.g. homePath or coldPath.  To refer to a volume stanza, use
# the "volume:" prefix. For example, to set a cold DB to the example stanza
# above, in index "hiro", use:
#   [hiro]
#   coldPath = volume:volume_name/baz
# This will cause the cold DB files to be placed under /foo/bar/baz.  If the
# volume spec is not followed by a path
# (e.g.  "coldPath=volume:volume_name"), then the cold path would be
# composed by appending the index name to the volume name ("/foo/bar/hiro").
#
# If "path" is specified with a URI-like value (e.g., "s3://bucket/path"),
# this is a remote storage volume.  A remote storage volume can only be
# referenced by a remotePath setting, as described above.  An Amazon S3
# remote path might look like "s3://bucket/path", whereas an NFS remote path
# might look like "file:///mnt/nfs".  The name of the scheme ("s3" or "file"
# from these examples) is important, because it can indicate some necessary
# configuration specific to the type of remote storage.  To specify a
# configuration under the remote storage volume stanza, you use settings
# with the pattern "remote.<scheme>.<param name>". These settings vary
# according to the type of remote storage.  For example, remote storage of
# type S3 might require that you specify an access key and a secret key.
# You would do this through the "remote.s3.access_key" and
# "remote.s3.secret_key" settings.
#
# Note: thawedPath may not be defined in terms of a volume.
# Thawed allocations are manually controlled by Splunk administrators,
# typically in recovery or archival/review scenarios, and should not
# trigger changes in space automatically used by normal index activity.
#**************************************************************************

storageType = local | remote
* Optional.
* Specifies whether the volume definition is for indexer local storage or remote
  storage. Only the 'remotePath' setting references a remote volume.
* Default: "local".

path = <path on server>
* Required.
* If storageType is set to its default value of "local":
  * The 'path' setting points to the location on the file system where al
    indexes that will use this volume reside.
   * This location must not overlap with the location for any other volume
     or index.
* If storageType is set to "remote":
  * The 'path' setting points to the remote storage location where indexes
    reside.
  * The format for this setting is: <scheme>://<remote-location-specifier>
    * The "scheme" identifies a supported external storage system type.
    * The "remote-location-specifier" is an external system-specific string for
       identifying a location inside the storage system.

maxVolumeDataSizeMB = <positive integer>
* If set, this setting limits the total size of all databases that reside
  on this volume to the maximum size specified, in MB.  Note that this it
  will act only on those indexes which reference this volume, not on the
  total size of the path set in the 'path' setting of this volume.
* If the size is exceeded, splunkd removes buckets with the oldest value
  of latest time (for a given bucket) across all indexes in the volume,
  until the volume is below the maximum size. This is the trim operation.
  This can cause buckets to be chilled [moved to cold] directly
  from a hot DB, if those buckets happen to have the least value of
  latest-time (LT) across all indexes in the volume.
* The highest legal value is 4294967295.
* The lowest legal value is 1.
* Optional.
* This setting is ignored when 'storageType' is set to "remote".

rotatePeriodInSecs = <nonnegative integer>
* Optional, ignored for storageType=remote
* Specifies period of trim operation for this volume.
* The highest legal value is 4294967295.
* Default: the global 'rotatePeriodInSecs' value.

datatype = <event|metric>
* Determines whether the index stores log events or metric data.
* If set to "metric", Splunk software optimize the index to store
  metric data which can be queried later only using the 'mstats'
  operator as searching metric data is different from traditional
  log events.
* Use "metric" only for metric sourcetypes like statsd.
* Optional.
* Default: event

remote.* = <string>
* With remote volumes, communication between the indexer and the external
  storage system may require additional configuration, specific to the type of
  storage system. You can pass configuration information to the storage
  system by specifying the settings through the following schema:
  remote.<scheme>.<config-variable> = <value>.
  For example: remote.s3.access_key = ACCESS_KEY
* Optional.

################################################################
##### S3 specific settings
################################################################

remote.s3.header.<http-method-name>.<header-field-name> = <string>
* Enable server-specific features, such as reduced redundancy, encryption,
  and so on, by passing extra HTTP headers with the REST requests.
  The <http-method-name> can be any valid HTTP method. For example, GET,
  PUT, or ALL, for setting the header field for all HTTP methods.
* Example: remote.s3.header.PUT.x-amz-storage-class = REDUCED_REDUNDANCY
* Optional.

remote.s3.access_key = <string>
* Specifies the access key to use when authenticating with the remote storage
  system supporting the S3 API.
* If not specified, the indexer will look for these environment variables:
  AWS_ACCESS_KEY_ID or AWS_ACCESS_KEY (in that order).
* If the environment variables are not set and the indexer is running on EC2,
  the indexer attempts to use the access key from the IAM role.
* Optional.
* Default: not set

remote.s3.secret_key = <string>
* Specifies the secret key to use when authenticating with the remote storage
  system supporting the S3 API.
* If not specified, the indexer will look for these environment variables:
  AWS_SECRET_ACCESS_KEY or AWS_SECRET_KEY (in that order).
* If the environment variables are not set and the indexer is running on EC2,
  the indexer attempts to use the secret key from the IAM role.
* Optional.
* Default: not set

remote.s3.list_objects_version = v1|v2
* The AWS S3 Get Bucket (List Objects) Version to use.
* See AWS S3 documentation "GET Bucket (List Objects) Version 2" for details.
* Default: v1

remote.s3.signature_version = v2|v4
* The signature version to use when authenticating with the remote storage
  system supporting the S3 API.
* For 'sse-kms' server-side encryption scheme, you must use signature_version=v4.
* Optional.
* Default: v4

remote.s3.auth_region = <string>
* The authentication region to use for signing requests when interacting
  with the remote storage system supporting the S3 API.
* Used with v4 signatures only.
* If unset and the endpoint (either automatically constructed or explicitly
  set with remote.s3.endpoint setting) uses an AWS URL (for example,
  https://s3-us-west-1.amazonaws.com), the instance attempts to extract
  the value from the endpoint URL (for example, "us-west-1").  See the
  description for the remote.s3.endpoint setting.
* If unset and an authentication region cannot be determined, the request
  will be signed with an empty region value.
* Optional.
* Default: not set

remote.s3.use_delimiter = <boolean>
* Specifies whether a delimiter (currently "guidSplunk") should be
  used to list the objects that are present on the remote storage.
* A delimiter groups objects that have the same delimiter value
  so that the listing process can be more efficient as it
  does not need to report similar objects.
* Optional.
* Default: true

remote.s3.supports_versioning = <boolean>
* Specifies whether the remote storage supports versioning.
* Versioning is a means of keeping multiple variants of an object
  in the same bucket on the remote storage.
* Optional.
* Default: true

remote.s3.endpoint = <URL>
* The URL of the remote storage system supporting the S3 API.
* The scheme, http or https, can be used to enable or disable SSL connectivity
  with the endpoint.
* If not specified and the indexer is running on EC2, the endpoint will be
  constructed automatically based on the EC2 region of the instance where the
  indexer is running, as follows: https://s3-<region>.amazonaws.com
* Example: https://s3-us-west-2.amazonaws.com
* Optional.

remote.s3.multipart_download.part_size = <unsigned integer>
* Sets the download size of parts during a multipart download.
* This setting uses HTTP/1.1 Range Requests (RFC 7233) to improve throughput
  overall and for retransmission of failed transfers.
* A value of 0 disables downloading in multiple parts, i.e., files will always
  be downloaded as a single (large) part.
* Do not change this value unless that value has been proven to improve
  throughput.
* Optional.
* Minimum value: 5242880 (5 MB)
* Default: 134217728 (128 MB)

remote.s3.multipart_upload.part_size = <unsigned integer>
* Sets the upload size of parts during a multipart upload.
* Optional.
* Minimum value: 5242880 (5 MB)
* Default: 134217728 (128 MB)

remote.s3.multipart_max_connections = <unsigned integer>
* Specifies the maximum number of HTTP connections to have in progress for
  either multipart download or upload.
* A value of 0 means unlimited.
* Default: 8

remote.s3.enable_data_integrity_checks = <boolean>
* If set to true, Splunk sets the data checksum in the metadata field of the
  HTTP header during upload operation to S3.
* The checksum is used to verify the integrity of the data on uploads.
* Default: false

remote.s3.enable_signed_payloads  = <boolean>
* If set to true, Splunk signs the payload during upload operation to S3.
* Valid only for remote.s3.signature_version = v4
* Default: true

remote.s3.retry_policy = max_count
* Sets the retry policy to use for remote file operations.
* A retry policy specifies whether and how to retry file operations that fail
  for those failures that might be intermittent.
* Retry policies:
  + "max_count": Imposes a maximum number of times a file operation will be
    retried upon intermittent failure both for individual parts of a multipart
    download or upload and for files as a whole.
* Optional.
* Default: max_count

remote.s3.max_count.max_retries_per_part = <unsigned integer>
* When the remote.s3.retry_policy setting is max_count, sets the maximum number
  of times a file operation will be retried upon intermittent failure.
* The count is maintained separately for each file part in a multipart download
  or upload.
* Optional.
* Default: 9

remote.s3.max_count.max_retries_in_total = <unsigned integer>
* When the remote.s3.retry_policy setting is max_count, sets the maximum number
  of times a file operation will be retried upon intermittent failure.
* The count is maintained for each file as a whole.
* Optional.
* Default: 128

remote.s3.timeout.connect = <unsigned integer>
* Set the connection timeout, in milliseconds, to use when interacting
  with S3 for this volume
* Optional.
* Default: 5000

remote.s3.timeout.read = <unsigned integer>
* Set the read timeout, in milliseconds, to use when interacting with
  S3 for this volume
* Optional.
* Default: 60000

remote.s3.timeout.write = <unsigned integer>
* Set the write timeout, in milliseconds, to use when interacting with
  S3 for this volume
* Optional.
* Default: 60000

remote.s3.sslVerifyServerCert = <boolean>
* If this is set to true, Splunk verifies certificate presented by S3
  server and checks that the common name/alternate name matches the ones
  specified in 'remote.s3.sslCommonNameToCheck' and
  'remote.s3.sslAltNameToCheck'.
* Optional
* Default: false

remote.s3.sslVersions = <versions_list>
* Comma-separated list of SSL versions to connect to 'remote.s3.endpoint'.
* The versions available are "ssl3", "tls1.0", "tls1.1", and "tls1.2".
* The special version "*" selects all supported versions.  The version "tls"
  selects all versions tls1.0 or newer.
* If a version is prefixed with "-" it is removed from the list.
* SSLv2 is always disabled; "-ssl2" is accepted in the version list
  but does nothing.
* When configured in FIPS mode, ssl3 is always disabled regardless
  of this configuration.
* Optional.
* Default: tls1.2

remote.s3.sslCommonNameToCheck = <commonName1>, <commonName2>, ..
* If this value is set, and 'remote.s3.sslVerifyServerCert' is set to true,
  splunkd checks the common name of the certificate presented by
  the remote server (specified in 'remote.s3.endpoint') against this list
  of common names.
* Default: not set

remote.s3.sslAltNameToCheck = <alternateName1>, <alternateName2>, ..
* If this value is set, and 'remote.s3.sslVerifyServerCert' is set to true,
  splunkd checks the alternate name(s) of the certificate presented by
  the remote server (specified in 'remote.s3.endpoint') against this list of
  subject alternate names.
* Default: not set

remote.s3.sslRootCAPath = <path>
* Full path to the Certificate Authority (CA) certificate PEM format file
  containing one or more certificates concatenated together. S3 certificate
  will be validated against the CAs present in this file.
* Optional.
* Default: [sslConfig/caCertFile] in server.conf

remote.s3.cipherSuite = <cipher suite string>
* If set, uses the specified cipher string for the SSL connection.
* If not set, uses the default cipher string.
* Must specify 'dhFile' to enable any Diffie-Hellman ciphers.
* Optional.
* Default: TLSv1+HIGH:TLSv1.2+HIGH:@STRENGTH

remote.s3.ecdhCurves = <comma-separated list>
* ECDH curves to use for ECDH key negotiation.
* The curves should be specified in the order of preference.
* The client sends these curves as a part of Client Hello.
* Splunk software only supports named curves specified
  by their SHORT names.
* The list of valid named curves by their short/long names can be obtained
  by executing this command:
  $SPLUNK_HOME/bin/splunk cmd openssl ecparam -list_curves
* e.g. ecdhCurves = prime256v1,secp384r1,secp521r1
* Optional.
* Default: not set

remote.s3.dhFile = <path>
* PEM format Diffie-Hellman parameter file name.
* DH group size should be no less than 2048bits.
* This file is required in order to enable any Diffie-Hellman ciphers.
* Optional.
* Default: not set

remote.s3.encryption = sse-s3 | sse-kms | sse-c | none
* Specifies the scheme to use for Server-side Encryption (SSE) for data-at-rest.
* sse-s3: Check http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html
* sse-kms: Check http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html
* sse-c: Check http://docs.aws.amazon.com/AmazonS3/latest/dev/ServerSideEncryptionCustomerKeys.html
* none: no Server-side encryption enabled. Data is stored unencrypted on the
  remote storage.
* Optional.
* Default: none

remote.s3.encryption.sse-c.key_type = kms
* Determines the mechanism Splunk uses to generate the key for sending over to
  S3 for SSE-C.
* The only valid value is 'kms', indicating AWS KMS service.
* One must specify required KMS settings: e.g. remote.s3.kms.key_id
  for Splunk to start up while using SSE-C.
* Optional.
* Default: kms

remote.s3.encryption.sse-c.key_refresh_interval = <unsigned integer>
* Specifies period in seconds at which a new key will be generated and used
  for encrypting any new data being uploaded to S3.
* Optional.
* Default: 86400

remote.s3.kms.key_id = <string>
* Required if remote.s3.encryption = sse-c | sse-kms
* Specifies the identifier for Customer Master Key (CMK) on KMS. It can be the
  unique key ID or the Amazon Resource Name (ARN) of the CMK or the alias
  name or ARN of an alias that refers to the CMK.
* Examples:
  Unique key ID: 1234abcd-12ab-34cd-56ef-1234567890ab
  CMK ARN: arn:aws:kms:us-east-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab
  Alias name: alias/ExampleAlias
  Alias ARN: arn:aws:kms:us-east-2:111122223333:alias/ExampleAlias
* Default: not set

remote.s3.kms.access_key = <string>
* Similar to 'remote.s3.access_key'.
* If not specified, KMS access uses 'remote.s3.access_key'.
* Optional.
* Default: not set

remote.s3.kms.secret_key = <string>
* Similar to 'remote.s3.secret_key'.
* If not specified, KMS access uses 'remote.s3.secret_key'.
* Optional.
* Default: not set

remote.s3.kms.auth_region = <string>
* Required if 'remote.s3.auth_region' is unset and Splunk can not
  automatically extract this information.
* Similar to 'remote.s3.auth_region'.
* If not specified, KMS access uses 'remote.s3.auth_region'.
* Default: not set

remote.s3.kms.max_concurrent_requests = <unsigned integer>
* Optional.
* Limits maximum concurrent requests to KMS from this Splunk instance.
* NOTE: Can severely affect search performance if set to very low value.
* Default: 10

remote.s3.kms.<ssl_settings> = <...>
* Optional.
* Check the descriptions of the SSL settings for remote.s3.<ssl_settings>
  above. e.g. remote.s3.sslVerifyServerCert.
* Valid ssl_settings are sslVerifyServerCert, sslVersions, sslRootCAPath,
  sslAltNameToCheck, sslCommonNameToCheck, cipherSuite, ecdhCurves, and dhFile.
* All of these settings are optional.
* All of these settings have the same defaults as
  'remote.s3.<ssl_settings>'.
