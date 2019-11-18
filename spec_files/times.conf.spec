#   Version 7.3.0
#
# This file contains possible attribute/value pairs for creating custom time
# ranges.
#
# To set custom configurations, place a times.conf in
# $SPLUNK_HOME/etc/system/local/.  For help, see times.conf.example. You
# must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see
# the documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#   * You can also define global settings outside of any stanza, at the top
#     of the file.
#   * Each conf file should have at most one default stanza. If there are
#     multiple default stanzas, attributes are combined. In the case of
#     multiple definitions of the same attribute, the last definition in the
#     file wins.
#   * If an attribute is defined at both the global level and in a specific
#     stanza, the value in the specific stanza takes precedence.


[<timerange_name>]
* The token to be used when accessing time ranges via the API or command
  line
* A times.conf file can contain multiple stanzas.

label = <string>
* The textual description used by the UI to reference this time range
* Required

header_label = <string>
* The textual description used by the UI when displaying search results in
  this time range.
* Optional.  If omitted, the <timerange_name> is used instead.

earliest_time = <string>
* The string that represents the time of the earliest event to return,
  inclusive.
* The time can be expressed with a relative time identifier or in epoch time.
* Optional.  If omitted, no earliest time bound is used.

latest_time = <string>
* The string that represents the time of the earliest event to return,
  inclusive.
* The time can be expressed with a relative time identifier or in epoch
  time.
* Optional.  If omitted, no latest time bound is used.  NOTE: events that
  occur in the future (relative to the server timezone) may be returned.

order = <integer>
* The key on which all custom time ranges are sorted, ascending.
* The default time range selector in the UI will merge and sort all time
  ranges according to the 'order' key, and then alphabetically.
* Optional.  Default value is 0.

disabled = <integer>
* Determines if the menu item is shown. Set to 1 to hide menu item.
* Optional. Default value is 0

sub_menu = <submenu name>
* REMOVED.  This setting is no longer used.

is_sub_menu = <boolean>
* REMOVED.  This setting is no longer used.

[settings]
* List of flags that modify the panels that are displayed in the time range picker.

show_advanced = [true|false]
* Determines if the 'Advanced' panel should be displayed in the time range picker
* Optional. Default value is true

show_date_range = [true|false]
* Determines if the 'Date Range' panel should be displayed in the time range picker
* Optional. Default value is true

show_datetime_range = [true|false]
* Determines if the 'Date & Time Range' panel should be displayed in the time range picker
* Optional. Default value is true

show_presets = [true|false]
* Determines if the 'Presets' panel should be displayed in the time range picker
* Optional. Default value is true

show_realtime = [true|false]
* Determines if the 'Realtime' panel should be displayed in the time range picker
* Optional. Default value is true

show_relative = [true|false]
* Determines if the 'Relative' panel should be displayed in the time range picker
* Optional. Default value is true
