#   Version 7.3.0
#
# This file contains possible attribute/value pairs for creating search
# commands for any custom search scripts created.  Add your custom search
# script to $SPLUNK_HOME/etc/searchscripts/ or
# $SPLUNK_HOME/etc/apps/MY_APP/bin/.  For the latter, put a custom
# commands.conf in $SPLUNK_HOME/etc/apps/MY_APP.  For the former, put your
# custom commands.conf in $SPLUNK_HOME/etc/system/local/.

# There is a commands.conf in $SPLUNK_HOME/etc/system/default/.  For examples,
# see commands.conf.example.  You must restart Splunk to enable configurations.

# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

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


[<STANZA_NAME>]
* Each stanza represents a search command; the command is the stanza name.
* The stanza name invokes the command in the search language.
* Set the following attributes/values for the command.  Otherwise, Splunk uses
  the defaults.
* If the filename attribute is not specified, Splunk searches for an
  external program by appending extensions (e.g. ".py", ".pl") to the
  stanza name.
* If chunked = true, in addition to ".py" and ".pl" as above, Splunk
  searches using the extensions ".exe", ".bat", ".cmd", ".sh", ".js",
  and no extension (to find extensionless binaries).
* See the filename attribute for more information about how Splunk
  searches for external programs.

type = <string>
* Type of script: python, perl
* Defaults to python.

filename = <string>
* Optionally specify the program to be executed when the search command is used.
* Splunk looks for the given filename in the app's bin directory.
* The filename attribute can not reference any file outside of the app's bin directory.
* If the filename ends in ".py", Splunk's python interpreter is used
  to invoke the external script.
* If chunked = true, Splunk looks for the given filename in
  $SPLUNK_HOME/etc/apps/MY_APP/<PLATFORM>/bin before searching
  $SPLUNK_HOME/etc/apps/MY_APP/bin, where <PLATFORM> is one of
  "linux_x86_64", "linux_x86", "windows_x86_64", "windows_x86",
  "darwin_x86_64" (depending on the platform on which Splunk is
  running on).
* If chunked = true and if a path pointer file (*.path) is specified,
  the contents of the file are read and the result is used as the
  command to be run. Environment variables in the path pointer
  file are substituted. Path pointer files can be used to reference
  system binaries (e.g. /usr/bin/python).

command.arg.<N> = <string>
* Additional command-line arguments to use when invoking this
  program. Environment variables will be substituted (e.g. $SPLUNK_HOME).
* Only available if chunked = true.

local = [true|false]
* If true, specifies that the command should be run on the search head only
* Defaults to false

perf_warn_limit = <integer>
* Issue a performance warning message if more than this many input events are
  passed to this external command (0 = never)
* Defaults to 0 (disabled)

streaming = [true|false]
* Specify whether the command is streamable.
* Defaults to false.

maxinputs = <integer>
* Maximum number of events that can be passed to the command for each
  invocation.
* This limit cannot exceed the value of maxresultrows in limits.conf.
* 0 for no limit.
* Defaults to 50000.

passauth = [true|false]
* If set to true, splunkd passes several authentication-related facts
  at the start of input, as part of the header (see enableheader).
* The following headers are sent
  * authString: psuedo-xml string that resembles
      <auth><userId>username</userId><username>username</username><authToken>auth_token</authToken></auth>
    where the username is passed twice, and the authToken may be used
    to contact splunkd during the script run.
  * sessionKey: the session key again.
  * owner: the user portion of the search context
  * namespace: the app portion of the search context
* Requires enableheader = true; if enableheader = false, this flag will
  be treated as false as well.
* Defaults to false.
* If chunked = true, this attribute is ignored. An authentication
  token is always passed to commands using the chunked custom search
  command protocol.

run_in_preview = [true|false]
* Specify whether to run this command if generating results just for preview
  rather than final output.
* Defaults to true

enableheader = [true|false]
* Indicate whether or not your script is expecting header information or not.
* Currently, the only thing in the header information is an auth token.
* If set to true it will expect as input a head section + '\n' then the csv input
* NOTE: Should be set to true if you use splunk.Intersplunk
* Defaults to true.

retainsevents = [true|false]
* Specify whether the command retains events (the way the sort/dedup/cluster
  commands do) or whether it transforms them (the way the stats command does).
* Defaults to false.

