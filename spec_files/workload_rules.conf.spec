#   Version 7.3.0
#
############################################################################
# OVERVIEW
############################################################################
# This file contains descriptions of the settings that you can use to
# configure workloads classification rules for splunk.
#
# There is a workload_rules.conf file in the $SPLUNK_HOME/etc/system/default/ directory.
# Never change or copy the configuration files in the default directory.
# The files in the default directory must remain intact and in their original
# location.
#
# To set custom configurations, create a new file with the name workload_rules.conf in
# the $SPLUNK_HOME/etc/system/local/ directory. Then add the specific settings
# that you want to customize to the local configuration file.
# For examples, see workload_rules.conf.example. You do not need to restart the Splunk instance
# to enable workload_rules.conf configuration changes.
#
# To learn more about configuration files (including file precedence) see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles
#
############################################################################
# GLOBAL SETTINGS
############################################################################
# Use the [default] stanza to define any global settings.
#   * You can also define global settings outside of any stanza, at the top of
#     the file.
#   * Each .conf file should have at most one default stanza. If there are
#     multiple default stanzas, settings are combined. In the case of
#     multiple definitions of the same setting, the last definition in the
#     file takes precedence.
#   * If a setting is defined at both the global level and in a specific
#     stanza, the value in the specific stanza takes precedence.
#
# CAUTION: Do not alter the settings in the workload_rules.conf file unless you know
#     what you are doing.  Improperly configured workload rules might result in
#     splunkd crashes, memory overuse, or both.

[workload_rule:<rule_name>]
predicate = <string>
* Specifies the predicate of this workload classification rule.
* The format is logical expression with predicate as <type>=<value>.
* For example, "app=search AND (NOT role=power)".
* The valid <type> are "app", "role", "user", and
  "index". The <value> is the exact value of the <type>.
* For "app" type, the value is the name of the app. For example, "app=search".
* For "role" type, the value is the name of the role. For example, "role=admin".
* For "index" type, the value is the name of the index. For example,
  "index=_internal". Note that the value can refer to an internal or public index.
* For "user" type, the value is the name of any valid user. For example,
  "user=bob". Note that the reserved internal user "noboby" is invalid; the
  reserved internal user "splunk-system-user" is valid.
* Required.

workload_pool = <string>
* Specifies the name of the workload pool, for example "pool1".
* The pool name specified must be defined earlier through [workload_pool:<pool_name>] stanza in
  workload_pools.conf.
* Required

[workload_rules_order]
rules = <string>
* List of all workload classification rules.
* The format of the "string" is comma separated items, "rule1,rule2,...".
* The rules listed are defined in [workload_rule:<rule_name>] stanza.
* The order of the rule name in the list determines the priorities of that rule.
  For example, in "rule1,rule2", rule1 has higher priority than rule2.
* The default value for this property is empty, meaning there is no rule defined.

