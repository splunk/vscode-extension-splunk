#   Version 7.3.0
#
# This file contains possible attribute and value pairs for creating multikv
# rules.  Multikv is the process of extracting events from table-like events,
# such as the output of top, ps, ls, netstat, etc.
#
# There is NO DEFAULT multikv.conf.  To set custom configurations, place a
# multikv.conf in $SPLUNK_HOME/etc/system/local/. For examples, see
# multikv.conf.example.  You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles
#
# NOTE: Only configure multikv.conf if Splunk's default multikv behavior does
# not meet your needs.

# A table-like event includes a table consisting of four sections:
#
#---------------------------------------------------------------------------------------
# Section Name | Description
#---------------------------------------------------------------------------------------
# pre          | optional: info/description (for example: the system summary output in top)
# header       | optional: if not defined, fields are named Column_N
# body         | required: the body of the table from which child events are constructed
# post         | optional: info/description
#---------------------------------------------------------------------------------------

# NOTE: Each section must have a definition and a processing component. See
# below.

[<multikv_config_name>]
* Name of the stanza to use with the multikv search command, for example:
       '| multikv conf=<multikv_config_name> rmorig=f | ....'
* Follow this stanza name with any number of the following attribute/value pairs.

#####################
# Section Definition
#####################
# Define where each section begins and ends.

<Section Name>.start = <regex>
* A line matching this regex denotes the start of this section (inclusive).

OR

<Section Name>.start_offset = <int>
* Line offset from the start of an event or the end of the previous section
  (inclusive).
* Use this if you cannot define a regex for the start of the section.

<Section Name>.member = <regex>
* A line membership test.
* Member if lines match the regex.

<Section Name>.end = <regex>
* A line matching this regex denotes the end of this section (exclusive).

OR

<Section Name>.linecount = <int>
* Specify the number of lines in this section.
* Use this if you cannot specify a regex for the end of the section.

#####################
# Section processing
#####################
# Set processing for each section.

<Section Name>.ignore = [_all_|_none_|_regex_ <regex-list>]
* Determines which member lines will be ignored and not processed further.

<Section Name>.replace = <quoted-str> = <quoted-str>, <quoted-str> = <quoted-str>,...
* List of the form: "toReplace" = "replaceWith".
* Can have any number of quoted string pairs.
* For example: "%" = "_", "#" = "_"

<Section Name>.tokens = [<chopper>|<tokenizer>|<aligner>|<token-list>]
* See below for definitions of each possible token: chopper, tokenizer, aligner,
  token-list.

<chopper> = _chop_, <int-list>
* Transform each string into a list of tokens specified by <int-list>.
* <int-list> is a list of (offset, length) tuples.

<tokenizer> = _tokenize_ <max_tokens (int)> <delims> (<consume-delims>)?
* Tokenize the string using the delim characters.
* This generates at most max_tokens number of tokens.
* Set max_tokens to:
  * -1 for complete tokenization.
  * 0 to inherit from previous section (usually header).
  * A non-zero number for a specific token count.
* If tokenization is limited by the max_tokens, the rest of the string is added
  onto the last token.
* <delims> is a comma-separated list of delimiting chars.
* <consume-delims> - boolean, whether to consume consecutive delimiters. Set to
                     false/0 if you want consecutive delimiters to be treated
                     as empty values. Defaults to true.

<aligner> = _align_, <header_string>, <side>, <max_width>
* Generates tokens by extracting text aligned to the specified header fields.
* header_string: a complete or partial header field value the columns are aligned with.
* side: either L or R (for left or right align, respectively).
* max_width: the maximum width of the extracted field.
  * Set max_width to -1 for automatic width. This expands the field until any
    of the following delimiters are found: " ", "\t"

<token_list> = _token_list_ <comma-separated list>
* Defines a list of static tokens in a section.
* This is useful for tables with no header, for example: the output of 'ls -lah'
  which misses a header altogether.
