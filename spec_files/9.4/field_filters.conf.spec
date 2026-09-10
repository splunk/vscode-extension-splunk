#   Version 9.4.3
#
############################################################################
READ THIS FIRST: Should you deploy field filters in your organization?
############################################################################
# Field filters is a powerful tool that can help many organizations protect 
# their sensitive fields from prying eyes, but it might not be a good fit 
# for everyone. If your organization runs Splunk Enterprise Security or if 
# your users rely heavily on commands that field filters restricts by default
# (mpreview, mstats, tstats, typeahead, and walklex), do not use field filters 
# in production until you have thoroughly planned how you will work around 
# these restricted commands. For more information about restricted commands,
# search for "Plan for field filters in your organization" in Securing 
# Splunk Platform in the Splunk Docs. 
# 
############################################################################ 
# OVERVIEW
############################################################################
# This file contains descriptions of the settings that you can use to
# configure field filters in the field_filters.conf file.
#
# To learn about how to protect PII, PHI, and other sensitive data with 
# field filters, search for "Protect PII, PHI, and other sensitive data 
# with field filters" in Securing Splunk Platform in the Splunk Docs. 
#
# Configurations for field filters are stored in
# etc/system/local/field_filters.conf.
# To customize your configuration, create a field_filters.conf file
# at $SPLUNK_HOME/etc/system/local if you are using *nix, or
# %SPLUNK_HOME%\etc\system\local if you are using Windows.

[<fieldFilterName>]
* Field filter names can contain only alphanumeric characters and
  underscores "_".
* Each field filter must have a unique name.

action = <field> = <operator>
* BNF for <action> syntax:
    <action>          ::= <field> = <operator>
    <operator>        ::= null() | sha256() | sha512() | <string literal>
                            | sed(<string literal>)
    <field>           ::= <string literal>
* An operator for an action can be one of the following:
    * null(): Removes the <field> from results of
      searches to which this filter is applied.
      For example: action = "password"=null()
    * sha256(): Hashes the <field> value with a SHA-256 hash
      wherever the <field> appears in results of searches to which this 
      filter is applied.
      For example: action = "userid"=sha256()
    * sha512(): Hashes the <field> value with a SHA-512 hash
      wherever the <field> appears in results of searches to which this 
      filter is applied.
      For example: action = "userid"=sha512()
    * <string literal>: Replaces the <fieldname> value
      with the specified string wherever the <field> value appears in results 
      of searches to which this filter is applied.
      For example: action = "ssn"="xxx-xx-xxx"
    * sed(<string literal>): Uses the sed expression on the '_raw' field to 
      which this filter is applied. The sed expression replaces strings in raw
      events that are matched by a regular expression (s) or transliterates 
      characters found in raw events with corresponding characters 
      provided by the sed expression (y).
      For example: action = "_raw"=sed("s/drop_count=0/drop_count=ZERO/g")
* <string literal> is a sequence of characters enclosed in double quotation 
  marks (" "). Use \ to escape the characters \ and " in a string literal 
  (\\ and \" respectively).
* No default.
* Required.

limit = [<limit_type>::<string>]
* Apply the action of a field filter to events matching the specified
  'host', 'source', or 'sourcetype' limit.
* Use <limit_type> to specify the limit type: 'host', 'source', or 'sourcetype'.
  You can't specify multiple limit types in a single field filter.
* Use <string> to specify a value or a list of comma-separated values for
  the specified limit.
* Example 1: limit = sourcetype::access_combined
  The field filter acts on events that match the 'access_combined' source type.
* Example 2: limit = sourcetype::st1,st2,st3
  The field filter acts on events that match any of the following source types:
  'st1', 'st2', or 'st3'.
* No default.
* Optional.

index = <string>
* Apply the action of a field filter to events from the specified indexes.
* Use <string> to specify an index name or a list of comma-separated index
  names.
* Example 1: index = myidx
  A field filter acts on events from the 'myidx' index.
* Example 2: index = idx1,idx2,idx3
  A field filter acts on events from any of the following indexes:
  'idx1', 'idx2', or 'idx3'.
* No default.
* Required.

description = <string>
* Used to store a description of the field filter.
* No default.
* Optional.

roleExemptions = <string>
* To maintain data security and integrity, do not manually change this setting.
* Identifies the user roles that are exempt from this field filter.
* This setting is automatically generated by Splunk Web or Splunk platform
  REST API requests, and should not be manually edited.
* <string> indicates a role name or a list of comma-separated role
  names that are exempt from this field filter.
* This setting and the 'fieldFilterExemption' setting in the 'authorize.conf'
  file are both required to exempt a role from a field filter.
* Example 1: roleExemptions = myrole
  A field filter is not applied to searches of a user who has the role "myrole".
* Example 2: roleExemptions = role_1,role_2,role_3
  A field filter is not applied to searches of a user who has any of the 
  following roles: "role_1", "role_2", "role_3".
* No default.
* Optional.
