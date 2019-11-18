#   Version 7.3.0
#
# This file contains all possible attributes and value pairs for a
# transactiontypes.conf file.  Use this file to configure transaction searches
# and their properties.
#
# There is a transactiontypes.conf in $SPLUNK_HOME/etc/system/default/.  To set
# custom configurations, place a transactiontypes.conf in
# $SPLUNK_HOME/etc/system/local/. You must restart Splunk to enable
# configurations.
#
# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#   * You can also define global settings outside of any stanza, at the top of
#     the file.
#   * Each conf file should have at most one default stanza. If there are
#     multiple default stanzas, attributes are combined. In the case of
#     multiple definitions of the same attribute, the last definition in the
#     file wins.
#   * If an attribute is defined at both the global level and in a specific
#     stanza, the value in the specific stanza takes precedence.


[<TRANSACTIONTYPE>]
* Create any number of transaction types, each represented by a stanza name and
  any number of the following attribute/value pairs.
* Use the stanza name, [<TRANSACTIONTYPE>], to search for the transaction in
  Splunk Web.
* If you do not specify an entry for each of the following attributes, Splunk
  uses the default value.

maxspan = [<integer> s|m|h|d|-1]
* Set the maximum time span for the transaction.
* Can be in seconds, minutes, hours, or days, or -1 for an unlimited timespan.
  * For example:  5s, 6m, 12h or 30d.
* Defaults to: maxspan=-1

maxpause = [<integer> s|m|h|d|-1]
* Set the maximum pause between the events in a transaction.
* Can be in seconds, minutes, hours, or days, or -1 for an unlimited pause.
  * For example:  5s, 6m, 12h or 30d.
* Defaults to: maxpause=-1

maxevents = <integer>
* The maximum number of events in a transaction. This constraint is disabled if
  the value is a negative integer.
* Defaults to: maxevents=1000

fields = <comma-separated list of fields>
* If set, each event must have the same field(s) to be considered part of the
  same transaction.
  * For example: fields=host,cookie
* Defaults to: ""

connected=[true|false]
* Relevant only if fields (see above) is not empty. Controls whether an event
  that is not inconsistent and not consistent with the fields of a transaction
  opens a new transaction (connected=true) or is added to the transaction.
* An event can be not inconsistent and not field-consistent if it contains
  fields required by the transaction but none of these fields has been
  instantiated in the transaction (by a previous event addition).
* Defaults to: connected=true

startswith=<transam-filter-string>
* A search or eval filtering expression which, if satisfied by an event, marks
  the beginning of a new transaction.
* For example:
  * startswith="login"
  * startswith=(username=foobar)
  * startswith=eval(speed_field < max_speed_field)
  * startswith=eval(speed_field < max_speed_field/12)
* Defaults to: ""

endswith=<transam-filter-string>
* A search or eval filtering expression which, if satisfied by an event, marks
  the end of a transaction.
* For example:
  * endswith="logout"
  * endswith=(username=foobar)
  * endswith=eval(speed_field > max_speed_field)
  * endswith=eval(speed_field > max_speed_field/12)
* Defaults to: ""

* For startswith/endswith <transam-filter-string> has the following syntax:
* syntax:   "<search-expression>" | (<quoted-search-expression>) | eval(<eval-expression>)
* Where:
  * <search-expression>        is a valid search expression that does not contain quotes
  * <quoted-search-expression> is a valid search expression that contains quotes
  * <eval-expression>          is a valid eval expression that evaluates to a boolean. For example,
    startswith=eval(foo<bar*2) will match events where foo is less than 2 x bar.
* Examples:
  * "<search expression>":       startswith="foo bar"
  * <quoted-search-expression>:  startswith=(name="mildred")
  * <quoted-search-expression>:  startswith=("search literal")
  * eval(<eval-expression>):     startswith=eval(distance/time < max_speed)

### memory constraint options ###

maxopentxn=<int>
* Specifies the maximum number of not yet closed transactions to keep in the
  open pool. When this limit is surpassed, Splunk begins evicting transactions
  using LRU (least-recently-used memory cache algorithm) policy.
* The default value of this attribute is read from the transactions stanza in
  limits.conf.

maxopenevents=<int>
* Specifies the maximum number of events (can be) part of open transactions.
  When this limit is surpassed, Splunk begins evicting transactions using LRU
  (least-recently-used memory cache algorithm) policy.
* The default value of this attribute is read from the transactions stanza in
  limits.conf.

keepevicted=<bool>
* Whether to output evicted transactions. Evicted transactions can be
  distinguished from non-evicted transactions by checking the value of the
  'evicted' field, which is set to '1' for evicted transactions.
* Defaults to: keepevicted=false

### multivalue rendering options ###

mvlist=<bool>|<field-list>
* Field controlling whether the multivalued fields of the transaction are (1) a
  list of the original events ordered in arrival order or (2) a set of unique
  field values ordered lexigraphically. If a comma/space delimited list of
  fields is provided only those fields are rendered as lists
* Defaults to: mvlist=f

delim=<string>
* A string used to delimit the original event values in the transaction event
  fields.
* Defaults to: delim=" "

nullstr=<string>
* The string value to use when rendering missing field values as part of mv
  fields in a transaction.
* This option applies only to fields that are rendered as lists.
* Defaults to: nullstr=NULL

### values only used by the searchtxn search command ###

search=<string>
* A search string used to more efficiently seed transactions of this type.
* The value should be as specific as possible, to limit the number of events
  that must be retrieved to find transactions.
* Example: sourcetype="sendmaill_sendmail"
* Defaults to "*" (all events)
