# -*- coding: utf-8 -*-


class ODataError(Exception):
    pass


class ODataConnectionError(ODataError):
    pass


class ODataQueryError(ODataError):
    pass


class NoResultsFound(ODataQueryError):
    pass


class MultipleResultsFound(ODataQueryError):
    pass
