"""Exception classes."""

from data_definitions.errors import ErrorResponse, ExternalError, ExternalErrorDatum


class JSONRPCException(Exception):
    """
    Implementation of JSON-RPC 2.0 error exception. Handles formatting error message according to
    JSON-RPC 2.0 specification, and error conversion from pydantic to client-specific format.
    """
    def __init__(self, internal_error_code: str = '', param_name: str = '', code=None, message=None, data=None):
        self._data = list()
        self.code = getattr(self.__class__, "CODE", code)
        self.message_prefix = getattr(self.__class__, "MESSAGE_PREFIX", '')
        self.message = getattr(self.__class__, "MESSAGE", message)
        self.data = data
        self.internal_error_code = internal_error_code
        self.param_name = param_name

        external_error = self.process_errors(self.data)
        self.external_error = ErrorResponse(id=-1, error=external_error)

    def process_errors(self, errors) -> ExternalError:
        return self.convert_custom_error_to_external(errors)

    def convert_custom_error_to_external(self, errors=None) -> ExternalError:
        return ExternalError(code=self.code, data=None, message=self.message)

    @property
    def dict(self):
        return self.external_error.dict()

    @property
    def json(self):
        return self.external_error.json()


class ModelValidationException(JSONRPCException):
    """Invalid params. The JSON sent does not pass validation step and/or cannot
    be used for calculation or visualization."""
    MESSAGE_PREFIX = 'Validation error. '
    CODE = -32602

    _error_collation = {
        'type_error.enum': 'value_out_of_range',
        'type_error.integer': 'value_incorrect',
        'type_error.float': 'value_incorrect',
        'type_error.none.not_allowed': 'value_absent',
        'value_error.missing': 'value_absent',
        'value_error.datetime': 'timestamp_incorrect',
        'value_error.timestamp_out_of_range': 'timestamp_out_of_range',
        'value_error.gender_out_of_range': 'value_out_of_range',
        'value_error.timestamp_incorrect': 'timestamp_incorrect',
        'value_error.number.not_le': 'value_out_of_range',
        'value_error.number.not_ge': 'value_out_of_range'
    }

    def convert_custom_error_to_external(self, errors=None) -> ExternalError:
        for error in errors:
            error['param_name'] = '/'.join(map(str, error.pop('loc')))
            error['message'] = error.pop('msg')
            pydantic_error_type = error.pop('type')
            if pydantic_error_type in self._error_collation:
                error['internal_error_code'] = self._error_collation[pydantic_error_type]
            else:
                error['internal_error_code'] = 'undefined'
            if 'ctx' in error.keys():
                del error['ctx']

        try:
            message = self.message_prefix + '. '.join(map(lambda x: str(x['param_name']) + ': ' + x['message'], errors))
        except Exception as e:
            message = f"{self.message_prefix}Undefined error occurred with '{e}'"

        return ExternalError(code=self.code, data=errors, message=message)


class ModelTypeCheckException(ModelValidationException):
    MESSAGE_PREFIX = 'Type check error. '


class JSONRPCInvalidRequest(JSONRPCException):
    """Invalid Request. The JSON sent is not a valid Request object."""

    CODE = -32600

    def convert_custom_error_to_external(self, errors=None) -> ExternalError:
        datum = ExternalErrorDatum(param_name=self.param_name,
                                   internal_error_code=self.internal_error_code,
                                   message=self.message)

        return ExternalError(code=self.code, data=[datum], message=datum.message)


class JSONRPCMethodNotFound(JSONRPCException):
    """Method not found. The method does not exist / is not available."""

    CODE = -32601
    MESSAGE = "The method does not exist / is not available"


class JSONRPCInternalError(JSONRPCException):
    """Internal error. Internal JSON-RPC error."""

    CODE = -32603
    MESSAGE = "Internal error"
