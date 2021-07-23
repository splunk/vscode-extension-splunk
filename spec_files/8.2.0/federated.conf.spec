#   Version 8.2.0
#
# This file contains possible setting and value pairs for federated provider entries
# for use in Data Fabric Search (DFS), when the federated search functionality is
# enabled.
#
# A federated search allows authorized users to run searches across multiple federated
# providers. Only Splunk deployments are supported as federated providers. Information
# on the Splunk deployment (i.e. the federated provider) is added in the federated
# provider stanza of the federated.conf file. A federated search deployment can have
# multiple federated search datasets. The settings for federated search dataset stanzas
# are located in savedsearches.conf.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles
#
# Here are the settings for the federated provider stanzas.

[<federated-provider-stanza>]
* Create a unique stanza name for each federated provider.

type = [splunk]
* Specifies the type of the federated provider.
* Only Splunk deployments are supported as of this revision.
* Default: splunk

ip = <IP address or Host Name>
* Identifies the IP address or host name of the federated provider.
* Default: No default.

splunk.port = <port>
* Identifies the splunkd REST port on the remote Splunk deployment.
* No default.

splunk.serviceAccount = <user>
* Identifies an authorized user on the remote Splunk deployment.
* The security credentials associated with this account are managed securely in
  fshpasswords.conf.
* No default.

splunk.app = <string>
* The name of the Splunk application on the remote Splunk deployment in which
* to perform the search.
* No default.

#
# Federated Provider Stanza
#
[provider]
* Each federated provider definition must have a separate stanza.
* <provider> must follow the following syntax: 
  provider://<unique-federated-provider-name>
* <unique-federated-provider-name> can contain only alphanumeric characters and 
  underscores.

type = [splunk]
* Specifies the type of the federated provider.
* Only Splunk deployments are supported as of this version.
* Default: splunk

hostPort = <Host_Name_or_IP_Address>:<service_port>
* Specifies the protocols required to connect to a federated provider.
* You can provide a host name or an IP address.
* The <service_port> can be any legitimate port number.
* No default.

serviceAccount = <user_name>
* Specifies the user name for a service account that has been set up on the
  federated provider for the purpose of enabling secure federated search.
* This service account allows the federated search head on your local Splunk
  platform deployment to query datasets on the federated provider in a secure
  manner.
* No default.

password = <password>
* Specifies the service account password for the user specified in the
  'serviceAccount' setting.
* No default.

appContext = <application_short_name>
* Specifies the Splunk application context for the federated searches that will
  be run with this federated provider definition.
* Provision of an application context ensures that federated searches which use
  the federated provider are limited to the knowledge objects that are
  associated with the named application. Application context can also affect
  search job quota and resource allocation parameters.
* NOTE: This setting applies only when `useFSHKnowledgeObjects = false`.
* <application_short_name> must be the "short name" of a Splunk application
  currently installed on the federated provider. For example, the short name of
  Splunk IT Service Intelligence is 'itsi'.
* You can create multiple federated provider definitions for the same remote
  search head that differ only by app context.
* Find the short names of apps installed on a Splunk deployment by going to
  'Apps > Manage Apps' and reviewing the values in the 'Folder name' column.
* Default: search

useFSHKnowledgeObjects = <boolean>
* Determines whether federated searches with this provider use knowledge
  objects from the federated provider (the remote search head) or from the
  federated search head (the local search head).
* When set to 'true' federated searches with this provider use knowledge
  objects from the federated search head.
* Default: true

