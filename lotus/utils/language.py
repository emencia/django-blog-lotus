from django.conf import settings


def get_language_code(request=None):
    """
    A simple helper to get language code.

    The code is retrieved either from a request object (when middleware
    ``LocaleMiddleware`` is enabled) if it exists else fallback to use the code from
    ``settings.LANGUAGE_CODE``.

    Concretely, both i18n url and using HTTP header 'Accept-Language' will properly
    set the current language code by the way of ``LocaleMiddleware``.

    Purpose of this helper is that Lotus querysets require a language code but a single
    language project may not enable middleware ``LocaleMiddleware`` so request object
    won't have attribute ``LANGUAGE_CODE``, then in this situation we have to use
    ``settings.LANGUAGE_CODE``.

    Keyword arguments:
        request (WSGIRequest): A proper request object that should have attribute
            ``LANGUAGE_CODE``. If its value is None, the settings is directly used
            instead. Default argument value is None.

    Returns:
        string: Language code retrieved either from request object or settings.
    """
    if request and hasattr(request, "LANGUAGE_CODE"):
        return request.LANGUAGE_CODE

    return settings.LANGUAGE_CODE
