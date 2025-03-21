def success_response(status_code, message_code, message, error=True, ):
    response_data = {
        "success": bool(error),
        "response": [{
            "status_code": int(status_code),
            "code": message_code,
            "details": [
                message
            ]
        }]
    }
    return response_data


def error_response(status_code, error_code, message, error=False):
    error_data = {
        "success": bool(error),
        "errors": [{
            "error_code": error_code,
            "details": {"message": message}
        }]
    }

    return error_data
