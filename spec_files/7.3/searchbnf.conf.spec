#   Version 7.3.0
#
#
# This file contain descriptions of stanzas and attribute/value pairs for
# configuring search-assistant via searchbnf.conf
#
# There is a searchbnf.conf in $SPLUNK_HOME/etc/system/default/.  It should
# not be modified.  If your application has its own custom python search
# commands, your application can include its own searchbnf.conf to describe
# the commands to the search-assistant.
#
# To learn more about configuration files (including precedence) please see
# the documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#  * You can also define global settings outside of any stanza, at the top
#    of the file.
#  * Each conf file should have at most one default stanza. If there are
#    multiple default stanzas, attributes are combined. In the case of
#    multiple definitions of the same attribute, the last definition in the
#    file wins.
#  * If an attribute is defined at both the global level and in a specific
#    stanza, the value in the specific stanza takes precedence.

[<search-commandname>-command]
* This stanza enables properties for a given <search-command>.
* A searchbnf.conf file can contain multiple stanzas for any number of
  commands.  * Follow this stanza name with any number of the following
  attribute/value pairs.
* If you do not set an attribute for a given <spec>, the default is used.
  The default values are empty.
* An example stanza name might be "geocode-command", for a "geocode"
  command.
* Search command stanzas can refer to definitions defined in others stanzas,
  and they do not require "-command", appended to them.  For example:

  [geocode-command]
  syntax = geocode <geocode-option>*
  ...
  [geocode-option]
  syntax = (maxcount=<int>) | (maxhops=<int>)
  ...


#******************************************************************************
# The possible attributes/value pairs for searchbnf.conf
#******************************************************************************


syntax = <string>
* Describes the syntax of the search command.  See the head of
  searchbnf.conf for details.
* Required

simplesyntax = <string>

* Optional simpler version of the syntax to make it easier to
  understand at the expense of completeness.  Typically it removes
  rarely used options or alternate ways of saying the same thing.
* For example, a search command might accept values such as
  "m|min|mins|minute|minutes", but that would unnecessarily
  clutter the syntax description for the user.  In this can, the
  simplesyntax can just pick the one (e.g., "minute").

alias = <commands list>
* Alternative names for the search command.  This further cleans
  up the syntax so the user does not have to know that
  'savedsearch' can also be called by 'macro' or 'savedsplunk'.

description = <string>
* Detailed text description of search command.  Description can continue on
  the next line if the line ends in "\"
* Required

shortdesc = <string>
* A short description of the search command.  The full DESCRIPTION
  may take up too much screen real-estate for the search assistant.
* Required

example<index> = <string>
comment<index> = <string>
* 'example' should list out a helpful example of using the search
  command, and 'comment' should describe that example.
* 'example' and 'comment' can be appended with matching indexes to
  allow multiple examples and corresponding comments.
* For example:
    example2 = geocode maxcount=4
    command2 = run geocode on up to four values
    example3 = geocode maxcount=-1
    comment3 = run geocode on all values

usage = public|private|deprecated
* Determines if a command is public, private, depreciated.  The
  search assistant only operates on public commands.
* Required

tags = <tags list>
* List of tags that describe this search command.  Used to find
  commands when the use enters a synonym (e.g. "graph" -> "chart")

related = <commands list>
* List of related commands to help user when using one command to
  learn about others.


#******************************************************************************
# Optional attributes primarily used internally at Splunk
#******************************************************************************

appears-in = <string>
category = <string>
maintainer = <string>
note = <string>
optout-in = <string>
supports-multivalue = <string>
