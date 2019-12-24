#   Version 7.3.0
#
# This file maintains the credential information associated with a federated provider.
#
# There is no global, default fshpasswords.conf. Instead, anytime a user creates
# a new user or edit a user assocated with a federated provider onwards hitting
# the fsh storage endpoint will create this fshpasswords.conf file.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles


[credential:<federated-provider>:<username>:]
password = <password>
* Password that corresponds to the service account for the given federated provider.
* The password can be in clear text, however when saved from splunkd the
  password will always be encrypted
