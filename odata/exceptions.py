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
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

        self.status_code = None
        """HTTP status"""

        self.code = None
        """Error code supplied by server"""

        self.message = None
        """Error message supplied by server"""

        self.detailed_message = None
        """Detailed error message supplied by server"""


class ODataConnectionError(ODataError):
    """Raised when the endpoint responds with an HTTP error code"""
    pass


class ODataQueryError(ODataError):
    pass


class ODataReflectionError(ODataError):
    """
    Raised when MetaData is unable to reflect types
    """
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
