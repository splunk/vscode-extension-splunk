#   Version 7.3.0
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

ip = <IP address>
* Identifies the IP address of the federated provider.
* Default: No default.

splunk.port = <port>
* Identifies the splunkd REST port on the remote Splunk deployment.
* Default: No default.

splunk.serviceAccount = <user>
* Identifies an authorized user on the remote Splunk deployment.
* The security credentials associated with this account are managed securely in
  fshpasswords.conf.
* Default: No default.

splunk.app = <string>
* The name of the Splunk application on the remote Splunk deployment in which
* to perform the search.
* Default: No default.
