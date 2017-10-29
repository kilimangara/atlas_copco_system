from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .error_types import INVALID_AUTH

def error_response_content(error_type, status_code, description):
    return {
        'error': {
            'status_code': status_code,
            'type': error_type,
            'description': description,
        }
    }


def SuccessResponse(data=None, status=None, **kwargs):
    if data is None:
        data = {}
    return Response({'data': data}, status, **kwargs)


def ErrorResponse(error_type, status, description=None, **kwargs):
    description = description or error_type
    return Response(error_response_content(error_type, status, description), status, **kwargs)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            response.data = error_response_content(INVALID_AUTH, exc.status_code, exc.detail)
    return response
