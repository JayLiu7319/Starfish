# Copyright 2014 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging
from webob import exc

LOG = logging.getLogger(__name__)


def check_exception(response, ignore=tuple()):
    status_code = response.status_code
    responses = {
        400: InvalidRequest,
        401: Unauthorized,
        403: Forbidden,
        404: NotFound,
        405: InvalidRequest,
        409: Conflict,
        500: InternalServerError,
        503: ServiceUnavailable
    }
    if (status_code not in ignore) and (status_code in responses):
        try:
            LOG.error('Amphora agent returned unexpected result code %s with '
                      'response %s', status_code, response.json())
        except Exception:
            # Handle the odd case where there is no response body
            # like when using requests_mock which doesn't support has_body
            pass
        raise responses[status_code]()

    return response


class APIException(exc.HTTPClientError):
    msg = "Something unknown went wrong"
    code = 500

    def __init__(self, **kwargs):
        self.msg = self.msg % kwargs
        super(APIException, self).__init__(detail=self.msg)


class InvalidRequest(APIException):
    msg = "Invalid request"
    code = 400


class Unauthorized(APIException):
    msg = "Unauthorized"
    code = 401


class Forbidden(APIException):
    msg = "Forbidden"
    code = 403


class NotFound(APIException):
    msg = "Not Found"
    code = 404


class Conflict(APIException):
    msg = "Conflict"
    code = 409


class InternalServerError(APIException):
    msg = "Internal Server Error"
    code = 500


class ServiceUnavailable(APIException):
    msg = "Service Unavailable"
    code = 503