generating = [true|false]
* Specify whether your command generates new events. If no events are passed to
  the command, will it generate events?
* Defaults to false.

generates_timeorder = [true|false]
* If generating = true, does command generate events in descending time order
  (latest first)
* Defaults to false.

overrides_timeorder = [true|false]
* If generating = false and streaming=true, does command change the order of
  events with respect to time?
* Defaults to false.

requires_preop = [true|false]
* Specify whether the command sequence specified by the 'streaming_preop' key
  is required for proper execution or is it an optimization only
* Default is false (streaming_preop not required)

streaming_preop = <string>
* A string that denotes the requested pre-streaming search string.

required_fields = <string>
* A comma separated list of fields that this command may use.
* Informs previous commands that they should retain/extract these fields if
  possible.  No error is generated if a field specified is missing.
* Defaults to '*'

supports_multivalues = [true|false]
* Specify whether the command supports multivalues.
* If true, multivalues will be treated as python lists of strings, instead of a
  flat string (when using Intersplunk to interpret stdin/stdout).
* If the list only contains one element, the value of that element will be
  returned, rather than a list
  (for example, isinstance(val, basestring) == True).

supports_getinfo = [true|false]
* Specifies whether the command supports dynamic probing for settings
  (first argument invoked == __GETINFO__ or __EXECUTE__).

supports_rawargs = [true|false]
* Specifies whether the command supports raw arguments being passed to it or if
  it prefers parsed arguments (where quotes are stripped).
* If unspecified, the default is false

undo_scheduler_escaping = [true|false]
* Specifies whether the commands raw arguments need to be unesacped.
* This is perticularly applies to the commands being invoked by the scheduler.
* This applies only if the command supports raw arguments(supports_rawargs).
* If unspecified, the default is false

requires_srinfo = [true|false]
* Specifies if the command requires information stored in SearchResultsInfo.
* If true, requires that enableheader be set to true, and the full
  pathname of the info file (a csv file) will be emitted in the header under
  the key 'infoPath'
* If unspecified, the default is false


needs_empty_results = [true|false]
* Specifies whether or not this search command needs to be called with
  intermediate empty search results
* If unspecified, the default is true

changes_colorder = [true|false]
* Specify whether the script output should be used to change the column
  ordering of the fields.
* Default is true

outputheader = <true/false>
* If set to true, output of script should be
  a header section + blank line + csv output
* If false, script output should be pure csv only
* Default is false

clear_required_fields = [true|false]
* If true, required_fields represents the *only* fields required.
* If false, required_fields are additive to any fields that may be required by
  subsequent commands.
* In most cases, false is appropriate for streaming commands and true for
  reporting commands
* Default is false

stderr_dest = [log|message|none]
* What do to with the stderr output from the script
* 'log' means to write the output to the job's search.log.
* 'message' means to write each line as an search info message.  The message
  level can be set to adding that level (in ALL CAPS) to the start of the
  line, e.g. "WARN my warning message."
* 'none' means to discard the stderr output
* Defaults to log

is_order_sensitive = [true|false]
* Specify whether the command requires ordered input.
* Defaults to false.

is_risky = [true|false]
* Searches using Splunk Web are flagged to warn users when they
  unknowingly run a search that contains commands that might be a
  security risk. This warning appears when users click a link or type
  a URL that loads a search that contains risky commands. This warning
  does not appear when users create ad hoc searches.
* This flag is used to determine whether the command is risky.
* Defaults to false.
* - Specific commands that ship with the product have their own defaults

chunked = [true|false]
* If true, this command supports the new "chunked" custom
  search command protocol.
* If true, the only other commands.conf attributes supported are
  is_risky, maxwait, maxchunksize, filename, command.arg.<N>, and
  run_in_preview.
* If false, this command uses the legacy custom search command
  protocol supported by Intersplunk.py.
* Default is false

maxwait = <integer>
* Only available if chunked = true.
* Not supported in Windows.
* The value of maxwait is the maximum number of seconds the custom
  search command can pause before producing output.
* If set to 0, the command can pause forever.
* Default is 0

maxchunksize = <integer>
* Only available if chunked = true.
* The value of maxchunksize is maximum size chunk (size of metadata
  plus size of body) the external command may produce. If the command
  tries to produce a larger chunk, the command is terminated.
* If set to 0, the command may send any size chunk.
* Default is 0
