#   Version 7.3.0
#
# This file contains possible attribute/value pairs for search language macros.

# To learn more about configuration files (including precedence) please see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

[<STANZA_NAME>]
* Each stanza represents a search macro that can be referenced in any search.
* The stanza name is the name of the macro if the macro takes no arguments.
  Otherwise, the stanza name is the macro name appended with "(<numargs>)",
  where <numargs> is the number of arguments that this macro takes.
* Macros can be overloaded. In other words, they can have the same name but a
  different number of arguments. If you have [foobar], [foobar(1)],
  [foobar(2)], etc., they are not the same macro.
* Macros can be used in the search language by enclosing the macro name and any
  argument list within tick marks, for example:`foobar(arg1,arg2)` or `footer`.
* Splunk does not expand macros when they are inside of quoted values, for
  example: "foo`bar`baz".

args = <string>,<string>,...
* A comma-delimited string of argument names.
* Argument names can only contain alphanumeric characters, underscores '_', and
  hyphens '-'.
* If the stanza name indicates that this macro takes no arguments, this
  attribute will be ignored.
* This list cannot contain any repeated elements.

definition = <string>
* The string that the macro will expand to, with the argument substitutions
  made. (The exception is when iseval = true, see below.)
* Arguments to be substituted must be wrapped by dollar signs ($), for example:
  "the last part of this string will be replaced by the value of argument foo $foo$".
* Splunk replaces the $<arg>$ pattern globally in the string, even inside of
  quotes.

validation = <string>
* A validation string that is an 'eval' expression.  This expression must
  evaluate to a boolean or a string.
* Use this to verify that the macro's argument values are acceptable.
* If the validation expression is boolean, validation succeeds when it returns
  true.  If it returns false or is NULL, validation fails, and Splunk returns
  the error message defined by the attribute, errormsg.
* If the validation expression is not boolean, Splunk expects it to return a
  string or NULL.  If it returns NULL, validation is considered a success.
  Otherwise, the string returned is the error string.

errormsg = <string>
* The error message to be displayed if validation is a boolean expression and
  it does not evaluate to true.

iseval = <true/false>
* If true, the definition attribute is expected to be an eval expression that
  returns a string that represents the expansion of this macro.
* Defaults to false.

description = <string>
* OPTIONAL. Simple english description of what the macro does.
