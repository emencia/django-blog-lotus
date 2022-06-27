from django.http import HttpResponse


class HttpResponseUnauthorized(HttpResponse):
    """
    Response to implemente the Unauthorized HTTP status code formerly.
    """
    status_code = 401
