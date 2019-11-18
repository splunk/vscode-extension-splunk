#   Version 7.3.0
#
# This file describes some of the settings that are used, and
# can be configured on a per-user basis for use by the Splunk Web UI.

# Settings in this file are requested with user and application scope of the
# relevant user, and the user-prefs app.

# Additionally, settings by the same name which are available in the roles
# the user belongs to will be used at lower precedence.

# This means interactive setting of these values will cause the values to be
# updated in
# $SPLUNK_HOME/etc/users/<username>/user-prefs/local/user-prefs.conf where
# <username> is the username for the user altering their preferences.

# It also means that values in another app will never be used unless they
# are exported globally (to system scope) or to the user-prefs app.

# In practice, providing values in other apps isn't very interesting, since
# values from the authorize.conf roles settings are more typically sensible
# ways to defaults for values in user-prefs.

[general]

default_namespace = <app name>
* Specifies the app that the user will see initially upon login to the
  Splunk Web User Interface.
* This uses the "short name" of the app, such as launcher, or search,
  which is synonymous with the app directory name.
* Splunk defaults this to 'launcher' via the default authorize.conf

tz = <timezone>
* Specifies the per-user timezone to use
* If unset, the timezone of the Splunk Server or Search Head is used.
* Only canonical timezone names such as America/Los_Angeles should be
  used (for best results use the Splunk UI).
* Defaults to unset.

lang = <language>
* Specifies the per-user language preference for non-webui operations, where
  multiple tags are separated by commas.
* If unset, English "en-US" will be used when required.
* Only tags used in the "Accept-Language" HTTP header will be allowed, such as
  "en-US" or "fr-FR".
* Fuzzy matching is supported, where "en" will match "en-US".
* Optional quality settings is supported, such as "en-US,en;q=0.8,fr;q=0.6"
* Defaults to unset.

install_source_checksum = <string>
* Records a checksum of the tarball from which a given set of private user
  configurations was installed.
* Analogous to <install_source_checksum> in app.conf.

search_syntax_highlighting = [light|dark|black-white]
* Highlights different parts of a search string with different colors.
* Defaults to light.
* Dashboards ignore this setting.

search_use_advanced_editor = <boolean>
* Specifies whether the search bar is run using the advanced editor or in just plain text.
* If set to false, search_auto_format, and search_line_numbers will be false and search_assistant can only be [full|none].
* Defaults to true.

search_assistant = [full|compact|none]
* Specifies the type of search assistant to use when constructing a search.
* Defaults to compact.

search_auto_format = <boolean>
* Specifies if auto-format is enabled in the search input.
* Default to false.

search_line_numbers = <boolean>
* Display the line numbers with the search.
* Defaults to false.

datasets:showInstallDialog = <boolean>
* Flag to enable/disable the install dialog for the datasets addon
* Defaults to true

dismissedInstrumentationOptInVersion = <integer>
* Set by splunk_instrumentation app to its current value of optInVersion when the opt-in modal is dismissed.

hideInstrumentationOptInModal = <boolean>
* Set to 1 by splunk_instrumentation app when the opt-in modal is dismissed.

[default]
# Additional settings exist, but are entirely UI managed.
<setting> = <value>

[general_default]
default_earliest_time = <string>
default_latest_time = <string>
* Sets the global default time range across all apps, users, and roles on the search page.

[role_<name>]

<name> = <value>
