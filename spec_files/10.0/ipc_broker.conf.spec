#   Version 9.4.3
#
############################################################################
# OVERVIEW
############################################################################
# This file contains descriptions of the settings that you can use to
# configure the inter-process communication (IPC) broker.
#
# There is an ipc_broker.conf file in the $SPLUNK_HOME/etc/system/default/ directory.
# Never change or copy the configuration files in the default directory.
# The files in the default directory must remain intact and in their original
# location.
#
# To set custom configurations, create a new file with the name ipc_broker.conf in
# the $SPLUNK_HOME/etc/system/local/ directory. Then add the specific settings
# that you want to customize to the local configuration file.
# You must restart the Splunk instance to enable configuration changes.
#
# To learn more about configuration files (including file precedence) see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles


# IPC broker settings. This stanza must exist.
[ipc_broker_main]
port = <integer>
* The TCP/IP network port that the IPC broker process uses to serve incoming requests.
* The lowest valid value is 1025 and the highest is 65535.
* No default.


# Splunkd helper process settings.
[<splunkd_helper_process_name>:<service_name>]
* Use this stanza type to specify settings for a specific service within
  a helper process for splunkd. If you do not specify a <service_name>, then the settings
  apply to the default service within that [<splunkd_helper_process_name>].
port = <integer>
* The TCP/IP network port that the splunkd helper process uses to serve incoming requests.
* The lowest valid value is 1025 and the highest is 65535.
* No default.
