from rest_framework import exceptions, status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

class ErrorCode:
    """Constants for error codes to ensure consistency"""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_ERROR = "permission_denied"
    NOT_FOUND = "not_found"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    UNSUPPORTED_MEDIA = "unsupported_media"
    NOT_ACCEPTABLE = "not_acceptable"
    PARSE_ERROR = "parse_error"
    THROTTLED = "throttled"
    SERVER_ERROR = "server_error"
    GENERIC_ERROR = "error"


def error_response(status_code, error_code, message, details=None):
    """
    Standardized error response format
    """
    response = {
        "success": False,
        "status_code": status_code,
        "error_code": error_code,
        "message": message
    }
    
    if details:
        response["details"] = details
        
    return response


class CustomAPIException(APIException):
    """Base class for custom API exceptions"""
    def __init__(self, message, error_code=ErrorCode.GENERIC_ERROR, status_code=status.HTTP_400_BAD_REQUEST, details=None):
        self.status_code = status_code
        self.error_detail = error_response(
            status_code=self.status_code,
            error_code=error_code,
            message=message,
            details=details
        )
        super().__init__(detail=self.error_detail)


class CustomInternalServerError(CustomAPIException):
    """Custom exception for internal server errors"""
    def __init__(self, message="A server error occurred.", error_code=ErrorCode.SERVER_ERROR, details=None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


def custom_exception_handler(exc, context):
    """
    Custom exception handler for standardizing error responses
    """
    # First, get the standard DRF response
    response = exception_handler(exc, context)
    if not response:
        return response
    
    # Map exception class names to handler functions
    handlers = {
        'ValidationError': _handle_validation_error,
        'Http404': _handle_not_found_error,
        'NotFound': _handle_not_found_error,
        'PermissionDenied': _handle_permission_error,
        'NotAuthenticated': _handle_authentication_error,
        'AuthenticationFailed': _handle_authentication_error,
        'UnsupportedMediaType': _handle_media_type_error,
        'MethodNotAllowed': _handle_method_not_allowed_error,
        'NotAcceptable': _handle_not_acceptable_error,
        'ParseError': _handle_parse_error,
        'Throttled': _handle_throttle_error
    }
    
    # Process the exception with an appropriate handler
    exception_class = exc.__class__.__name__
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    
    # If no specific handler, use a generic one
    return _handle_generic_error(exc, context, response)


def _handle_validation_error(exc, context, response):
    """
    Handle validation errors with detailed field errors and more specific messages
    """
    details = {}
    
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            for field, errors in exc.detail.items():
                if isinstance(errors, list):
                    # Keep all error messages for each field
                    details[field] = errors[0] if len(errors) == 1 else errors
                else:
                    details[field] = str(errors)
                    
            # Create more specific error message based on the fields with errors
            field_names = list(details.keys())
            if len(field_names) == 1:
                message = f"Invalid {field_names[0]} provided."
            else:
                field_list = ", ".join(field_names[:-1]) + f" and {field_names[-1]}" if len(field_names) > 1 else field_names[0]
                message = f"Invalid inputs provided for {field_list} (Already exist)."
        else:
            details = {"non_field_errors": str(exc.detail)}
            message = str(exc.detail)
    else:
        message = "Validation failed. Please check input data."
    
    response.data = error_response(
        status_code=response.status_code,
        error_code=ErrorCode.VALIDATION_ERROR,
        message=message,
        details=details
    )
    return response


def _handle_authentication_error(exc, context, response):
    """Handle authentication-related errors"""
    response.data = error_response(
        status_code=response.status_code,
        error_code=ErrorCode.AUTHENTICATION_ERROR,
        message="Authentication credentials are wrong, try again"
    )
    return response


def _handle_permission_error(exc, context, response):
    """Handle permission denied errors"""
    response.data = error_response(
        status_code=response.status_code,
        error_code=ErrorCode.PERMISSION_ERROR,
        message="You do not have permission to perform this action"
    )
    return response


def _handle_not_found_error(exc, context, response):
    """Handle resource not found errors"""
    response.data = error_response(
        status_code=response.status_code,
        error_code=ErrorCode.NOT_FOUND,
        message="The requested resource was not found"
    )
    return response


def _handle_method_not_allowed_error(exc, context, response):
    """Handle method not allowed errors"""
    response.data = error_response(
        status_code=response.status_code,
        error_code=ErrorCode.METHOD_NOT_ALLOWED,
        message="The HTTP method is not allowed for this endpoint"
    )
    return response


def _handle_media_type_error(exc, context, response):
    """Handle unsupported media type errors"""
    response.data = error_response(
        status_code=response.status_code,
        error_code=ErrorCode.UNSUPPORTED_MEDIA,
        message="Unsupported media type"
    )
    return response


def _handle_not_acceptable_error(exc, context, response):
    """Handle not acceptable errors"""
    response.data = error_response(
        status_code=response.status_code,
        error_code=ErrorCode.NOT_ACCEPTABLE,
        message="Not acceptable content type in request"
    )
    return response


def _handle_parse_error(exc, context, response):
    """Handle parsing errors"""
    response.data = error_response(
        status_code=response.status_code,
        error_code=ErrorCode.PARSE_ERROR,
        message="Malformed request syntax"
    )
    return response


def _handle_throttle_error(exc, context, response):
    """Handle rate limiting/throttling errors"""
    wait_time = getattr(exc, 'wait', None)
    details = {"tryAgainIn": f"{wait_time} seconds"} if wait_time else None
    
    response.data = error_response(
        status_code=response.status_code,
        error_code=ErrorCode.THROTTLED,
        message="Request limit exceeded",
        details=details
    )
    return response


def _handle_generic_error(exc, context, response):
    """Handle all other types of errors"""
    if hasattr(exc, 'detail'):
        message = str(exc.detail)
    else:
        message = str(exc)
    
    error_code = getattr(exc, 'default_code', ErrorCode.GENERIC_ERROR)
    
    response.data = error_response(
        status_code=response.status_code,
        error_code=error_code,
        message=message
    )
    return response