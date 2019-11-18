#   Version 7.3.0
#
# This file contains possible attribute/value pairs for configuring tags.  Set
# any number of tags for indexed or extracted fields.
#
# There is no tags.conf in $SPLUNK_HOME/etc/system/default/.  To set custom
# configurations, place a tags.conf in $SPLUNK_HOME/etc/system/local/. For
# help, see tags.conf.example.  You must restart Splunk to enable
# configurations.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

[<fieldname>=<value>]
* The field name and value to which the tags in the stanza
  apply ( eg host=localhost ).
* A tags.conf file can contain multiple stanzas. It is recommended that the
  value be URL encoded to avoid
* config file parsing errors especially if the field value contains the
  following characters: \n, =, []
* Each stanza can refer to only one field=value

<tag1> = <enabled|disabled>
<tag2> = <enabled|disabled>
<tag3> = <enabled|disabled>
* Set whether each <tag> for this specific <fieldname><value> is enabled or
  disabled.
* While you can have multiple tags in a stanza (meaning that multiple tags are
  assigned to the same field/value combination), only one tag is allowed per
  stanza line. In other words, you can't have a list of tags on one line of the
  stanza.

* WARNING: Do not quote the <tag> value: foo=enabled, not "foo"=enabled.
