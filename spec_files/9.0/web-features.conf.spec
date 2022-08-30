#   Version 9.0.0.1
#
############################################################################
# OVERVIEW
############################################################################
# This file contains descriptions of the settings that you can use to
# configure Splunk features. These features are replicated in a Search Head
# Cluster environment.
#
# Each stanza controls a different web feature.
#
# For more information on configuration files, including precedence, search for
# "Use Splunk Web to manage configuration files" in the Admin Manual in the Splunk Docs.

[feature:quarantine_files]

enable_jQuery2 = <boolean>
* DEPRECATED.
* Determines whether or not Splunk Web can use jQuery 2 JavaScript files
  packaged with the Splunk platform.
* A "false" value means Splunk Web cannot use jQuery 2 JavaScript files
  packaged with the Splunk platform.
* CAUTION: Do not change this setting.
* Default: true

enable_unsupported_hotlinked_imports = <boolean>
* Determines whether or not Splunk Web can use unsupported JavaScript
  files that the Splunk platform will delete in a future release.
* Unsupported hotlinked imports are dependencies in your Simple XML Custom
  JavaScript Extensions that directly reference Splunk software.
* A "false" value means Splunk Web cannot use hotlinked imports
  that the Splunk platform will delete in a future release.
* CAUTION: Do not change this setting.
* Default: true
