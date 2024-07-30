from django.http import HttpResponse


class HttpResponseUnauthorized(HttpResponse):
    """
    Response to implement the Unauthorized HTTP status code formerly.
    """
    status_code = 401
