from rest_framework import exceptions, status
from rest_framework.exceptions import Throttled, APIException
from rest_framework.views import exception_handler

from util.messages.handle_messages import error_response


class CustomInternalServerError(APIException):
    def __init__(self, success: bool = False, code: str = 'server error', message: str = 'A server error occurred.',
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
        if status_code is None:
            status_code = code

        self.status_code = status_code

        detail = message

        details = error_response(status_code=self.status_code, error_code=code, message=detail)
        super().__init__(detail=details)


def custom_exception_handler(exc, context):
    handlers = {
        'ValidationError': _handle_request_error,
        'Http404': _handle_generic_error,
        'PermissionDenied': _handle_generic_error,
        'NotAuthenticated': _handle_authentication_error,
        'UnsupportedMediaType': _handle_generic_error,
        'NotFound': _handle_generic_error,
        'MethodNotAllowed': _handle_generic_error,
        'NotAcceptable': _handle_generic_error,
        'AuthenticationFailed': _handle_generic_error,
        'ParseError': _handle_generic_error,
        'Throttled': _handle_throttle_error
    }

    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response


def _handle_throttle_error(exc, context, response):
    if isinstance(exc, Throttled):  # check that a Throttled exception is raised
        custom_response_data = {  # prepare custom response data
            'info': 'request limit exceeded',
            'tryAgainIn': '%d seconds' % exc.wait
        }

        response.data = error_response(status_code=response.status_code, error_code=response.data['detail'].code,
                                       message=custom_response_data)

    return response


def _handle_generic_error(exc, context, response):
    response.data = error_response(status_code=response.status_code, error_code=response.data['detail'].code,
                                   message=response.data['detail'])
    return response


def _handle_request_error(exc, context, response):
    error_details = {}
    error_code = "Bad request syntax or unsupported methods"

    # Handle validation errors
    if isinstance(exc, exceptions.ValidationError):
        error_code = "validation error"
        for field, errors in exc.detail.items():
            error_details[field] = errors

    # Customize error response
    response.data = {
        "error": True,
        "errors": [
            {
                "error_code": error_code,
                "details": error_details
            }
        ]
    }
    return response


def _handle_authentication_error(exc, context, response):
    response.data = error_response(status_code=response.status_code, error_code=response.data['detail'].code,
                                   message="Authentications credentials were not provided or have expired")

    return response
