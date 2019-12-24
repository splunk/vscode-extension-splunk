#   Version 7.3.0
#
# This file contains possible attribute and value pairs for creating new
# Representational State Transfer (REST) endpoints.
#
# There is a restmap.conf in $SPLUNK_HOME/etc/system/default/. To set custom
# configurations, place a restmap.conf in $SPLUNK_HOME/etc/system/local/. For
# help, see restmap.conf.example. You must restart Splunk to enable
# configurations.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# NOTE: You must register every REST endpoint via this file to make it
# available.

###########################
# Global stanza

[global]
* This stanza sets global configurations for all REST endpoints.
* Follow this stanza name with any number of the following attribute/value
  pairs.

allowGetAuth=[true|false]
* Allow user/password to be passed as a GET parameter to endpoint
  services/auth/login.
* Setting this to true, while convenient, may result in user/password getting
  logged as cleartext in Splunk's logs *and* any proxy servers in between.
* Defaults to false.

allowRestReplay=[true|false]
* POST/PUT/DELETE requests can be replayed on other nodes in the deployment.
* This enables centralized management.
* Turn on or off this feature. You can also control replay at each endpoint
  level. This feature is currently INTERNAL and should not be turned on witout
  consulting splunk support.
* Defaults to false

defaultRestReplayStanza=<string>
* Points to global rest replay configuration stanza.
* Related to allowRestReplay
* Defaults to "restreplayshc"

pythonHandlerPath=<path>
* Path to 'main' python script handler.
* Used by the script handler to determine where the actual 'main' script is
  located.
* Typically, you should not need to change this.
* Defaults to $SPLUNK_HOME/bin/rest_handler.py.

###########################
# Applicable to all REST stanzas
# Stanza definitions below may supply additional information for these.
#

[<rest endpoint name>:<endpoint description string>]
match=<path>
* Specify the URI that calls the handler.
* For example if match=/foo, then https://$SERVER:$PORT/services/foo calls this
  handler.
* NOTE: You must start your path with a /.

requireAuthentication=[true|false]
* This optional attribute determines if this endpoint requires authentication.
* Defaults to 'true'.

authKeyStanza=<stanza>
* This optional attribute determines the location of the pass4SymmKey in the
  server.conf to be used for endpoint authentication.
* Defaults to 'general' stanza.
* Only applicable if the requireAuthentication is set true.

restReplay=[true|false]
* This optional attribute enables rest replay on this endpoint group
* Related to allowRestReplay
* This feature is currently INTERNAL and should not be turned on without consulting
  splunk support.
* Defaults to false

restReplayStanza=<string>
* This points to stanza which can override the [global]/defaultRestReplayStanza
  value on a per endpoint/regex basis
* Defaults to empty

capability=<capabilityName>
capability.<post|delete|get|put>=<capabilityName>
* Depending on the HTTP method, check capabilities on the authenticated session user.
* If you use 'capability.post|delete|get|put,' then the associated method is
  checked against the authenticated user's role.
* If you just use 'capability,' then all calls get checked against this
  capability (regardless of the HTTP method).
* Capabilities can also be expressed as a boolean expression. Supported operators 
  include: or, and, ()

acceptFrom=<network_acl> ...
* Lists a set of networks or addresses to allow this endpoint to be accessed
  from.
* This shouldn't be confused with the setting of the same name in the
  [httpServer] stanza of server.conf which controls whether a host can
  make HTTP requests at all
* Each rule can be in the following forms:
    1. A single IPv4 or IPv6 address (examples: "10.1.2.3", "fe80::4a3")
    2. A CIDR block of addresses (examples: "10/8", "fe80:1234/32")
    3. A DNS name, possibly with a '*' used as a wildcard (examples:
       "myhost.example.com", "*.splunk.com")
    4. A single '*' which matches anything
* Entries can also be prefixed with '!' to cause the rule to reject the
  connection.  Rules are applied in order, and the first one to match is
  used.  For example, "!10.1/16, *" will allow connections from everywhere
  except the 10.1.*.* network.
* Defaults to "*" (accept from anywhere)

includeInAccessLog=[true|false]
* If this is set to false, requests to this endpoint will not appear
  in splunkd_access.log
* Defaults to 'true'.

###########################
# Per-endpoint stanza
# Specify a handler and other handler-specific settings.
# The handler is responsible for implementing arbitrary namespace underneath
# each REST endpoint.

[script:<uniqueName>]
* NOTE: The uniqueName must be different for each handler.
* Call the specified handler when executing this endpoint.
* The following attribute/value pairs support the script handler.

scripttype=python
* Tell the system what type of script to execute when using this endpoint.
* Defaults to python.
* If set to "persist" it will run the script via a persistent-process that
  uses the protocol from persistconn/appserver.py.

handler=<SCRIPT>.<CLASSNAME>
* The name and class name of the file to execute.
* The file *must* live in an application's bin subdirectory.
* For example, $SPLUNK_HOME/etc/apps/<APPNAME>/bin/TestHandler.py has a class
  called MyHandler (which, in the case of python must be derived from a base
  class called 'splunk.rest.BaseRestHandler'). The tag/value pair for this is:
  "handler=TestHandler.MyHandler".

xsl=<path to XSL transform file>
* Optional.
* Perform an optional XSL transform on data returned from the handler.
* Only use this if the data is XML.
* Does not apply to scripttype=persist.

script=<path to a script executable>
* For scripttype=python this is optional.  It allows you to run a script
  which is *not* derived from 'splunk.rest.BaseRestHandler'.  This is
  rarely used.  Do not use this unless you know what you are doing.
* For scripttype=persist this is the path with is sent to the driver
  to execute.  In that case, environment variables are substituted.

