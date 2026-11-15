#   Version 10.6.1.1
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

redact_fields = <comma-separated list>
* A list of configuration files, stanzas, and settings whose values the Splunk
  platform must redact in log files that it writes.
* Provide the files, stanzas, and settings that must be redacted as a 
  field that includes 3 elements.
* Separate field elements with colons, and fields with commas. For example:
  <conf-file>:<stanza-prefix>:<setting>,<conf-file>:<stanza-prefix>:<setting>,...
* Each field must contain at least 2 colons that separate the field elements:
  * The first colon separates the configuration file name element from the
    stanza prefix element
  * The second colon separates the stanza prefix element from the
    setting name element
  * The Splunk platform treats the string between the first and last colon as
    the stanza prefix element
* Do not include stanza brackets when you specify a stanza prefix element.
* The Splunk platform automatically trims whitespace around colons. For example,
  "app: :api_key" and "app::api_key" are equivalent. This description shows
  examples without spaces for clarity, but spaces are acceptable.
* To represent a wildcard, leave the element empty between colons.
  Do not use asterisks (*) as wildcards. The Splunk platform will treat them 
  as literal characters.
* To match all stanzas from a configuration file, leave the ‘stanza-prefix’ element
  empty. For example: "app::api_key" matches all stanzas in the app.conf 
  configuration file that have 'api_key' as a setting.
* The stanza prefix also supports prefix matching. For example,
  "passwords:credential:password" matches stanzas in the passwords.conf file like
  '[credential:admin]' or '[credential:user]'.
* To match stanzas whose names include colons, you can include colons in stanza prefixes.
  For example:
  * "inputs:monitor://:host" matches the 'host' setting in inputs.conf stanzas
    like [monitor://var/log/app.log]
  * "outputs:tcpout:mygroup:server" matches the 'server' setting in outputs.conf
    stanzas like [tcpout:mygroup]
  * "passwords:credential:app:user" matches stanzas in passwords.conf like
    [credential:app:user] or [credential:app:user:admin]
* To match a field across all configuration files, leave the 'conf-file' element empty.
  For example: "::password" matches any setting named 'password' in any stanza
  of any configuration file.
* To match all properties in a stanza, leave the 'setting' element empty.
  For example: "server:general:" matches all properties in the [general] stanza
  of the server.conf file.
* You can combine wildcards. For example: "::" matches all properties in all
  stanzas of all configuration files.
* While it is possible for '<stanza-prefix>' elements to contain colons, 
  it is not possible for '<conf-file>' or '<setting>' elements to contain them. 
* There is no support for the following scenarios:
  * Specifying whitespace at the beginning or end of a stanza prefix
  * Specifying a file name, stanza name, or property names that contains
    one or more commas.
* The Splunk platform automatically redacts fields that you specify in the
  'encrypt_fields' setting in the server.conf file, in addition to fields
  that you redact using this setting.
* You must either reload the audit subsystem or the audit.conf configuration
  file directly through the REST API for changes to this setting to take affect.

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

[throttling]
eventCountThreshold = <nonnegative integer>
* Number of audit events per action, per user, before a summarized audit entry
  is generated.
* Throttling is disabled if this value is 0 or 1.
* Default: 1000

users = <colon-separated list>
* Users whose audit entries will be throttled.
* Default: internal_observability
