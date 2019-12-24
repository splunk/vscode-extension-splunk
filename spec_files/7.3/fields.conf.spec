#   Version 7.3.0
#
# This file contains possible attribute and value pairs for:
#  * Telling Splunk how to handle multi-value fields.
#  * Distinguishing indexed and extracted fields.
#  * Improving search performance by telling the search processor how to
#    handle field values.

# Use this file if you are creating a field at index time (not advised).
#
# There is a fields.conf in $SPLUNK_HOME/etc/system/default/.  To set custom
# configurations, place a fields.conf in $SPLUNK_HOME/etc/system/local/.  For
# examples, see fields.conf.example.  You must restart Splunk to enable
# configurations.
#
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

[<field name>]
* Name of the field you're configuring.
* Follow this stanza name with any number of the following attribute/value
  pairs.
* Field names can only contain a-z, A-Z, 0-9, and  _, but cannot begin with a
  number or _

# TOKENIZER indicates that your configured field's value is a smaller part of a
# token.  For example, your field's value is "123" but it occurs as "foo123" in
# your event.
TOKENIZER = <regular expression>
* Use this setting to configure multivalue fields (refer to the online
  documentation for multivalue fields).
* A regular expression that indicates how the field can take on multiple values
  at the same time.
* If empty, the field can only take on a single value.
* Otherwise, the first group is taken from each match to form the set of
  values.
* This setting is used by the "search" and "where" commands, the summary and
  XML outputs of the asynchronous search API, and by the top, timeline and
  stats commands.
* Tokenization of indexed fields (INDEXED = true) is not supported so this
  attribute is ignored for indexed fields.
* Default to empty.

INDEXED = [true|false]
* Indicate whether a field is indexed or not.
* Set to true if the field is indexed.
* Set to false for fields extracted at search time (the majority of fields).
* Defaults to false.

INDEXED_VALUE = [true|false|<sed-cmd>|<simple-substitution-string>]
* Set this to true if the value is in the raw text of the event.
* Set this to false if the value is not in the raw text of the event.
* Setting this to true expands any search for key=value into a search of
  value AND key=value (since value is indexed).
* For advanced customization, this setting supports sed style substitution.
  For example, 'INDEXED_VALUE=s/foo/bar/g' would take the value of the field,
  replace all instances of 'foo' with 'bar,' and use that new value as the
  value to search in the index.
* This setting also supports a simple substitution based on looking for the
  literal string '<VALUE>' (including the '<' and '>' characters).
  For example, 'INDEXED_VALUE=source::*<VALUE>*' would take a search for
  'myfield=myvalue' and search for 'source::*myvalue*' in the index as a
  single term.
* For both substitution constructs, if the resulting string starts with a '[',
  Splunk interprets the string as a Splunk LISPY expression.  For example,
  'INDEXED_VALUE=[OR <VALUE> source::*<VALUE>]' would turn 'myfield=myvalue'
  into applying the LISPY expression '[OR myvalue source::*myvalue]' (meaning
  it matches either 'myvalue' or 'source::*myvalue' terms).
* Defaults to true.
* NOTE: You only need to set indexed_value if indexed = false.
