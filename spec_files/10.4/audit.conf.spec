#   Version 10.4.2
#
# This file contains possible attributes and values you can use to configure
# auditing in audit.conf.
#
# There is an audit.conf file in the $SPLUNK_HOME/etc/system/default/ directory.
# Never change or copy the configuration files in the default directory.
# The files in the default directory must remain intact and in their original
# location.
#
# To set custom configurations, place an
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
* Default: both


[auditconfig:/path]
enabled = <comma-separated list>
* Lists the audit actions that the system explicitly logs for the 
  Representational State Transfer (REST) resource identified by
  ``/path`` (for example ``/servicesNS/admin/app``).
* A value of "all" means that the system activates logging for every action in the stanza. 
  Child stanzas inherit activated actions from their parent stanzas, 
  but they can override the inherited actions by defining their own settings.
* Protected actions such as ``delete`` always remain logged even if the setting omits them.

disabled = <comma-separated list>
* Lists the audit actions that the system explicitly skips for the stanza path.
* A value of "all" deactivates logging for every action in the stanza. Child stanzas inherit 
  deactivated actions unless they override them with their own settings.
* The system ignores attempts to deactivate protected actions like ``delete``
  and generates a warning in splunkd.log.

sampling.<action> = <positive integer>
* Activates sampling for a specific action. The integer value represents the sampling interval,
  meaning "log 1 out of N" events. For example, ``sampling.edit = 5`` logs the
  first event and then every fifth edit event.
* Use ``sampling.*`` as a wildcard to apply the same interval to every action
  that the stanza governs.
* The system ignores sampling for protected actions (``delete`` and the authentication
  categories) and when the generated sampling key exceeds internal limits.
* Sampling applies only when the action is otherwise activated; if an action is
  deactivated, the system logs no events regardless of the sampling interval.

Note:* If no stanza matches a given path, the system logs audit actions by default.
Stanzas inherit settings from their nearest parent path. For example,
``[auditconfig:/services]`` applies to ``[auditconfig:/services/foo]`` unless
the child stanza overrides the same setting.
All settings in [auditconfig:/path] stanzas take effect when you reload 
the audit subsystem or the audit.conf file using the REST API.

