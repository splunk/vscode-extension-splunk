#   Version 7.3.0
#
# This file effects how the search assistant (typeahead) shows the syntax for
# search commands

[<syntax-type>]
* The name of the syntax type you're configuring.
* Follow this field name with one syntax= definition.
* Syntax type can only contain a-z, and -, but cannot begin with -

syntax = <string>
* The syntax for you syntax type.
* Should correspond to a regular expression describing the term.
* Can also be a <field> or other similar value.
