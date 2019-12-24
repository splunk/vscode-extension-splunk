#   Version 7.3.0
#
# This file maintains the state of a given app in Splunk Enterprise. It may also be used
# to customize certain aspects of an app.
#
# There is no global, default app.conf. Instead, an app.conf may exist in each
# app in Splunk Enterprise.
#
# You must restart Splunk Enterprise to reload manual changes to app.conf.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

#
# Settings for how an app appears in Launcher (and online on Splunkbase)
#

[author=<name>]
email = <e-mail>
company = <company-name>

[id]
group = <group-name>
name = <app-name>
version = <version-number>

[launcher]

# global setting

remote_tab = <bool>
* Set whether the Launcher interface will connect to apps.splunk.com.
* This setting only applies to the Launcher app and should be not set in any
  other app
* Defaults to true.

# per-application settings

version = <version string>
* Version numbers are a number followed by a sequence of dots and numbers.
* Version numbers for releases should use three digits.
* Pre-release versions can append a single-word suffix like "beta" or "preview."
* Pre-release designations should use lower case and no spaces.
* Examples:
  * 1.2.0
  * 3.2.1
  * 11.0.34
  * 2.0beta
  * 1.3beta2
  * 1.0preview

description = <string>
* Short explanatory string displayed underneath the app's title in Launcher.
* Descriptions should be 200 characters or less because most users won't read
  long descriptions!

author = <name>
* For apps you intend to post to Splunkbase, enter the username of your
  splunk.com account.
* For internal-use-only apps, include your full name and/or contact info
  (e.g. email).

# Your app can include an icon which will show up next to your app in Launcher
# and on Splunkbase. You can also include a screenshot, which will show up on
# Splunkbase when the user views info about your app before downloading it.
# You do not need to include an icon, but if you do, icon file names must end 
# with "Icon" before the file extension, and the "I" must be capitalized. For
# example, "mynewIcon.png".
# Screenshots are optional.
#
# There is no setting in app.conf for these images. Splunk Web places files you
# upload into the <app_directory>/appserver/static directory. These images will  
# not appear in your app. 
#
# Move or place icon images to the <app_directory>/static directory.
# Move or place screenshot images to the <app_directory>/default/static directory.
# Launcher and Splunkbase will automatically detect the images.
#
# For example:
#
#     <app_directory>/static/appIcon.png    (the capital "I" is required!)
#     <app_directory>/default/static/screenshot.png
#
# An icon image must be a 36px by 36px PNG file.
# An app screenshot must be 623px by 350px PNG file.
#
#
# [package] defines upgrade-related metadata, and will be
# used in future versions of Splunk Enterprise to streamline app upgrades.
#

[package]

id = <appid>
* id should be omitted for internal-use-only apps which are not intended to be
  uploaded to Splunkbase
* id is required for all new apps uploaded to Splunkbase. Future versions of
  Splunk Enterprise will use appid to correlate locally-installed apps and the
  same app on Splunkbase (e.g. to notify users about app updates)
* id must be the same as the folder name in which your app lives in
  $SPLUNK_HOME/etc/apps
* id must adhere to cross-platform folder-name restrictions:
  * must contain only letters, numbers, "." (dot), and "_" (underscore) characters
  * must not end with a dot character
  * must not be any of the following names: CON, PRN, AUX, NUL,
      COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9,
      LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9

check_for_updates = <bool>
* Set whether Splunk Enterprise should check Splunkbase for updates to this app.
* Defaults to true.


#
# Set install settings for this app
#

[install]

state = disabled | enabled
* Set whether app is disabled or enabled.
* If an app is disabled, its configs are ignored.
* Defaults to enabled.

state_change_requires_restart = true | false
* Set whether changing an app's state ALWAYS requires a restart of Splunk Enterprise.
* State changes include enabling or disabling an app.
* When set to true, changing an app's state always requires a restart.
* When set to false, modifying an app's state may or may not require a restart
  depending on what the app contains. This setting cannot be used to avoid all
  restart requirements!
* Defaults to false.

is_configured = true | false
* Stores indication of whether the application's custom setup has been performed
* Defaults to false

build = <integer>
* Required.
* Must be a positive integer.
* Increment this whenever you change files in appserver/static.
* Every release must change both "version" and "build" settings.
* Ensures browsers don't use cached copies of old static files
  in new versions of your app.
* Build is a single integer, unlike version which can be a complex string
  like 1.5.18.

allows_disable = true | false
* Set whether an app allows itself to be disabled.
* Defaults to true.

install_source_checksum = <string>
* Records a checksum of the tarball from which a given app was installed.
* Splunk Enterprise will automatically populate this value upon install.
* You should *not* set this value explicitly within your app!

