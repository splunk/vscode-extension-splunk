#   Version 10.2.3
#
# This file contains possible attributes and values you can use to configure
# auditing in audit.conf.
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

[auditTrail]
queueing = <boolean>
* Whether or not audit events are sent to the indexQueue.
* If set to "true", audit events are sent to the indexQueue.
* If set to "false", you must add an inputs.conf stanza to tail the
  audit log for the events reach your index.
* Default: true

logging_format = v1|v2|both
* Specifies the log format of audit events sent to the indexQueue.
* A value of "v1" means Splunk software sends audit events in the legacy format
  with unchanged 'Audit:[...]' and fields.
* A value of "v2" means Splunk software sends audit events in a new JSONL format with
  enriched metadata.
* A value of "both" means Splunk software sends audit events in both "v1" and
  "v2" formats. Use this setting when transitioning from "v1" to "v2".
* Default: v1

