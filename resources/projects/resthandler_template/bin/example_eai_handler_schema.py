from schema import Schema, And

# The schema validation is provided by the Schema library documented here: https://pypi.org/project/schema/
example_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    'custom_parameter': And(str, len, error='Invalid custom_parameter value'),
})

CONF_FIELDS = ['name', 'custom_parameter']

# Supported POST request arguments -- removes name for Splunk API expectations
ALL_FIELDS = list(set(CONF_FIELDS) - set(['name']))