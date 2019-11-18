#   Version 7.3.0
#
# This file contains possible attributes and values for configuring
# authentication via authentication.conf.
#
# There is an authentication.conf file in $SPLUNK_HOME/etc/system/default/.  To
# set custom configurations, place an authentication.conf in
# $SPLUNK_HOME/etc/system/local/. For examples, see
# authentication.conf.example. You must restart the Splunk software to enable
# configurations.
#
# To learn more about configuration files, including precedence, see
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles.

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#   * You can also define global settings outside of any stanza, at the top
#     of the file.
#   * Each .conf file should have at most one default stanza. If there are
#     multiple default stanzas, settings are combined. In the case of
#     multiple definitions of the same setting, the last definition in the
#     file wins.
#   * If a setting is defined at both the global level and in a specific
#     stanza, the value in the specific stanza takes precedence.

[authentication]
* Follow this stanza name with any number of the following setting/value
  pairs.

authType = [Splunk|LDAP|Scripted|SAML|ProxySSO]
* Specify which authentication system to use.
* Supported values: Splunk, LDAP, Scripted, SAML, ProxySSO.
* Default: Splunk.

authSettings = <authSettings-key>,<authSettings-key>,...
* Key to look up the specific configurations of chosen authentication
  system.
* <authSettings-key> is the name of a stanza header that specifies
  settings for scripted authentication, SAML, ProxySSO and for an LDAP
  strategy. Those stanzas are defined below.
* For LDAP, specify the LDAP strategy name(s) here. If you want Splunk
  software to query multiple LDAP servers, provide a comma-separated list
  of all strategies. Each strategy must be defined in its own stanza. 
  The order in which you specify the strategy names is the order Splunk
  software uses to query their servers when looking for a user.
* For scripted authentication, <authSettings-key> should be a single 
  stanza name.

passwordHashAlgorithm = [SHA512-crypt|SHA256-crypt|SHA512-crypt-<num_rounds>|SHA256-crypt-<num_rounds>|MD5-crypt]
* This controls how hashed passwords are stored in the
  $SPLUNK_HOME/etc/passwd file for the default "Splunk" authType.
* "MD5-crypt" is an algorithm originally developed for FreeBSD in the early
  1990s, which became a widely used standard among UNIX machines. Splunk 
  Enterprise also used it through the 5.0.x releases. MD5-crypt runs the
  salted password through a sequence of 1000 MD5 operations.
* "SHA256-crypt" and "SHA512-crypt" are newer versions that use 5000 rounds
  of the Secure Hash Algorithm-256 (SHA256) or SHA512 hash functions. 
  This is slower than MD5-crypt and therefore more resistant to dictionary 
  attacks.  SHA512-crypt is used for system passwords on many versions of Linux.
* These SHA-based algorithm can optionally be followed by a number of rounds
  to use. For example, "SHA512-crypt-10000" uses twice as many rounds
  of hashing as the default implementation. The number of rounds must be at
  least 1000.
  If you specify a very large number of rounds (i.e. more than 20x the
  default value of 5000), splunkd might become unresponsive and connections to
  splunkd (from splunkweb or CLI) time out.
