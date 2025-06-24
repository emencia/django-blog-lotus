class LotusException(Exception):
    """
    Exception base.

    You should never use it directly except for test purpose. Instead make or
    use a dedicated exception related to the error context.
    """
    pass


class DummyError(LotusException):
    """
    Dummy exception sample to raise from your code.
    """
    pass


class LanguageMismatchError(LotusException):
    """
    Raised when expected object language does not match.
    """
    pass


class Http500(Exception):
    """
    Raised from a view when a non blocking error (from bad configuration or else, not
    due to an exception) and we want to be explicit.
    """
    pass
