# -*- coding: utf-8 -*-
"""
Exceptions
==========

Specific application exceptions.
"""


class MyAppBaseException(Exception):
    """
    Exception base.

    You should never use it directly except for test purpose. Instead make or
    use a dedicated exception related to the error context.
    """
    pass


class DummyError(MyAppBaseException):
    """
    Dummy exception sample to raise from your code.
    """
    pass