* This setting only affects new password settings (either when a user is
  added or a user's password is changed).  Existing passwords work but retain their 
  previous hashing algorithm.
* Default: "SHA512-crypt".

defaultRoleIfMissing = <splunk role>
* Applicable for LDAP authType. If the LDAP server does not return any groups, or if
  groups cannot be mapped to Splunk roles, then this value is used, if provided.
* This setting is optional.
* Default: empty string

externalTwoFactorAuthVendor = <string>
* A valid multifactor vendor string enables multifactor authentication
  and loads support for the corresponding vendor if supported by the Splunk software.
* An empty string disables multifactor authentication in the Splunk software.
* Currently Splunk supports Duo and RSA as multifactor authentication vendors.
* This setting is optional.
* No default.

externalTwoFactorAuthSettings = <externalTwoFactorAuthSettings-key>
* Key to look up the specific configuration of chosen multifactor
  authentication vendor.
* This setting is optional.
* No default.

#####################
# LDAP settings
#####################

[<authSettings-key>]
* Follow this stanza name with the following setting/value pairs.
* For multiple strategies, specify multiple instances of
  this stanza, each with its own stanza name and a separate set of
  settings.
* The <authSettings-key> must be one of the values listed in the
  authSettings setting, which must be specified in the previous [authentication] 
  stanza.

host = <string>
* The hostname of the LDAP server.
* Confirm that your Splunk server can resolve the host name through DNS.
* Required.
* No default.

SSLEnabled = [0|1]
* Specifies whether SSL is enabled.
* See the file $SPLUNK_HOME/etc/openldap/ldap.conf for SSL LDAP settings
* This setting is optional.
* Default: 0 (disabled)

port = <integer>
* The port that Splunk software should use to connect to your LDAP server.
* This setting is optional.
* Default (non-SSL): 389
* Default (SSL): 636

bindDN = <string>
* The LDAP Distinguished Name of the user that retrieves the LDAP entries.
* This user must have read access to all LDAP users and groups you wish to
  use in the Splunk platform.
* This setting is optional. 
* Leave this setting blank to retrieve your LDAP entries using
  anonymous bind (which must be supported by the LDAP server)
* No default.

bindDNpassword = <password>
* Password for the bindDN user.
* This setting is optional. 
* Leave this blank if anonymous bind is sufficient.
* No default.

userBaseDN = <string>
* The distinguished names of LDAP entries whose subtrees contain the users.
* Enter a ';' delimited list to search multiple trees.
* Required.
* No default.

userBaseFilter = <string>
* The LDAP search filter to use when searching for users.
* Highly recommended, especially when there are many entries in your LDAP
  user subtrees.
* When used properly, search filters can significantly speed up LDAP queries
* Here is an example that matches users in the IT or HR department:
    * userBaseFilter = (|(department=IT)(department=HR))
    * See RFC 2254 for more detailed information on search filter syntax
* This setting is optional.
* Default: empty string (no filtering.)

userNameAttribute = <string>
* This is the username.
* NOTE: This setting should use case insensitive matching for its values,
  and the values should not contain whitespace
    * Usernames are case insensitive in the Splunk software
* In Active Directory, this is 'sAMAccountName'
* Required.
* A typical value is 'uid'.
* No default.

realNameAttribute = <string>
* The user's real, human readable name.
* Required.
* A typical value is 'cn'.
* No default.

emailAttribute = <string>
* The user's email address.
* This setting is optional.
* Default: 'mail'

groupMappingAttribute  = <string>
* The value that group entries use to declare membership.
* Groups are often mapped with user DN, so this defaults to 'dn'
* Set this if groups are mapped using a different setting
  * Usually only needed for OpenLDAP servers.
  * A typical setting is 'uid'
    * For example, assume a group declares that one of its members is
      'splunkuser' — every user with the 'uid' value 'splunkuser' is
      mapped to that group.
* This setting is optional.
* No default.

groupBaseDN = [<string>;<string>;...]
* The LDAP Distinguished Names of LDAP entries whose subtrees contain 
  the groups.
* Required.
* Enter a semicolon (;) delimited list to search multiple trees.
* If your LDAP environment does not have group entries, there is a
  configuration that can treat each user as its own group:
  * Set groupBaseDN to the same as userBaseDN, which means you search
    for groups in the same place as users.
  * Next, set the groupMemberAttribute and groupMappingAttribute to the same
    setting as userNameAttribute.
    * This means the entry, when treated as a group, uses the username
      value as its only member.
  * For clarity, also set groupNameAttribute to the same
    value as userNameAttribute.
* No default.

groupBaseFilter = <string>
* The LDAP search filter Splunk software uses when searching for static groups
* Like 'userBaseFilter', this is highly recommended to speed up LDAP queries
* See Request for Comments (RFC) 2254 on the Internet Engineering Task Force
  (IETF) website for more information.
* This setting is optional.
* Default: empty string (no filtering).

dynamicGroupFilter = <string>
* The LDAP search filter Splunk software uses when searching for dynamic groups.
* Configure this setting only if you intend to retrieve dynamic groups
  on your LDAP server.
* Example: '(objectclass=groupOfURLs)'
* This setting is optional.
* Default: empty string

dynamicMemberAttribute = <string>
* This setting contains the LDAP URL needed to retrieve members dynamically.
* Only configure this if you intend to retrieve dynamic groups on your
  LDAP server
* This setting is required if you want to retrieve dynamic groups.
* Otherwise, it is optional.
* Example: 'memberURL'

groupNameAttribute = <string>
* This is the group entry setting whose value stores the group name.
* A typical setting for this is 'cn' (common name)
* Recall that if you are configuring LDAP to treat user entries as their own
  group, user entries must have this setting
* Required.
* Default: empty string

groupMemberAttribute = <string>
* This is the group entry setting whose values are the groups members
* Typical setting for this are 'member' and 'memberUid'
* For example, consider the groupMappingAttribute example above using
  groupMemberAttribute 'member'
  * To declare 'splunkuser' as a group member, its setting 'member' must
    have the value 'splunkuser'
* Required.
* Default: empty string

nestedGroups = <boolean>
* Controls whether Splunk software expands nested groups using the
  'memberof' extension.
* Set to 1 if you have nested groups you want to expand and the 'memberof'
  extension on your LDAP server.
* This setting is optional.

charset = <string>
* Only set this for an LDAP setup that returns non-UTF-8 encoded data. LDAP
  is supposed to always return UTF-8 encoded data (See RFC 2251), but some
  tools incorrectly return other encodings.
* Follows the same format as 'CHARSET' in props.conf (see props.conf.spec)
* An example value would be "latin-1"
* This setting is optional.
* Default: empty string

anonymous_referrals = [0|1]
* Set this to 0 to turn off referral chasing
* Set this to 1 to turn on anonymous referral chasing
* NOTE: Splunk software only chases referrals using anonymous bind.
        It does not support rebinding using credentials.
* If you do not need referral support, set this to 0.
* If you wish to make referrals work, set this to 1 and conirm your server
  allows anonymous searching
* This setting is optional.
* Default: 1

sizelimit = <integer>
* Limits the amount of entries that Splunk software requests in LDAP search.
* NOTE: The max entries returned is still subject to the maximum
        imposed by your LDAP server
  * Example: If you set this to 5000 and the server limits it to 1000,
             the software only returns 1000 entries.
* This setting is optional.
* Default: 1000

pagelimit = <integer>
* OPTIONAL
* The maximum number of entries to return in each page.
* Enables result sets that exceed the maximum number of entries defined for the
  LDAP server.
* If set to -1, ldap pagination is off.
* IMPORTANT: The maximum number of entries a page returns is subject to
  the maximum page size limit of the LDAP server. For example: If you set 'pagelimit =
  5000' and the server limit is 1000, you cannot receive more than 1000 entries in
  a page.
* Default: -1

enableRangeRetrieval = <boolean>
* OPTIONAL
* The maximum number of values that can be retrieved from one attribute in a
  single LDAP search request is determined by the LDAP server. If the number of
  users in a group exceeds the LDAP server limit, enabling this setting fetches all
  users by using the "range retrieval" mechanism.
* Enables result sets for a given attribute that exceed the maximum number of
  values defined for the LDAP server.
* If set to false, ldap range retrieval is off.
* Default: false

timelimit = <integer>
* Limits the amount of time, in seconds, that Splunk software waits for an LDAP search
  request to complete.
* If your searches finish quickly, lower this value from the default.
* Maximum value is 30 seconds
* Default: 15

network_timeout = <integer>
* Limits the amount of time a socket polls a connection without activity
* This is useful for determining if your LDAP server cannot be reached
* NOTE: As a connection could be waiting for search results, this value
        must be higher than 'timelimit'.
* Like 'timelimit', if you have a fast connection to your LDAP server,
  lower this value.
* This setting is optional.
* Default: 20

ldap_negative_cache_timeout = <nonnegative decimal>
* The amount of time, in seconds, that Splunk software remembers that a non-existent
  user on an LDAP provider does not exist.
* This setting is useful when you want to avoid frequent LDAP queries for users
  that do not exist on the LDAP provider.
* This setting does not prevent LDAP queries on login. Login always queries the LDAP
  provider to confirm that a user exists.
* Default: 86400

#####################
# Map roles
#####################

[roleMap_<authSettings-key>]
* The mapping of Splunk roles to LDAP groups for the LDAP strategy specified
  by <authSettings-key>
* Follow this stanza name with several Role-to-Group(s) mappings as defined
  below.
* NOTE: This role mapping ONLY applies to the specified strategy.
* Importing groups for the same user from different strategies is not 
  supported.

<Splunk RoleName> = <LDAP group string>
* Maps a Splunk role (from authorize.conf) to LDAP groups
* This LDAP group list is semicolon delimited (no spaces).
* List several of these setting/value pairs to map several Splunk roles to
  LDAP Groups

#####################
# Scripted authentication
#####################

[<authSettings-key>]
* Follow this stanza name with the following setting/value pairs:

scriptPath = <string>
* The full path to the script, including the path to the program
  that runs it (python)
* Required.
* For example: "$SPLUNK_HOME/bin/python" "$SPLUNK_HOME/etc/system/bin/$MY_SCRIPT"
* NOTE: If a path contains spaces, it must be quoted. The example above
  handles the case where SPLUNK_HOME contains a space.
* No default.

scriptSearchFilters = [1|0]
* Whether or not to call the script to add search filters.
* Set this to 1 to call the script to add search filters.
* Default: 0

[cacheTiming]
* Use these settings to adjust how long Splunk software uses the answers returned
  from script functions before calling them again.
* All timeouts can be expressed in seconds or as a search-like time range
* Examples include "30" (30 seconds), "2mins" (2 minutes), "24h" (24 hours), etc.
* You can opt to use no caching for a particular function by setting the
  value to "0".
  * Be aware that this can severely hinder performance as a result of heavy
    script invocation.
* Choosing the correct values for cache timing involves a tradeoff between
  new information latency and general performance.
  * High values yield better performance from calling the script less, but
    introduces a latency in picking up changes.
  * Low values pick up changes in your external auth system more
    quickly, but can slow down performance due to increased script
    invocations.

userLoginTTL = <time range string>
* The timeout for the 'userLogin' script function.
* These return values are cached on a per-user basis.
* Default: 0 (no caching)

getUserInfoTTL = <time range string>
* The timeout for the getUserInfo script function.
* These return values are cached on a per-user basis.
* Default: 10s

getUsersTTL = <time range string>
* The timeout for the getUsers script function.
* There is only one global getUsers cache (it is not tied to a
  specific user).
* Default: 10s

#####################
# Settings for Splunk Authentication mode
#####################

[splunk_auth]
* Settings for Splunk's internal authentication system.

minPasswordLength = <positive integer>
* Specifies the minimum permitted password length in characters when
  passwords are set or modified. 
* This setting is optional.
* Password modification attempts which do not meet this requirement are
* explicitly rejected.
* Values less than 1 are ignored.
* Default: 8

minPasswordUppercase = <positive integer>
* Specifies the minimum permitted uppercase characters when passwords are set or modified.
* Splunk software ignores negative values.
* This setting is optional.
* Password modification attempts which do not meet this requirement are
* explicitly rejected.
* Default: 0

minPasswordLowercase = <positive integer>
* Specifies the minimum permitted lowercase characters when passwords are set or modified.
* Splunk software ignores negative values.
* This setting is optional.
* Password modification attempts which do not meet this requirement are
* explicitly rejected.
* Default: 0

minPasswordDigit = <positive integer>
* Specifies the minimum permitted digit or number characters when passwords are set or modified.
* Splunk software ignores negative values.
* This setting is optional.
* Password modification attempts which do not meet this requirement are
* explicitly rejected.
* Default: 0

minPasswordSpecial = <positive integer>
* Specifies the minimum permitted special characters when passwords are set or modified.
* The semicolon character is not allowed.
* Splunk software ignores negative values.
* This setting is optional.
* Password modification attempts which do not meet this requirement are
* explicitly rejected.
* Default: 0

expirePasswordDays = <positive integer>
* Specifies the number of days before the password expires after a reset.
* Minimum value: 0
* Maximum value: 3650
* Splunk software ignores negative values.
* This setting is optional.
* Default: 90

expireAlertDays = <positive integer>
* Specifies the number of days to issue alerts before password expires.
* Minimum value: 0
* Maximum value: 120
* Splunk software ignores negative values.
* This setting is optional.
* Alerts appear in splunkd.log.
* Default: 15

expireUserAccounts = <boolean>
* Specifies whether password expiration is enabled.
* This setting is optional.
* Default: false (user passwords do not expire).

forceWeakPasswordChange = <boolean>
* Specifies whether users must change a weak password.
* This setting is optional.
* Default: false (users can keep weak password).

lockoutUsers = <boolean>
* Specifies whether locking out users is enabled.
* This setting is optional.
* If you enable this setting on members of a search head cluster, user lockout 
  state applies only per SHC member, not to the entire cluster.
* Default: true (users are locked out on incorrect logins).

lockoutMins = <positive integer>
* The number of minutes that a user is locked out after entering an incorrect 
  password more than 'lockoutAttempts' times in 'lockoutThresholdMins' minutes.
* Any value less than 1 is ignored.
* Minimum value: 1
* Maximum value: 1440
* This setting is optional.
* If you enable this setting on members of a search head cluster, user lockout 
  state applies only per SHC member, not to the entire cluster.
* Default: 30

lockoutAttempts = <positive integer>
* The number of unsuccessful login attempts that can occur before a user is locked out.
* The unsuccessful login attempts must occur within 'lockoutThresholdMins' minutes.
* Any value less than 1 is ignored.
* Minimum value: 1
* Maximum value: 64
* This setting is optional.
* If you enable this setting on members of a search head cluster, user lockout 
  state applies only per SHC member, not to the entire cluster.
* Default: 5

lockoutThresholdMins = <positive integer>
* Specifies the number of minutes that must pass from the time of the first failed 
  login before the failed login attempt counter resets.
* Any value less than 1 is ignored.
* Minimum value: 1
* Maximum value: 120
* This setting is optional.
* If you enable this setting on members of a search head cluster, user lockout 
  state applies only per SHC member, not to the entire cluster.
* Default: 5

enablePasswordHistory = <boolean>
* Specifies whether password history is enabled.
* When set to "true", Splunk software maintains a history of passwords
  that have been used previously.
* This setting is optional.
* Default: false

passwordHistoryCount = <positive integer>
* The number of passwords that are stored in history. If password
  history is enabled, on password change, user is not allowed to pick an
  old password.
* This setting is optional.
* Minimum value: 1
* Maximum value: 128
* Default: 24

constantLoginTime = <decimal>
* The amount of time, in seconds, that the authentication manager
* waits before returning any kind of response to a login request.
* When you set this setting, login is guaranteed to take the
* amount of time you specify. If necessary, the authentication manager
* adds a delay to the actual response time to keep this guarantee.
* This setting is optional.
* Minimum value: 0 (Disables login time guarantee)
* Maximum value: 5.0
* Default: 0

verboseLoginFailMsg = <boolean>
* Specifies whether or not the login failure message explains
  the failure reason.
* When set to true, Splunk software displays a message on login
  along with the failure reason.
* When set to false, Splunk software displays a generic failure
  message without a specific failure reason.
* This setting is optional.
* Default: true

#####################
# Security Assertion Markup Language (SAML) settings
#####################

[<saml-authSettings-key>]
* Follow this stanza name with the following setting/value pairs.
* The <authSettings-key> must be one of the values listed in the
* authSettings setting, specified above in the [authentication] stanza.

fqdn = <string>
* The fully qualified domain name where this splunk instance is running.
* If this value is not specified, Splunk software uses the value specified
  in server.conf.
* If this value is specified and 'http://' or 'https://' prefix is not
  present, Splunk software uses the SSL setting for splunkweb.
* This setting is optional.
* Splunk software uses this information to populate the 'assertionConsumerServiceUrl'.
* Default: empty string

redirectPort = <port number>
* The port where SAML responses are sent. 
* Typically, this is the web port.
* If internal port redirection is needed, set this port and the
  'assertionconsumerServiceUrl' in the AuthNRequest contains this port
  instead of the Splunk Web port.
* To prevent any port information to be appended in the
  'assertionConsumerServiceUrl' setting, set this to 0.
* No default.

idpSSOUrl = <url>
* The protocol endpoint on the IDP (Identity Provider) where the
  AuthNRequests should be sent.
* Required.
* SAML requests fail if this information is missing.
* No default.

idpAttributeQueryUrl = <url>
* The protocol endpoint on the IDP (Identity Provider) where the setting
  query requests should be sent.
* Attribute queries can be used to get the latest 'role' information,
  if there is support for Attribute queries on the IDP.
* This setting is optional.
* When this setting is absent, Splunk software caches the role information 
  from the SAML assertion and use it to run saved searches.
* No default.

idpCertPath = <Pathname>
* This value is relative to $SPLUNK_HOME/etc/auth/idpCerts.
* The value for this setting can be the name of the certificate file or a directory.
* If it is empty, Splunk software automatically verify with certificates in all subdirectories
  present in $SPLUNK_HOME/etc/auth/idpCerts.
* If the SAML response is to be verified with a IdP (Identity Provider) certificate that
  is self signed, then this setting holds the filename of the certificate.
* If the SAML response is to be verified with a certificate that is a part of a
  certificate chain(root, intermediate(s), leaf), create a subdirectory and place the
  certificate chain as files in the subdirectory.
* If there are multiple end certificates, create a subdirectory such that, one subdirectory
  holds one certificate chain.
* If multiple such certificate chains are present, the assertion is considered verified,
  if validation succeeds with any certifcate chain.
* The file names within a certificate chain should be such that root certificate is alphabetically
  before the intermediate which is alphabetically before of the end cert.
  ex. cert_1.pem has the root, cert_2.pem has the first intermediate cert, cert_3.pem has the second
      intermediate certificate and cert_4.pem has the end certificate.
* This setting is required if 'signedAssertion' is set to true.
* Otherwise, it is optional.
* No default.

idpSLOUrl = <url>
* The protocol endpoint on the IDP (Identity Provider) where a SP
  (Service Provider) initiated Single logout request should be sent.
* This setting is optional.
* No default.

errorUrl = <url>
* The URL to be displayed for a SAML error. 
* Errors may be due to erroneous or incomplete configuration in either
  the IDP or Splunk software.
* This URL can be absolute or relative. 
  * Absolute URLs should follow the pattern 
    <protocol>:[//]<host> e.g. https://www.external-site.com.
  * Relative URLs should start with '/'. A relative url shows up as an 
    internal link of the Splunk instance, for example: https://splunkhost:port/relativeUrlWithSlash
* No default.

errorUrlLabel = <string>
* Label or title of the content pointed to by errorUrl.
* This setting is optional.
* No default.

entityId = <string>
* The entity ID for SP connection as configured on the IDP.
* Required.
* No default.

issuerId = <string>
* Required.
* The unique identifier of the identity provider.
  The value of this setting corresponds to the setting "entityID" of
  "EntityDescriptor" node in IdP metadata document.
* If you configure SAML using IdP metadata, this field is extracted from
  the metadata.
* If you configure SAML manually, then you must configure this setting.
* When Splunk software tries to verify the SAML response, the issuerId
  specified here must match the 'Issuer' field in the SAML response. Otherwise,
  validation of the SAML response fails.

signAuthnRequest = <boolean>
* Whether or not Splunk software should sign AuthNRequests.
* This setting is optional.
* Default: true

signedAssertion = <boolean>
* Whether or not thee SAML assertion has been signed by the IDP.
* If set to false, Splunk software does not verify the signature 
  of the assertion using the certificate of the IDP.
* Currently, the software accepts only signed assertions.
* This setting is optional.
* Default: true

attributeQuerySoapPassword = <password>
* The password to be used when making an attribute query request.
* Attribute query requests are made using SOAP using basic authentication
* This setting is required if 'attributeQueryUrl' is specified.
* Otherwise, it is optional.
* This string is obfuscated upon splunkd startup.
* No default.

attributeQuerySoapUsername = <string>
* The username to be used when making an attribute query request.
* Attribute Query requests are made using SOAP using basic authentication
* This setting is required if 'attributeQueryUrl' is specified.
* Otherwise, it is optional.
* No default.

attributeQueryRequestSigned = <boolean>
* Whether or not to sign attribute query requests.
* Default: true

attributeQueryResponseSigned = <boolean>
* Specifies whether attribute query responses are signed.
* If set to false, Splunk software does not verify the signature in
  the response using the certificate of the IDP.
* This setting is optional.
* Default: true

redirectAfterLogoutToUrl = <url>
* The user is redirected to this url after logging out of Splunk.
* If this is not specified and 'idpSLO' is also not set, the user is
  redirected to splunk.com after logout.
* This setting is optional.
* No default.

defaultRoleIfMissing = <splunk role>
* If the IDP does not return any AD groups or splunk roles as a part of the
  assertion, Splun software uses this value if provided.
* This setting is optional.
* No default.

skipAttributeQueryRequestForUsers = <comma separated list of users>
* To skip attribute query requests being sent to the IDP for certain users,
  add them with this setting.
* By default, attribute query requests are skipped for local users.
* For non-local users, use this in conjunction with 'defaultRoleIfMissing'.
* This setting is optional.
* No default.

maxAttributeQueryThreads = <integer>
* Number of threads to use to make attribute query requests.
* Changes to this setting require a restart to take effect.
* This setting is optional.
* Maximum value: 10
* Default: 2

maxAttributeQueryQueueSize = <integer>
* The number of attribute query requests to queue, set to 0 for infinite
  size.
* Changes to this setting require a restart to take effect.
* This setting is optional.
* Default: 50

attributeQueryTTL = <integer>
* Determines the time for which Splunk software caches the user and role
  information (time to live).
* Once the ttl expires, Splunk software makes an attribute query request to
  retrieve the role information.
* This setting is optional.
* Defaul: 3600

allowSslCompression = <boolean>
* If set to true, the server allows clients to negotiate SSL-layer 
  data compression.
* This setting is optional.
* Default: the value of 'allowSslCompression' in server.conf

cipherSuite = <cipher suite string>
* If set, Splunk software uses the specified cipher string for the HTTP server.
* Attribute query requests might fail if the IDP requires a relaxed
  ciphersuite.
* Use "openssl s_client -cipher 'TLSv1+HIGH:@STRENGTH' -host <IDP host> -port 443" 
  to determine if Splunk software can connect to the IDP.
* This setting is optional.
* Default: the value or 'cipherSuite' in server.conf

sslVersions = <versions_list>
* Comma-separated list of SSL versions to support.
* The versions available are "ssl3", "tls1.0", "tls1.1", and "tls1.2"
* Default: the value of 'sslVersions' in server.conf.

sslCommonNameToCheck = <commonName>
* If this value is set, and 'sslVerifyServerCert' is set to true,
  splunkd limits most outbound HTTPS connections to hosts which use
  a cert with this common name.
* This setting is optional.
* Default: the value of 'cipherSuite' in server.conf

sslAltNameToCheck = <alternateName1>, <alternateName2>, ...
* If this value is set, and 'sslVerifyServerCert' is set to true,
  splunkd is also willing to verify certificates which have a so-called
  "Subject Alternate Name" that matches any of the alternate names in this
  list.
* This setting is optional.
* Default: the value of 'sslAltNametoCheck' in server.conf

ecdhCurveName = <string>
* DEPRECATED; use 'ecdhCurves' instead.
* Elliptic Curve-Diffie Hellman (ECDH) curve to use for ECDH key negotiation.
* If not set, Splunk uses the setting specified in server.conf.

ecdhCurves = <comma separated list>
* ECDH curves to use for ECDH key negotiation.
* The curves should be specified in the order of preference.
* The client sends these curves as a part of Client Hello.
* The server supports only the curves specified in the list.
* Splunk software only supports named curves that have been
  specified by their SHORT names.
* The list of valid named curves by their short/long names can be obtained
  by executing this CLI command:
  $SPLUNK_HOME/bin/splunk cmd openssl ecparam -list_curves
* Example setting: ecdhCurves = prime256v1,secp384r1,secp521r1
* Default: The value of ecdhCurves' setting in server.conf

clientCert = <path>
* Full path to the client certificate Privacy-Enhanced Mail (PEM) format file.
* Certificates are auto-generated upon first starting Splunk software.
* You may replace the auto-generated certificate with your own.
* If not set, Splunk uses the setting specified in
  server.conf/[sslConfig]/'serverCert'.
* Default: $SPLUNK_HOME/etc/auth/server.pem.

sslKeysfile = <filename>
* DEPRECATED; use 'clientCert' instead.
* Location of the PEM file in the directory specified by 'caPath'.
* Default: server.pem.

sslPassword = <password>
* The server certificate password.
* If not set, Splunk software uses the setting specified in server.conf.
* This setting is optional.
* Default: password.

sslKeysfilePassword = <password>
* DEPRECATED; use 'sslPassword' instead.

caCertFile = <filename>
* The public key of the signing authority.
* If not set, Splunk software uses the setting specified in server.conf.
* This setting is optional.
* Default: cacert.pem

caPath = <path>
* DEPRECATED; use absolute paths for all certificate files.
* If certificate files given by other settings in this stanza are not absolute
  paths, then they are relative to this path.
* Default: $SPLUNK_HOME/etc/auth

sslVerifyServerCert = <boolean>
* Used by distributed search: when making a search request to another
  server in the search cluster.
* If not set, Splunk software uses the setting specified in server.conf.
* This setting is optional.
* No default.

blacklistedAutoMappedRoles = <comma separated list of roles>
* Comma separated list of splunk roles that should be blacklisted
  from being auto-mapped by splunk from the IDP Response.
* This setting is optional.
* No default.

blacklistedUsers = <comma separated list of user names>
* Comma separated list of user names from the IDP response to be
  blacklisted by splunk platform.
* This setting is optional.
* No default.

nameIdFormat = <string>
* If supported by IDP, while making SAML Authentication request this value can
  be used to specify the format of the Subject returned in SAML Assertion.
* This setting is optional.
* No default.

ssoBinding = <string>
* The binding that is used when making a SP-initiated SAML request.
* Acceptable options are "HTTPPost" and "HTTPRedirect".
* This binding must match the one configured on the IDP.
* This setting is optional.
* Default: HTTPPost

sloBinding = <string>
* The binding that is used when making a logout request or sending a logout
  response to complete the logout workflow.
* Acceptable options are "HTTPPost" and "HTTPRedirect".
* This binding must match the one configured on the IDP.
* This setting is optional.
* Default: HTTPPost

signatureAlgorithm = RSA-SHA1 | RSA-SHA256
* The signature algorithm that is used for outbound SAML messages,
  for example, SP-initiated SAML request.
* This setting is only used when 'signAuthnRequest' is set to "true".
* This setting is applicable for both HTTP POST and HTTP Redirect binding.
* RSA-SHA1 corresponds to 'http://www.w3.org/2000/09/xmldsig#rsa-sha1'.
* RSA-SHA256 corresponds to 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'.
* This algorithm is sent as a part of 'sigAlg'.
* For improved security, set to "RSA-SHA256".
* This setting is optional.
* Default: RSA-SHA1

inboundSignatureAlgorithm = RSA-SHA1;RSA-SHA256
* Allows only SAML responses that are signed using any one of the specified
  algorithms.
* This setting is applicable for both HTTP POST and HTTP Redirect binding.
* Provide a semicolon-separated list of signature algorithms for the SAML responses
  that you want Splunk Web to accept. Splunk software rejects any SAML responses
  that are not signed by the specified algorithms.
* For improved security, set it to "RSA-SHA256".
* This setting is optional.
* Default: RSA-SHA1;RSA-SHA256

replicateCertificates = <boolean>
* If set to "true", IdP certificate files are replicated across search head cluster setup.
* If disabled, IdP certificate files need to be replicated manually across SHC, 
  otherwise verification of SAML-signed assertions fails.
* This setting has no effect if search head clustering is disabled.
* This setting is optional.
* Default: true

#####################
# Map roles
#####################

[roleMap_<saml-authSettings-key>]
* The mapping of Splunk roles to SAML groups for the SAML stanza specified
  by '<authSettings-key>'.
* If a SAML group is not explicitly mapped to a Splunk role, but has
  the same name as a valid Splunk role then for ease of configuration, 
  it is auto-mapped to that Splunk role.
* Follow this stanza name with several Role-to-Group(s) mappings as defined
  below.

<Splunk RoleName> = <SAML group string>
* Maps a Splunk role (from authorize.conf) to SAML groups
* This SAML group list is semicolon delimited (no spaces).
* List several of these setting/value pairs to map several Splunk roles to
  SAML Groups.
* If the role mapping is not specified, Splunk expects Splunk roles in the
  assertion and attribute query response returned from the IDP.

#####################
# SAML User Roles Map
#####################

[userToRoleMap_<saml-authSettings-key>]
* The mapping of SAML user to Splunk roles, real names, and emails,
  for the SAML stanza specified by '<authSettings-key>'.
* Follow this stanza name with several User-to-Role::Realname::Email mappings
  as defined below.
* The stanza is used only when the IDP does not support Attribute Query Request

<SAML User> = <Splunk Roles string>::<Realname>::<Email>
* Maps a SAML user to a Splunk role(from authorize.conf), real name, and email
* The Splunk Roles string is semicolon delimited (no spaces).
* The Splunk Roles string, Realname and Email are :: delimited (no spaces).

#####################
# Authentication Response Attribute Map
#####################

[authenticationResponseAttrMap_SAML]
* Splunk software expects emails, real names, and roles to be returned as SAML
  attributes in SAML assertion. This stanza can be used to map attribute names
  to what is expected. These are optional settings, and are only needed for
  certain IDPs.

role = <string>
* Attribute name to be used as role in SAML Assertion.
* This setting is optional.
* Default: "role"

realName = <string>
* Attribute name to be used as realName in SAML Assertion.
* This setting is optional.
* Default: "realName"

mail = <string>
* Attribute name to be used as email in SAML Assertion.
* This setting is optional.
* Default: "mail"

#####################
# Settings for Proxy SSO mode
#####################

[roleMap_proxySSO]
* The mapping of Splunk roles to groups passed in headers from the proxy server.
* If a group is not explicitly mapped to a Splunk role, but has
  the same name as a valid Splunk role, then, for ease of configuration, it is
  auto-mapped to that Splunk role.
* Follow this stanza name with several Role-to-Group(s) mappings as defined
  later in this section.

<Splunk RoleName> = <Group string>
* Maps a Splunk role (from authorize.conf) to one or more groups.
* This group list is semicolon delimited (no spaces).
* List several of these setting value pairs to map several Splunk roles to
  groups.
* If role mapping is not specified, the user is logged in with the 
  default User role.
* No default.

[userToRoleMap_proxySSO]
* The mapping of ProxySSO user to Splunk roles
* Follow this stanza name with several User-to-Role(s) mappings as defined
  later in this section.

<ProxySSO User> = <Splunk Roles string>
* Maps a ProxySSO user to Splunk role (from authorize.conf).
* This Splunk Role list is semicolon delimited (no spaces).
* No default.

[proxysso-authsettings-key]
* Follow this stanza name with the attribute/value pairs listed below.

defaultRoleIfMissing = <splunk role>
* If Splunk roles cannot be determined based on role mapping, Splunk software
  uses the default configured splunk role.
* This setting is optional.

blacklistedAutoMappedRoles = <comma separated list of roles>
* Comma-separated list of splunk roles that should be blacklisted
  from being auto-mapped by splunk from the proxy server headers.
* This setting is optional.

blacklistedUsers = <comma separated list of user names>
* Comma-separated list of user names from the proxy server headers to be
  blacklisted by splunk platform.
* This setting is optional.

#####################
# Secret Storage
#####################

[secrets]

disabled = <boolean>
* Toggles integration with platform-provided secret storage facilities.
* NOTE: Splunk plans to submit Splunk Enterprise for Common Criteria
  evaluation. Splunk does not support using the product in Common
  Criteria mode until it has been certified by NIAP. See the "Securing
  Splunk Enterprise" manual for information on the status of Common
  Criteria certification.
* Default (if Common Criteria mode is enabled): false
* Default (if Common Criteria mode is disabled): true


filename = <filename>
* Designates a Python script that integrates with platform-provided
  secret storage facilities, like the GNOME keyring software for the
  GNOME desktop manager.
* Set <filename> to the name of a Python script located in one of the
  following directories:
    $SPLUNK_HOME/etc/apps/*/bin
    $SPLUNK_HOME/etc/system/bin
    $SPLUNK_HOME/etc/searchscripts
* Set <filename> to a basename. Do not user a name with path separators.
* Ensure <filename> ends with a .py file extension.
* No default.

namespace = <string>
* Use an instance-specific string as a namespace within secret storage.
* When using GNOME keyring, this namespace is used as a keyring name.
* If multiple Splunk instances must store separate sets of secrets within the
  same storage backend, customize this value to be unique for each
  Splunk instance.
* Default: "splunk"

#####################
# Duo Multi-Factor Authentication (MFA) vendor settings
#####################
[<duo-externalTwoFactorAuthSettings-key>]
* <duo-externalTwoFactorAuthSettings-key> must be the value listed in the
  'externalTwoFactorAuthSettings' setting, specified in the [authentication]
  stanza.
* This stanza contains Duo specific multifactor authentication settings and is
  activated only when you set 'externalTwoFactorAuthVendor' to "Duo".
* All the following settings, except 'appSecretKey', are provided by Duo.

apiHostname = <string>
* Duo's API endpoint which performs the actual multifactor authentication.
* Example: apiHostname = api-xyz.duosecurity.com
* Required.
* No default.

integrationKey = <string>
* Duo's integration key for Splunk software.
* Must be of size = 20.
* Integration key is obfuscated before being saved here for security.
* Required.
* No default.

secretKey = <string>
* Duo's secret key for Splunk software. 
* Must be of size = 40.
* Secret key is obfuscated before being saved here for security.
* Required.
* No default.

appSecretKey = <string>
* Splunk application specific secret key which should be random and locally generated.
* Must be at least of size = 40 or longer.
* This secret key is not shared with Duo.
* Application secret key is obfuscated before being saved here for security.
* Required.
* No default.

failOpen = <boolean>
* If set to "true", Splunk software bypasses Duo multifactor authentication when
  the service is unavailable.
* This setting is optional.
* Default: false

timeout = <integer>
* The connection timeout, in seconds, for the outbound Duo HTTPS connection.
* This setting is optional.
* Default: The default Splunk HTTPS connection timeout

sslVersions = <versions_list>
* Comma-separated list of SSL versions to support for incoming connections.
* The versions available are "ssl3", "tls1.0", "tls1.1", and "tls1.2".
* This setting is optional.
* Default: the value of 'sslVersions in server.conf

cipherSuite = <cipher suite string>
* The cipher string for the HTTP server.
* This setting is optional.
* Default: the value of 'cipherSuite' in server.conf

ecdhCurves = <comma separated list of ec curves>
* ECDH curves to use for ECDH key negotiation.
* This setting is optional.
* Default: the value of 'ecdhCurves' in server.conf

sslVerifyServerCert = <boolean>
* If this is set to true, Splunk software confirms the server that is
  being connected to is a valid one (authenticated). 
* Both the common name and the alternate name of the server are then
  checked for a match, if they are specified in this configuration file. 
* A certificiate is considered verified if either is matched.
* This setting is optional.
* Default: false

sslCommonNameToCheck = <commonName1>, <commonName2>, ...
* If this value is set, Splunk software limits outbound Duo HTTPS connections
  to a host which use a cert with one of the listed common names.
* 'sslVerifyServerCert' must be set to "true" for this setting to work.
* This setting is optional.
* Default: not set

sslAltNameToCheck =  <alternateName1>, <alternateName2>, ...
* If this value is set, the Splunk software limits outbound duo HTTPS connections
  to host which use a cert with one of the listed alternate names.
* sslVerifyServerCert must be set to true for this setting to work.
* This setting is optional.
* Default: not set

sslRootCAPath = <path>
* The full path of a PEM format file containing one or more
  root CA certificates concatenated together.
* This Root CA must match the CA in the certificate chain of the SSL certificate
  returned by the Duo server.
* This setting is optional.
* Default: not set

useClientSSLCompression = <boolean>
* Whether or not compression is enabled between the Splunk instance and a Duo server.
* If set to "true" on client side, compression is enabled between the server and client
  as long as the server also supports it.
* If not set, Splunk software uses the client SSL compression setting provided in server.conf
* This setting is optional.
* Default: false

#####################
# RSA MFA vendor settings
#####################
[<rsa-externalTwoFactorAuthSettings-key>]
* <rsa-externalTwoFactorAuthSettings-key> must be the value listed in the
  externalTwoFactorAuthSettings setting specified in the [authentication]
  stanza.
* This stanza contains RSA-specific multifactor authentication settings and is
  activated only when you set 'externalTwoFactorAuthVendor' to "RSA".
* All the following settings can be obtained from RSA Authentication Manager 8.2 SP1.

authManagerUrl = <string>
* URL of the REST endpoint of RSA Authentication Manager.
* Splunk software sends authentication requests to this URL. 
* Specify a HTTPS-based URL. Splunk software does not support communication over HTTP.
* Required.
* No default.

accessKey = <string>
* Access key needed by Splunk software to communicate with RSA Authentication Manager. 
* Required.
* No default.

clientId = <string>
* The clientId is the agent name created on RSA Authentication Manager.
* Required.
* No default.

failOpen = <boolean>
* Whether or not Splunk software allows login if the RSA MFA server is unavailable.
* If set to "true", allow login in case authentication server is unavailable.
* This setting is optional.
* Default: false.

timeout = <integer>
* The connection timeout, in seconds, for the outbound HTTPS connection to the RSA
  server.
* This setting is optional.
* Default: 5.

messageOnError = <string>
* The message that Splunk softawre shows to the user in the case of a login failure.
* You can specify contact of admin or link to a diagnostic page.
* This setting is optional.
* No default.

sslVersions = <versions_list>
* Comma-separated list of SSL versions to support for incoming connections.
* The versions available are "ssl3", "tls1.0", "tls1.1", and "tls1.2".
* If not set, Splunk software uses the value of 'sslVersions' in server.conf.
* This setting is optional.
* Default: tls1.2

cipherSuite = <cipher suite string>
* If set, Splunk software uses the specified cipher string for the HTTP server.
* If not set, Splunk software uses the value for 'cipherSuite' specified in server.conf
* This setting is optional.

ecdhCurves = <comma separated list of ec curves>
* ECDH curves to use for ECDH key negotiation.
* This setting is optional.
* Default: the value of 'ecdhCurves' in server.conf

sslVerifyServerCert = <boolean>
* Determines whether to verify the server being connected to is authenticated.
* If this is set to true, you should make sure that the server that is
  being connected to is a valid one (authenticated). Both the common
  name and the alternate name of the server are then checked for a
  match if they are specified in this configuration file.  A
  certificiate is considered verified if either is matched.
* This setting is optional.
* Default: true

sslCommonNameToCheck = <commonName1>, <commonName2>, ...
* If this value is set, Splunk software limits outbound RSA HTTPS connections
  to host which use a cert with one of the listed common names.
* 'sslVerifyServerCert' must be set to true for this setting to work.
* This setting is optional.
* Default: not set

sslAltNameToCheck =  <alternateName1>, <alternateName2>, ...
* If this value is set, Splunk software limits outbound RSA HTTPS connections
  to host which use a cert with one of the listed alternate names.
* 'sslVerifyServerCert' must be set to true for this setting to work.
* This setting is optional.
* Default: not set


sslRootCAPath = <path>
* The <path> must refer to full path of a PEM format file containing one or more
  root CA certificates concatenated together.
* Required.
* This Root CA must match the CA in the certificate chain of the SSL certificate
  returned by RSA server.
* Default: not set

sslVersionsForClient = <versions_list>
* Comma-separated list of SSL versions to support for outgoing HTTP connections.
* If not set, Splunk uses the value for 'sslVersionsForClient' in server.conf.
* This setting is optional.
* Default: tls1.2

replicateCertificates = <boolean>
* Whether or not RSA certificate files are automatically replicated across search head
  cluster nodes.
* If set to "true", RSA certificate files are replicated across nodes in a search head 
  cluster.
* If disabled, RSA certificate files need to be replicated manually across SHC or else
  MFA verification fails.
* This setting has no effect if search head clustering is disabled.
* Default: true

enableMfaAuthRest = <boolean>
* Determines whether splunkd requires RSA two-factor authentication against REST endpoints.
* When two-factor authentication is enabled for REST endpoints, either you
  must log in to the Splunk instance with a valid RSA passcode, or requests
  to those endpoints must include a valid token in the following format: 
  "curl -k -u <username>:<password>:<token> -X GET <resource>"
* If set to "true", splunkd requires RSA REST two-factor authentication.
* If set to "false", splunkd does not require REST two-factor authentication.
* Optional.
* Default: false