install_source_local_checksum = <string>
* Records a checksum of the tarball from which a given app's local configuration
* was installed. Splunk Enterprise will automatically populate this value upon
* install. You should *not* set this value explicitly within your app!

#
# Handle reloading of custom .conf files (4.2+ versions only)
#

[triggers]

reload.<conf_file_name> = [ simple | rest_endpoints | access_endpoints <handler_url> | http_get <handler_url> | http_post <handler_url> ]
* Splunk Enterprise will reload app configuration after every app-state change:
  install, update, enable, and disable.
* If your app does not use a custom config file (e.g. myconffile.conf)
  then it won't need a [triggers] stanza, because
  $SPLUNK_HOME/etc/system/default/app.conf already includes a [triggers]
  stanza which automatically reloads config files normally used by Splunk Enterprise.
* If your app uses a custom config file (e.g. myconffile.conf) and you want to
  avoid unnecessary Splunk Enterprise restarts, you'll need to add a reload value in
  the [triggers] stanza.
* If you don't include [triggers] settings and your app uses a custom
  config file, a Splunk Enterprise restart will be required after every state change.
* Specifying "simple" implies that Splunk Enterprise will take no special action to
  reload your custom conf file.
* Specify "access_endpoints" and a URL to a REST endpoint, and Splunk Enterprise will
  call its _reload() method at every app state change.
* Specify "http_get" and a URL to a REST endpoint, and Splunk Enterprise will simulate
  an HTTP GET request against this URL at every app state change.
* Specify "http_post" and a URL to a REST endpoint, and Splunk Enterprise will simulate
  an HTTP POST request against this URL at every app state change.
* "rest_endpoints" is reserved for Splunk Enterprise internal use for reloading
  restmap.conf.

* Examples:

#       [triggers]
#       # Do not force a restart of Splunk Enterprise for state changes of MyApp
# 		# Do not run special code to tell MyApp to reload myconffile.conf
#       # Apps with custom config files will usually pick this option
#       reload.myconffile = simple
#
# 		# Do not force a restart of Splunk Enterprise for state changes of MyApp.
# 		# Splunk Enterprise calls the /admin/myendpoint/_reload method in my custom
# 		# EAI handler.
# 		# Use this advanced option only if MyApp requires custom code to reload
# 		# its configuration when its state changes
#       reload.myotherconffile = access_endpoints /admin/myendpoint

[shclustering]
deployer_lookups_push_mode = preserve_lookups | always_preserve | always_overwrite
* Determines the deployer_lookups_push_mode for the 'splunk apply
  shcluster-bundle' command.
* If set to preserve_lookups, the 'splunk apply shcluster-bundle' command
  honors the '-preserve-lookups' option as it appears on the command line. If
  '-preserve-lookups' is flagged as "true", then lookup tables for this app are
  preserved. Otherwise, lookup tables are overwritten.
* If set to always_preserve, the 'splunk apply shcluster-bundle' command ignores
  the '-preserve-lookups' option as it appears on the command line and lookup
  tables for this app are always preserved.
* If set to always_overwrite, the 'splunk apply shcluster-bundle' command
  ignores the '-preserve-lookups' option as it appears on the command line and
  lookup tables for this app are always overwritten.
* Default: preserve_lookups

deployer_push_mode = full | merge_to_default | local_only | default_only
* full: This option bundles all of the app's contents located in default/,
  local/, users/<app>/, and other app subdirs. It then pushes the bundle to
  the members. When applying the bundle on a member, the non-local and
  non-user configurations from the deployer's app folder are copied to the
  member's app folder, overwriting existing contents. Local and user
  configurations are merged with the corresponding folders on the member,
  such that member configuration takes precedence.  This option should not
  be used for built-in apps, as overwriting the member's built-in apps may
  result in adverse behavior.
* merge_to_default: This option merges the local and default folders into
  the default folder and pushes the merged app to the members. When
  applying the bundle on a member, the default configuration on the member
  is overwritten. User configurations are copied and merged with the user
  folder on the member, such that the existing configuration on the member
  takes precedence. In versions 7.2 and prior, this was the only behavior.
  This is the default mode if deployer_push_mode is not specified for an
  app, except for built-in apps, which default to local_only.
* local_only: This option bundles the app's local directory (and its
  metadata) and pushes it to the cluster. When applying the bundle to a
  member, the local configuration from the deployer is merged with the
  local configuration on the member, such that the member's existing
  configuration takes precedence. Use this option to push the local
  configuration of built-in apps, such as search. If used to push an app
  that relies on non-local content (such as default/ or bin/), these
  contents must already exist on the member.
* default_only: This option bundles all of the configuration files except
  for local and users/<app>/.  When applying the bundle on a member, the
  contents in the member's default folder are overwritten.

