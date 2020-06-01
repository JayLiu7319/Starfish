# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import flask
import six
import webob
from oslo_config import cfg
from oslo_log import log as logging
from werkzeug import exceptions

from starfish.amphorae.backends.agent import api_server
from starfish.amphorae.backends.agent.api_server import osutils

# from backends.agent.api_server import util

BUFFER = 1024
CONF = cfg.CONF
PATH_PREFIX = '/' + api_server.VERSION
LOG = logging.getLogger(__name__)


# make the error pages all json
def make_json_error(ex):
    code = ex.code if isinstance(ex, exceptions.HTTPException) else 500
    response = webob.Response(json={'error': str(ex), 'http_code': code})
    response.status_code = code
    return response


def register_app_error_handler(app):
    for code in six.iterkeys(exceptions.default_exceptions):
        app.register_error_handler(code, make_json_error)


class Server(object):
    def __init__(self):
        self.app = flask.Flask(__name__)
        self._osutils = osutils.BaseOS.get_os_util()

        register_app_error_handler(self.app)
        self.app.add_url_rule(rule='/test',
                              view_func=self.response_test,
                              methods=['GET'])
        self.app.add_url_rule(rule='/',
                              view_func=self.version_discovery,
                              methods=['GET'])

    def error_handler(self):
        return True

    def version_discovery(self):
        return webob.Response(json={'api_version': api_server.VERSION})

    def response_test(self):
        return webob.Response(json={'info': 'Hello world!'})