script.arg.<N>=<string>
* Only has effect for scripttype=persist.
* List of arguments which are passed to the driver to start the script .
* The script can make use of this information however it wants.
* Environment variables are substituted.

script.param=<string>
* Optional.
* Only has effect for scripttype=persist.
* Free-form argument that is passed to the driver when it starts the
  script.
* The script can make use of this information however it wants.
* Environment variables are substituted.

output_modes=<csv list>
* Specifies which output formats can be requested from this endpoint.
* Valid values are: json, xml.
* Defaults to xml.

passSystemAuth=<bool>
* Specifies whether or not to pass in a system-level authentication token on
  each request.
* Defaults to false.

driver=<path>
* For scripttype=persist, specifies the command to start a persistent
  server for this process.
* Endpoints that share the same driver configuration can share processes.
* Environment variables are substituted.
* Defaults to using the persistconn/appserver.py server.

driver.arg.<n> = <string>
* For scripttype=persist, specifies the command to start a persistent
  server for this process.
* Environment variables are substituted.
* Only takes effect when "driver" is specifically set.

driver.env.<name>=<value>
* For scripttype=persist, specifies an environment variable to set when running
  the driver process.

passConf=<bool>
* If set, the script is sent the contents of this configuration stanza
  as part of the request.
* Only has effect for scripttype=persist.
* Defaults to true.

passPayload=[true | false | base64]
* If set to true, sends the driver the raw, unparsed body of the
  POST/PUT as a "payload" string.
* If set to "base64", the same body is instead base64-encoded and
  sent as a "payload_base64" string.
* Only has effect for scripttype=persist.
* Defaults to false.

passSession=<bool>
* If set to true, sends the driver information about the user's
  session.  This includes the user's name, an active authtoken,
  and other details.
* Only has effect for scripttype=persist.
* Defaults to true.

passHttpHeaders=<bool>
* If set to true, sends the driver the HTTP headers of the request.
* Only has effect for scripttype=persist.
* Defaults to false.

passHttpCookies=<bool>
* If set to true, sends the driver the HTTP cookies of the request.
* Only has effect for scripttype=persist.
* Defaults to false.

#############################
# 'admin'
# The built-in handler for the Extensible Administration Interface.
# Exposes the listed EAI handlers at the given URL.
#

[admin:<uniqueName>]

match=<partial URL>
* URL which, when accessed, will display the handlers listed below.

members=<csv list>
* List of handlers to expose at this URL.
* See https://localhost:8089/services/admin for a list of all possible
  handlers.

#############################
# 'admin_external'
# Register Python handlers for the Extensible Administration Interface.
# Handler will be exposed via its "uniqueName".
#

[admin_external:<uniqueName>]

handlertype=<script type>
* Currently only the value 'python' is valid.

handlerfile=<unique filename>
* Script to execute.
* For bin/myAwesomeAppHandler.py, specify only myAwesomeAppHandler.py.

handlerpersistentmode=[true|false]
* Set to true to run the script in persistent mode and keep the process running
  between requests.

handleractions=<comma separated list>
* List of EAI actions supported by this handler.
* Valid values are: create, edit, list, delete, _reload.

#########################
# Validation stanzas
# Add stanzas using the following definition to add arg validation to
# the appropriate EAI handlers.

[validation:<handler-name>]

<field> =  <validation-rule> 

* <field> is the name of the field whose value would be validated when an
  object is being saved.
* <validation-rule> is an eval expression using the validate() function to
  evaluate arg correctness and return an error message. If you use a boolean
  returning function, a generic message is displayed.
* <handler-name> is the name of the REST endpoint which this stanza applies to
  handler-name is what is used to access the handler via
  /servicesNS/<user>/<app/admin/<handler-name>.
* For example:
  action.email.sendresult = validate( isbool('action.email.sendresults'), "'action.email.sendresults' must be a boolean value").
* NOTE: use ' or $ to enclose field names that contain non alphanumeric characters.

#############################
# 'eai'
# Settings to alter the behavior of EAI handlers in various ways.
# These should not need to be edited by users.
#

[eai:<EAI handler name>]

showInDirSvc = [true|false]
* Whether configurations managed by this handler should be enumerated via the
  directory service, used by SplunkWeb's "All Configurations" management page.
  Defaults to false.

desc = <human readable string>
* Allows for renaming the configuration type of these objects when enumerated
  via the directory service.


#############################
# Miscellaneous
# The un-described parameters in these stanzas all operate according to the
# descriptions listed under "script:", above.
# These should not need to be edited by users - they are here only to quiet
# down the configuration checker.
#

[input:...]
dynamic = [true|false]
* If set to true, listen on the socket for data.
* If false, data is contained within the request body.
* Defaults to false.

[peerupload:...]
path = <directory path>
* Path to search through to find configuration bundles from search peers.

untar = [true|false]
* Whether or not a file should be untarred once the transfer is complete.

[restreplayshc]
methods =  <comma separated strings>
* REST methods which will be replayed. POST, PUT, DELETE, HEAD, GET are the
  available options

nodelists = <comma separated string>
* strategies for replay. Allowed values are shc, nodes, filternodes
* shc - replay to all other nodes in Search Head Cluster
* nodes - provide raw comma separated URIs in nodes variable
* filternodes - filter out specific nodes. Always applied after other
  strategies

nodes = <comma separated management uris>
* list of specific nodes that you want the REST call to be replayed to

filternodes = <comma separated management uris>
* list of specific nodes that you do not want the REST call to be replayed to

[proxy:appsbrowser]
destination = <splunkbaseAPIURL>
* protocol, subdomain, domain, port, and path of the splunkbase api used to browse apps
* Defaults to https://splunkbase.splunk.com/api

