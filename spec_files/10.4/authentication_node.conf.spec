#   Version 10.4.2
#
# This file contains possible settings and values for configuring
# node-local authentication settings via authentication_node.conf.
#
# To set custom configurations, place an authentication_node.conf
# file in $SPLUNK_HOME/etc/system/local/.
#
# To learn more about configuration files, including precedence, visit
# the Splunk Help website and search for "about configuration files".


[client_<string>]
* Settings that define an OAuth2 internal client.
* The '<string>' suffix in this stanza heading is the client ID.

id = <string>
* The client ID, as defined in the suffix of this stanza.
* The Splunk platform uses this value to identify the client during
  request handling and to look up the client configuration.
* Required.
* No default.

name = <string>
* A human-readable name for the OAuth2 client.
* This value does not have to be unique because the ID string in
  the stanza name identifies the client.
* Required.
* No default.

grantTypes = <semicolon-separated list>
* A list of OAuth2 grant types that this client can use.
* Valid values are "client_credentials" and "authorization_code". The list can
  contain either or both of these values.
* A value of "client_credentials" means that service-to-service grants
  are allowed for this OAuth2 client.
  * These grants do not involve an end user. The client authenticates with its
    own credentials and acts on its own behalf.
  * When 'grantTypes' includes "client_credentials", you must provide one or
    more roles for the 'roles' setting.
* A value of "authorization_code" means that this OAuth2 client can use
  user-to-service grants.
  * These grants involve an end user. The client obtains authorization and
    acts on behalf of the authenticated user.
* Required.
* No default.

jwks = <string>
* A JSON Web Key Set (JWKS) array of public keys that the Splunk platform
  uses to verify the signature on a signed client assertion and authenticate
  the OAuth2 client.
* When specifying a value for this setting, use the following format:
  * {"keys":[{<string>:<string>,<string>:<string>,...}]}
* Required if 'tokenEndpointAuthMethod' has a value of "private_key_jwt".
* No default.

roles = <semicolon-separated list>
* A list of roles that the Splunk platform grants to the OAuth2 client.
* Required when 'grantTypes' includes the value "client_credentials".
* No default.

tokenEndpointAuthMethod = private_key_jwt
* The requested authentication method.
* The only valid value is "private_key_jwt".
* Required.
* No default.

instanceId = <string>
* The Splunk instance ID.
* This ID is a globally unique identifier (GUID).
* You can obtain this ID by running an HTTP GET method against the
  /services/server/info REST endpoint and extracting the "guid" field.
* Required.
* No default.

redirectUris = <semicolon-separated list>
* A list of OAuth2 redirect URIs.
* Required when 'grantTypes' includes the value "authorization_code".
* Optional otherwise.
* No default.

responseTypes = <semicolon-separated list>
* A list of OAuth2 response types.
* Optional.
* No default.

scopes = <semicolon-separated list>
* A list of OAuth2 scopes that the OAuth2 client requests.
* Optional.
* No default.
