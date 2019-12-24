#   Version 7.3.0
#
# This file contains possible attributes and values you can use to configure
# auditing and event signing in audit.conf.
#
# There is NO DEFAULT audit.conf. To set custom configurations, place an
# audit.conf in $SPLUNK_HOME/etc/system/local/. For examples, see
# audit.conf.example.  You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#  * You can also define global settings outside of any stanza, at the top of the file.
#  * Each conf file should have at most one default stanza. If there are
#    multiple default stanzas, attributes are combined. In the case of multiple
#    definitions of the same attribute, the last definition in the file wins.
#  * If an attribute is defined at both the global level and in a specific
#    stanza, the value in the specific stanza takes precedence.

#########################################################################################
# KEYS: specify your public and private keys for encryption.
#########################################################################################

queueing=[true|false]
* Turn off sending audit events to the indexQueue -- tail the audit events
  instead.
* If this is set to 'false', you MUST add an inputs.conf stanza to tail the
  audit log in order to have the events reach your index.
  * Defaults to true.
