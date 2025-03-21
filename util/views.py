"""
Function for displaying error 404 and 500 views
"""

from django.http import JsonResponse
from util.messages.handle_messages import error_response
import random

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' 
    '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 ' 
    '(KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) ',
    'Gecko/20100101 Firefox/89.0'
]

headers = {'User-Agent': random.choice(user_agents)}

def error_404(request, exception):
    message = 'The endpoint not found. Check your spelling or add a trailing slash </> at the end of the endpoint.'
    data = error_response(status_code=404, error_code='Not_Found', message=message)
    response = JsonResponse(data=data, )
    response.status_code = 404
    return response


def error_500(request):
    message = "Server experienced an internal error that needs technical attention"
    data = error_response(status_code=500, error_code='Internal server error', message=message)

    response = JsonResponse(data=data, )
    response.status_code = 500
    return response