#
# Set UI-specific settings for this app
#

[ui]

is_visible = true | false
* Indicates if this app should be visible/navigable as a UI app
* Apps require at least 1 view to be available from the UI

show_in_nav = true | false
* Indicates if this app should be shown in global app dropdown

is_manageable = true | false
* Support for this setting has been removed. It no longer has any effect.

label = <string>
* Defines the name of the app shown in the Splunk Enterprise GUI and Launcher
* Recommended length between 5 and 80 characters.
* Must not include "Splunk For" prefix.
* Label is required.
* Examples of good labels:
    IMAP Monitor
    SQL Server Integration Services
    FISMA Compliance

docs_section_override = <string>
* Defines override for auto-generated app-specific documentation links
* If not specified, app-specific documentation link will
  include [<app-name>:<app-version>]
* If specified, app-specific documentation link will
  include [<docs_section_override>]
* This only applies to apps with documentation on the Splunk documentation site

attribution_link = <string>
* URL that users can visit to find third-party software credits and attributions for assets the app uses.
* External links must start with http:// or https://.
* Values that do not start with http:// or https:// will be interpreted as Quickdraw "location" strings
* and translated to internal documentation references.

setup_view = <string>
* Optional setting
* Defines custom setup view found within /data/ui/views REST endpoint
* If not specified, default to setup.xml

#
# Credential-verification scripting (4.2+ versions only)
# Credential entries are superseded by passwords.conf from 6.3 onwards.
# While the entries here are still honored post-6.3, updates to these will occur in passwords.conf which will shadow any values present here.
#

[credentials_settings]
verify_script = <string>
* Optional setting.
* Command line to invoke to verify credentials used for this app.
* For scripts, the command line should include both the interpreter and the
  script for it to run.
    * Example: "$SPLUNK_HOME/bin/python" "$SPLUNK_HOME/etc/apps/<myapp>/bin/$MY_SCRIPT"
* The invoked program is communicated with over standard in / standard out via
  the same protocol as splunk scripted auth.
* Paths incorporating variable expansion or explicit spaces must be quoted.
  * For example, a path including $SPLUNK_HOME should be quoted, as likely
    will expand to C:\Program Files\Splunk

[credential:<realm>:<username>]
password = <password>
* Password that corresponds to the given username for the given realm.
  Note that realm is optional
* The password can be in clear text, however when saved from splunkd the
  password will always be encrypted

# diag app extensions, 6.4+ only
[diag]
extension_script = <filename>
* Setting this variable declares that this app will put additional information
  into the troubleshooting & support oriented output of the 'splunk diag'
  command.
* Must be a python script.
* Must be a simple filename, with no directory separators.
* The script must exist in the 'bin' sub-directory in the app.
* Full discussion of the interface is located on the Developer portal.
  See http://dev.splunk.com/view/SP-CAAAE8H
* Defaults to unset, no app-specific data collection will occur.

data_limit = <positive integer>[b|kb|MB|GB]
* Defines a soft-ceiling for the amount of uncompressed data that should be
  added to the diag by the app extension.
* Large diags damage the main functionality of the tool by creating data blobs
  too large to copy around or upload.
* Use this setting to ensure that your extension script does not accidentally
  produce far too much data.
* Once data produced by this app extension reaches the limit, diag will not add
  any further files on behalf of the extension.
* After diag has finished adding a file which goes over this limit, all further files
  will not be added.
* Must be a positive number followed by a size suffix.
  * Valid suffixes: b: bytes, kb: kilobytes, mb: megabytes, gb: gigabytes
  * Suffixes are case insensitive.
* Defaults to 100MB.


# Other diag settings

default_gather_lookups = <filename> [, <filename> ...]
* Setting this variable declares that the app contains lookups which should
  always be gathered by diag (by default).
* Essentially, if there are lookups which are useful for troubleshooting an
  app, and will never contain sensitive (user) data, they can be added to this
  list, and they will appear in generated diags for use when troubleshooting
  the app from customer diags.
* Any files in lookup dirs which are not listed here are not gathered by
  default; this can be overridden with the diag flag --include-lookups
* This setting is new in Splunk Enterprise/Light version 6.5.  Older versions
  gather all lookups by default.
* This does not override the size-ceiling on files in etc.  Large lookups will
  still be excluded, unless the etc-filesize-limit is raised/disabled.
* This controls only files in the same app directory as this conf file.  For
  example, if you have an app directory in etc/slave-apps (index clustering),
  this setting must appear in etc/slave-apps/appname/default/app.conf or
  local/app.conf
* Additional lists can be created with default_gather_lookups-classname = ...
* Defaults to unset.
