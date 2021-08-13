# NOTE!
# The shipped default.meta.spec file contains extraneous information beyond the 
# specification which thows off the spec parser.  This file has been included
# to correctly parse default.meta and local.meta files.
#
# For detailed information, refer to https://docs.splunk.com/Documentation/Splunk/latest/Admin/Defaultmetaconf

# GLOBAL SETTINGS
[]
access = read : [ <comma-separated list of roles>], write : [<comma-separated list of roles>]
export = <system|none>

[<object_type>]
access = read : [ <comma-separated list of roles>], write : [<comma-separated list of roles>]
export = <system|none>
owner = <string>
version = <string>
modtime = <float>

[<object_type>/<object_name>]
access = read : [ <comma-separated list of roles>], write : [<comma-separated list of roles>]
export = <system|none>
owner = <string>
version = <string>
modtime = <float>