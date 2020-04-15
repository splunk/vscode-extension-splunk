import json
import logging
import splunk.admin as admin
import splunk.rest as rest
import log_helper

# Setup the handler
logger = log_helper.setup(logging.INFO, 'BaseEAIHandler', 'base_handler.log')

class BaseEAIHandler(admin.MConfigHandler):
    def get_param(self, param, default=None):
        """
        Returns value of a matched param from either POST or GET encoded values.
        Note: Returns the first entry as a param - can be multi-valued.

        Arguments
        param -- The param key to extract.
        """
        if param in self.callerArgs:
            if self.callerArgs[param][0] is not None:
                return self.callerArgs[param][0].strip()
        return default

    def get_params(self, schema, filter=None):
        """
        Returns a flattened dictionary of key/value pairs of posted allowable params.
        The EAI Admin Handler plucks name out and sets it the id instance member. This
        adds the name key back to the params dictionary returned.

        Arguments
        filter -- (default None) An optional array of param keys to extract in dictionary
        This is useful to bypass a wholesale dump.
        """
        params = {}
        for param in schema.ALL_FIELDS:
            if param in self.callerArgs and (filter is None or param in filter):
                param_value = self.callerArgs[param][0]
                if param_value is not None:
                    params[param] = param_value.strip()
        if filter is None or 'name' in filter:
            params['name'] = self.callerArgs.id.strip()
        return params

    def validate_params(self, schema, params):
        """
        Returns validated params key/value pair dictionary using predefined schema that casts objects to python types.

        Arguments
        schema -- Schema object (see schema module).
        param_names -- (Optional) Parameters to filter out for validation.
        """
        try:
            params = schema.validate(params)
        except Exception as e:
            logger.error(e)
            error_message = str(e).replace('Missing keys:', 'Missing field(s):')
            raise admin.InternalException(error_message)
        return params

    def simple_request_messages_to_str(self, messages):
        """
        Returns a readable string from a simple request response message

        Arguments
        messages -- The simple request response message to parse
        """
        entries = []
        for message in messages:
            entries.append(message.get('text'))
        return ','.join(entries)

    def set_conf_info_from_eai_payload(self, confInfo, payload):
        """
        Takes the mutable confInfo object and sets the content to that found from
        the list of entry content children.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        payload -- Parsed EAI response from an EAI output_mode=json response.
        """
        entries = payload.get('entry', [])
        for entry in entries:
            entry_name = entry.get('name')
            entry_content = entry.get('content')
            for entry_content_key in entry_content:
                confInfo[entry_name][entry_content_key] = entry_content.get(entry_content_key)
        return confInfo

    def get_conf_handler_path_name(self, conf_file_name, user='nobody', app=None):
        """
        Returns the generic conf file REST handler path from the provided arguments

        Arguments
        conf_file_name -- The conf file to use in the returned the handler path.
        payload (optional) -- The user namespace to use in the returned the handler path. Default is 'nobody'
        """
        if app is None:
            app = self.appName
        return '/servicesNS/%s/%s/configs/conf-%s' % (user, app, conf_file_name)

    def simple_request_eai(self, url, action, method, params=None, get_args=None):
        """
        Returns the payload response from a simpleRequest call

        Arguments
        url -- The REST handler endpoint to use in the simpleRequest
        params -- The parameters sent in the POST body of the simpleRequest
        """
        if not params:
            params = {}

        default_get_args = dict(output_mode='json')
        if get_args:
            default_get_args.update(get_args)

        logger.info('%s request %s' % (method, url))
        try:
            response, content = rest.simpleRequest(url, getargs=default_get_args, postargs=params,
                                                   method=method, sessionKey=self.getSessionKey())
        except Exception as e:
            logger.error(e)
            raise admin.ServiceUnavailableException('Unable to %s %s entry.' % (action, url))
        try:
            payload = json.loads(content)
        except Exception as e:
            logger.error(e)
            raise admin.InternalException('Unable to parse %s response payload.' % url)
        if response.status not in [200, 201]:
            message = self.simple_request_messages_to_str(response.messages)
            logger.error(
                'handler_message="request failed, status code not in successful range" status="%s" params="%s" splunkd_message="%s"' % (
                response.status, params, message))
            raise admin.AlreadyExistsException(
                'Unable to %s %s entry. %s' % (action, url, message))
        return payload
