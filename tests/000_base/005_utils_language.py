from lotus.utils.language import get_language_code


class DummyRequest:
    """
    Dummy class just to set attribute 'LANGUAGE_CODE' to fake behavior with request
    object.
    """
    def __init__(self, lang=None):
        if lang is not None:
            self.LANGUAGE_CODE = lang


def test_get_language_code(settings):
    """
    Function should return language code from request if available, else the one from
    settings.
    """
    # No given request, use setting
    assert get_language_code() == settings.LANGUAGE_CODE
    # Request does not have LANGUAGE_CODE attribute, use setting
    assert get_language_code(DummyRequest()) == settings.LANGUAGE_CODE
    # Request have LANGUAGE_CODE attribute so use it
    assert get_language_code(DummyRequest(lang="zh")) == "zh"
    # Function does not care if attribute has been set to an empty string, it just use
    # it if exists
    assert get_language_code(DummyRequest(lang="")) == ""
