import logging
import sys
import uuid
import splunk.admin as admin
import example_eai_handler_schema
import urllib
import re
import errno
import base_eai_handler
import log_helper
import time
from splunk.clilib.bundle_paths import make_splunkhome_path

# Setup the logger
logger = log_helper.setup(logging.INFO, 'ExampleEAIHandler', 'example_eai_handler.log')

class ExampleEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in example_eai_handler_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action. Returns the contents of example_eai_handler.conf

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('List requested.')

        # Fetch from example_eai_handler conf handler
        example_eai_handler_conf_path = self.get_conf_handler_path_name('example_eai_handler', self.userName)
        example_eai_handler_conf_response_payload = self.simple_request_eai(example_eai_handler_conf_path, 'list', 'GET', get_args={'count': -1})

        self.set_conf_info_from_eai_payload(confInfo, example_eai_handler_conf_response_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the 'create' action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Create requested.')

        # Validate and extract correct POST params
        params = self.validate_schema_params()

        # Create stanza in example_eai_handler.conf
        example_eai_handler_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('example_eai_handler'), 'create', 'POST', params)

        # Always populate entry content from request to handler.
        example_eai_handler_rest_path = '/servicesNS/%s/%s/example_eai_handler/%s' % ('nobody', self.appName, urllib.quote_plus(params['name']))
        example_eai_handler_response_payload = self.simple_request_eai(example_eai_handler_rest_path, 'read', 'GET')
        self.set_conf_info_from_eai_payload(confInfo, example_eai_handler_response_payload)

    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Update requested.')

        params = self.validate_schema_params()

        conf_stanza = urllib.quote_plus(params.get('name'))
        del params['name']

        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('example_eai_handler', 'nobody'), conf_stanza)

        # Edit example_eai_handler.conf
        example_eai_handler_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST', params)

        # Always populate entry content from request to handler.
        example_eai_handler_rest_path = '/servicesNS/%s/%s/example_eai_handler/%s' % ('nobody', self.appName, conf_stanza)
        example_eai_handler_response_payload = self.simple_request_eai(example_eai_handler_rest_path, 'read', 'GET')
        self.set_conf_info_from_eai_payload(confInfo, example_eai_handler_response_payload)

    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'delete' action. Removes the requested stanza from example_eai_handler.conf

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Conf stanza deletion requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        # Delete example_eai_handler.conf stanza
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('example_eai_handler'),  conf_stanza)
        example_eai_handler_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')

        # Always populate entry content from request to handler.
        example_eai_handler_rest_path = '/servicesNS/%s/%s/example_eai_handler' % ('nobody', self.appName)
        example_eai_handler_response_payload = self.simple_request_eai(example_eai_handler_rest_path, 'list', 'GET', get_args={'count': -1})
        self.set_conf_info_from_eai_payload(confInfo, example_eai_handler_response_payload)

    def validate_schema_params(self):
        """
        Validates raw request params against the example schema
        """
        schema = example_eai_handler_schema.example_schema
        params = self.get_params(schema=example_eai_handler_schema, filter=example_eai_handler_schema.CONF_FIELDS)
        return self.validate_params(schema, params)

admin.init(ExampleEAIHandler, admin.CONTEXT_NONE)
