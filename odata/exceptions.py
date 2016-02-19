# -*- coding: utf-8 -*-

"""
Exceptions
==========

Error classes used by this library.
"""

class ODataError(Exception):
    """
    Base class for python-odata errors. All other errors are subclassed
    from this. Raising any other exception class is a bug and should be
    reported
    """
    pass


class ODataConnectionError(ODataError):
    """Raised when the endpoint responds with an HTTP error code"""
    pass


class ODataQueryError(ODataError):
    pass


class NoResultsFound(ODataQueryError):
    """
    Raised when :py:func:`~odata.query.Query.one` is called but zero results
    returned
    """
    pass


class MultipleResultsFound(ODataQueryError):
    """
    Raised when :py:func:`~odata.query.Query.one` is called but multiple results
    returned
    """
    pass
