#   Version 7.3.0
#
# This file contains all possible attributes and value pairs for an
# eventtypes.conf file.  Use this file to configure event types and their
# properties. You can also pipe any search to the "typelearner" command to
# create event types.  Event types created this way will be written to
# $SPLUNK_HOME/etc/system/local/eventtypes.conf.
#
# There is an eventtypes.conf in $SPLUNK_HOME/etc/system/default/.  To set
# custom configurations, place an eventtypes.conf in
# $SPLUNK_HOME/etc/system/local/. For examples, see eventtypes.conf.example.
# You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see
# the documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#  * You can also define global settings outside of any stanza, at the top
#    of the file.
#  * Each conf file should have at most one default stanza. If there are
#    multiple default stanzas, attributes are combined. In the case of
#    multiple definitions of the same attribute, the last definition in the
#    file wins.
#  * If an attribute is defined at both the global level and in a specific
#    stanza, the value in the specific stanza takes precedence.

[<$EVENTTYPE>]
* Header for the event type
* $EVENTTYPE is the name of your event type.
* You can have any number of event types, each represented by a stanza and
  any number of the following attribute/value pairs.
* NOTE: If the name of the event type includes field names surrounded by the
  percent character (for example "%$FIELD%") then the value of $FIELD is
  substituted into the event type name for that event.  For example, an
  event type with the header [cisco-%code%] that has "code=432" becomes
  labeled "cisco-432".

disabled = [1|0]
* Toggle event type on or off.
* Set to 1 to disable.

search = <string>
* Search terms for this event type.
* For example: error OR warn.
* NOTE: You cannot base an event type on:
* A search that includes a pipe operator (a "|" character).
* A subsearch (a search pipeline enclosed in square brackets).
* A search referencing a report. This is a best practice. Any report that is referenced by an
  event type can later be updated in a way that makes it invalid as an event type. For example,
  a report that is updated to include transforming commands cannot be used as the definition for
  an event type. You have more control over your event type if you define it with the same search
  string as the report.

priority = <integer, 1 through 10>
* Value used to determine the order in which the matching eventtypes of an
  event are displayed.
* 1 is the highest priority and 10 is the lowest priority.

description = <string>
* Optional human-readable description of this saved search.

tags = <string>
* DEPRECATED - see tags.conf.spec

color = <string>
* color for this event type.
* Supported colors: none, et_blue, et_green, et_magenta, et_orange, 
  et_purple, et_red, et_sky, et_teal, et_yellow

