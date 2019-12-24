#   Version 7.3.0
#
# This file contains possible attribute/value pairs for configuring
# segmentation of events in segementers.conf.
#
# There is a default segmenters.conf in $SPLUNK_HOME/etc/system/default. To set
# custom configurations, place a segmenters.conf in
# $SPLUNK_HOME/etc/system/local/.  For examples, see segmenters.conf.example.
# You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#     * You can also define global settings outside of any stanza, at the top of the file.
#     * Each conf file should have at most one default stanza. If there are multiple default
#       stanzas, attributes are combined. In the case of multiple definitions of the same
#       attribute, the last definition in the file wins.
#     * If an attribute is defined at both the global level and in a specific stanza, the
#       value in the specific stanza takes precedence.

[<SegmenterName>]
* Name your stanza.
* Follow this stanza name with any number of the following attribute/value
  pairs.
* If you don't specify an attribute/value pair, Splunk will use the default.

MAJOR = <space separated list of breaking characters>
* Set major breakers.
* Major breakers are words, phrases or terms in your data that are surrounded
  by set breaking characters.
* By default, major breakers are set to most characters and blank spaces.
* Typically, major breakers are single characters.
* Please note: \s represents a space; \n, a newline; \r, a carriage return; and
  \t, a tab.
* Default is [ ] < > ( ) { } | ! ; , ' " * \n \r \s \t & ? + %21 %26 %2526 %3B %7C %20 %2B %3D -- %2520 %5D %5B %3A %0A %2C %28 %29


MINOR = <space separated list of strings>
* Set minor breakers.
* In addition to the segments specified by the major breakers, for each minor
  breaker found, Splunk indexes the token from the last major breaker to the
  current minor breaker and from the last minor breaker to the current minor
  breaker.
* Default is / : = @ . - $ # % \\ _

INTERMEDIATE_MAJORS =  true | false
* Set this to "true" if you want an IP address to appear in typeahead as
  a, a.b, a.b.c, a.b.c.d
* The typical performance hit by setting to "true" is 30%.
* Default is "false".

FILTER = <regular expression>
* If set, segmentation will only take place if the regular expression matches.
* Furthermore, segmentation will only take place on the first group of the
  matching regex.
* Default is empty.

LOOKAHEAD = <integer>
* Set how far into a given event (in characters) Splunk segments.
* LOOKAHEAD applied after any FILTER rules.
* To disable segmentation, set to 0.
* Defaults to -1 (read the whole event).

MINOR_LEN = <integer>
* Specify how long a minor token can be.
* Longer minor tokens are discarded without prejudice.
* Defaults to -1.

MAJOR_LEN = <integer>
* Specify how long a major token can be.
* Longer major tokens are discarded without prejudice.
* Defaults to -1.

MINOR_COUNT = <integer>
* Specify how many minor segments to create per event.
* After the specified number of minor tokens have been created, later ones are
  discarded without prejudice.
* Defaults to -1.

MAJOR_COUNT = <integer>
* Specify how many major segments are created per event.
* After the specified number of major segments have been created, later ones
  are discarded without prejudice.
* Default to -1.
