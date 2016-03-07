#!/usr/bin/env python
'''
$Id: http.py,v 1.1 2015/04/17 21:21:09 weiwang Exp $

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

====

File Uploader
'''

import requests

class HTTP4xx(BaseException):
    '''Base exception for all 400 HTTP exceptions.
    '''
    HTTP4xxMsg = 'HTTP4xx exception'
    def __init__(self):
        BaseException.__init__(self, self.HTTP4xxMsg)

class HTTP5xx(StandardError):
    '''Base error for all 500 HTTP exceptions.
    '''
    HTTP5xxMsg = 'HTTP5xx error'
    def __init__(self):
        StandardError.__init__(self, self.HTTP5xxMsg)

class BadRequest(HTTP4xx):
    HTTP4xxMsg = '400: Bad request'

class Forbidden(HTTP4xx):
    HTTP4xxMsg = '403: Forbidden'

class NotAuthorized(HTTP4xx):
    HTTP4xxMsg = '401: Not authorized'

class NotFound(HTTP4xx):
    HTTP4xxMsg = '404: Not found'

class PaymentRequired(HTTP4xx):
    HTTP4xxMsg = '402: Payment required'

class MethodNotAllowed(HTTP4xx):
    HTTP4xxMsg = '405: Method not allowed'

class NotAcceptable(HTTP4xx):
    HTTP4xxMsg = '406: Not acceptable'

class ProxyAuthenticationRequired(HTTP4xx):
    HTTP4xxMsg = '407: Proxy authentication required'

class RequestTimeout(HTTP4xx):
    HTTP4xxMsg = '408: Request timeout'

class Conflict(HTTP4xx):
    HTTP4xxMsg = '409: Conflict'

class Gone(HTTP4xx):
    HTTP4xxMsg = '410: Gone'

class LengthRequired(HTTP4xx):
    HTTP4xxMsg = '411: Length required'

class PreconditionFailed(HTTP4xx):
    HTTP4xxMsg = '412: Precondition failed'

class RequestEntityTooLarge(HTTP4xx):
    HTTP4xxMsg = '413: Request entity too large'

class RequestURITooLong(HTTP4xx):
    HTTP4xxMsg = '414: Request-URI too long'

class UnsupportedMediaType(HTTP4xx):
    HTTP4xxMsg = '415: Unsupported media type'

class RequestedRangeNotSatisfiable(HTTP4xx):
    HTTP4xxMsg = '416: Requested range not satisfiable'

class ExpectationFailed(HTTP4xx):
    HTTP4xxMsg = '417: Expectation failed'

exceptions = {
    400: BadRequest,
    401: NotAuthorized,
    402: PaymentRequired,
    403: Forbidden,
    404: NotFound,
    405: MethodNotAllowed,
    406: NotAcceptable,
    407: ProxyAuthenticationRequired,
    408: RequestTimeout,
    409: Conflict,
    410: Gone,
    411: LengthRequired,
    412: PreconditionFailed,
    413: RequestEntityTooLarge,
    414: RequestURITooLong,
    415: UnsupportedMediaType,
    416: RequestedRangeNotSatisfiable,
    417: ExpectationFailed
    }


class InternalServerError(HTTP5xx):
    HTTP5xxMsg = '500: Internal Server Error'

class NotImplemented(HTTP5xx):
    HTTP5xxMsg = '501: Not Implemented'

class ServiceUnavailable(HTTP5xx):
    HTTP5xxMsg = '503: Service Unavailable'

class BadGateway(HTTP5xx):
    HTTP5xxMsg = '502: Bad Gateway'

class GatewayTimeout(HTTP5xx):
    HTTP5xxMsg = '504: Gateway Timeout'

class HTTPVersionNotSupported(HTTP5xx):
    HTTP5xxMsg = '505: HTTP Version Not Supported'

errors = {
    500: InternalServerError,
    501: NotImplemented,
    502: BadGateway,
    503: ServiceUnavailable,
    504: GatewayTimeout,
    505: HTTPVersionNotSupported
    }


def put(files, url, data={}):
    '''Upload a give (list of) file(s) to a destination specified by /url/.

    /files/ may be a file name in the form of a string; Or a dict keyed with
    variable and value in filename or binary data object.

    Returns responses from Requests.post() in a dict, keyed by files.
    '''
    if isinstance(files, basestring):
        files = dict(file=files)
    status = dict()
    for var,fdata in files.iteritems():
        parts = { var: (fdata, open(fdata, 'rb') if isinstance(fdata, basestring) else fdata) }
        status[fdata] = requests.post(url, files=parts, data=data)
    return status

if __name__ == '__main__':
    import doctest
    doctest.testfile('test/http.text')
