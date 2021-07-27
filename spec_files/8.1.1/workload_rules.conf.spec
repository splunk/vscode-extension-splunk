#   Version 8.1.1
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
* The valid <type> are "app", "role", "user", "index",
  "search_type", "search_mode" and "search_time_range". 
  The <value> is the exact value of the <type>.
* For "app" type, the value is the name of the app. For example, "app=search".
* For "role" type, the value is the name of the role. For example, "role=admin".
* For "index" type, the value is the name of the index. For example,
  "index=_internal". Note that the value can refer to an internal or public index.
* For "user" type, the value is the name of any valid user. For example,
  "user=bob". Note that the reserved internal user "noboby" is invalid; the
  reserved internal user "splunk-system-user" is valid.
* For "search_type" type, the value is the type of the search. Valid search 
  types include "adhoc", "scheduled", "datamodel_acceleration", 
  "report_acceleration" and "summary_index".
* For "search_mode" type, the value is the mode of the search. Valid modes 
  include "realtime" and "historical".
* For "search_time_range" type, the value is the time range of the search. 
  For now, value can only be "alltime".
* For "runtime" type, the value is the amount of time a search must run in a 
  workload pool to trigger a specified action, such as alert, move or abort.
  Valid units for runtime values include s, second, seconds, m, minute, minutes,
  and h, hour, hours.
* Required.

workload_pool = <string>
* Specifies the name of the workload pool, for example "pool1".
* The pool name that you specify must already be defined in the
  [workload_pool:<pool_name>] stanza in workload_pools.conf.

action = alert | move | abort
* Specifies the action to take when a search exceeds the specified runtime value.
* The action "alert" sends a notification message to Splunk Web that indicates
  the runtime of the search.
* The action "move" moves the search from the original workload pool to a
  designated alternate workload pool, and sends a notification message to
  Splunk Web.
* The action "abort" kills the search, and sends a notification message to
  Splunk Web.
* Optional.

schedule = always_on | time_range | every_day | every_week | every_month
* Specifies whether the rule is always on or has a valid time range that
  expires.
* Optional. If it's empty, it means the rule is always on.

start_time = <string>
* When 'schedule' is set to "time_range", 'start_time' specifies the exact time
  that the valid time range starts, including date, time and time zone.
* When 'schedule' is set to "every_week" or "every_month", it specifies
  the start hour.
* Optional.

end_time = <string>
* When 'schedule' is set to "time_range", 'end_time' specifies the exact time
  that the valid time range ends, including date, time and time zone.
* When 'schedule' is set to "every_week" or "every_month", it specifies the end
  hour.
* Optional.

every_week_days = <string>
* Specifies recurring days of the week.
* Supports numbers from 0 to 6, where 0 represents Sunday.
* Only applies when 'schedule' is set to "every_week".
* Optional.

every_month_days = <string>
* Specifies recurring days of the month.
* Supports numbers from 1 to 31, where 1 represents the 1st day of the month.
* Only applies when 'schedule' is set to "every_month".
* Optional.

user_message = <string>
* Specifies the message shown in the search job inspector if the rule is
  applied to a search.
* Cannot exceed 140 characters.
* Optional.

[workload_rules_order]
rules = <string>
* List of all workload classification rules.
* The format of the "string" is comma separated items, "rule1,rule2,...".
* The rules listed are defined in [workload_rule:<rule_name>] stanza.
* The order of the rule name in the list determines the priorities of that rule.
  For example, in "rule1,rule2", rule1 has higher priority than rule2.
* The default value for this property is empty, meaning there is no rule defined.

[search_filter_rule:<rule_name>]
predicate = <string>
* Specifies the predicate of this workload classification rule.
* The format is logical expression with predicate as <type>=<value>.
* For example, "app=search AND (NOT role=power)".
* The valid <type> are "app", "role", "user", "index",
  "search_type", "search_mode" and "search_time_range". 
  The <value> is the exact value of the <type>.
* For "app" type, the value is the name of the app. For example, "app=search".
* For "role" type, the value is the name of the role. For example, "role=admin".
* For "index" type, the value is the name of the index. For example,
  "index=_internal". Note that the value can refer to an internal or public index.
* For "user" type, the value is the name of any valid user. For example,
  "user=bob". Note that the reserved internal user "noboby" is invalid; the
  reserved internal user "splunk-system-user" is valid.
* For "search_type" type, the value is the type of the search. Valid search 
  types include "adhoc", "scheduled", "datamodel_acceleration", 
  "report_acceleration" and "summary_index".
* For "search_mode" type, the value is the mode of the search. Valid modes 
  include "realtime" and "historical".
* For "search_time_range" type, the value is the time range of the search. 
  For now, value can only be "alltime".
* Required.

action = filter
* Specifies the action to take when a search meets the rule criteria.
* The action "filter" is defined for search filter rules. If a search meets the rule
  criteria, the search is not executed.
* Required.

schedule = always_on | time_range | every_day | every_week | every_month
* Specifies whether the rule is always on or has a valid time range that
  expires.
* Optional. If it's empty, it means the rule is always on.

start_time = <string>
* When 'schedule' is set to "time_range", 'start_time' specifies the exact time
  that the valid time range starts, including date, time and time zone.
* When 'schedule' is set to "every_week" or "every_month", it specifies
  the start hour.
* Optional.

end_time = <string>
* When 'schedule' is set to "time_range", 'end_time' specifies the exact time
  that the valid time range ends, including date, time and time zone.
* When 'schedule' is set to "every_week" or "every_month", it specifies the end
  hour.
* Optional.

every_week_days = <string>
* Specifies recurring days of the week.
* Supports numbers from 0 to 6, where 0 represents Sunday.
* Only applies when 'schedule' is set to "every_week".
* Optional.

every_month_days = <string>
* Specifies recurring days of the month.
* Supports numbers from 1 to 31, where 1 represents the 1st day of the month.
* Only applies when 'schedule' is set to "every_month".
* Optional.

user_message = <string>
* Specifies the message when a search is filtered out by this rule.
* Cannot exceed 140 characters.
* Optional.
