# Copyright 2015 Hewlett-Packard Development Company, L.P.
# Copyright (c) 2015 Rackspace
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
import functools
import requests
import simplejson
import six
import time
import warnings
from oslo_config import cfg
from oslo_log import log as logging

from starfish.amphorae import exceptions as exc
from starfish.amphorae.driver_exceptions import exceptions as driver_except

OCTAVIA_API_CLIENT = (
    "Octavia HaProxy Rest Client/{version} "
    "(https://wiki.openstack.org/wiki/Octavia)").format(version='1.0')

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class RestDriverTest(object):

    def __init__(self):
        super(RestDriverTest, self).__init__()
        self.client = AmphoraAPIClient1_0()

    def get_version_info(self, msg='/', bind_ip_port={}):
        info = self.client.get_version(msg, bind_ip_port)
        return info

    def delete(self, msg, ip='127.0.0.1', port='8976'):
        self.client.delete_listener(msg, {'ip': ip, "port": port})
        return


def _base_url(ip, port):
    return "http://{ip}:{port}".format(
        ip=ip,
        port=port)


class AmphoraAPIClientBase(object):
    def __init__(self):
        super(AmphoraAPIClientBase, self).__init__()

        self.get = functools.partial(self.request, 'get')
        self.post = functools.partial(self.request, 'post')
        self.put = functools.partial(self.request, 'put')
        self.delete = functools.partial(self.request, 'delete')
        self.head = functools.partial(self.request, 'head')

        self.session = requests.Session()

    def request(self, method, setting, path='/', retry_404=True,
                raise_retry_exception=False, **kwargs):
        req_conn_timeout = 10
        req_read_timeout = 60
        conn_max_retries = 120
        conn_retry_interval = 5

        print("request path", path)
        _request = getattr(self.session, method.lower())
        _url = _base_url(setting['ip'], setting['port']) + path
        print("request url", _url)
        reqargs = {
            'url': _url,
            'timeout': (req_conn_timeout, req_read_timeout)}
        reqargs.update(kwargs)
        headers = reqargs.setdefault('headers', {})
        reqargs['verify'] = False

        headers['User-Agent'] = OCTAVIA_API_CLIENT
        exception = None
        # Keep retrying
        for dummy in six.moves.xrange(conn_max_retries):
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        message="A true SSLContext object is not available"
                    )
                    r = _request(**reqargs)
                print('Connected to amphora. Response:', r)

                content_type = r.headers.get('content-type', '')
                # Check the 404 to see if it is just that the network in the
                # amphora is not yet up, in which case retry.
                # Otherwise return the response quickly.
                if r.status_code == 404:
                    if not retry_404:
                        raise exc.NotFound()
                    print('Got a 404 (content-type: %(content_type)s) -- '
                          'connection data: %(content)s',
                          {'content_type': content_type,
                           'content': r.content})
                    if content_type.find("application/json") == -1:
                        print("Amphora agent not ready.")
                        raise requests.ConnectionError
                    try:
                        json_data = r.json().get('details', '')
                        if 'No suitable network interface found' in json_data:
                            print("Amphora network interface not found.")
                            raise requests.ConnectionError
                    except simplejson.JSONDecodeError:  # if r.json() fails
                        pass  # TODO(rm_work) Should we do something?
                return r
            except (requests.ConnectionError, requests.Timeout) as e:
                exception = e
                print(e)
                print("Could not connect to instance. Retrying.")
                time.sleep(conn_retry_interval)
                if raise_retry_exception:
                    # For taskflow persistence cause attribute should
                    # be serializable to JSON. Pass None, as cause exception
                    # is described in the expection message.
                    six.raise_from(
                        driver_except.AmpConnectionRetry(exception=str(e)),
                        None)
        print("Connection retries (currently set to %(max_retries)s) "
              "exhausted.  The amphora is unavailable. Reason: "
              "%(exception)s",
              {'max_retries': conn_max_retries,
               'exception': exception})
        raise driver_except.TimeOutException()


class AmphoraAPIClient1_0(AmphoraAPIClientBase):
    def __init__(self):
        super(AmphoraAPIClient1_0, self).__init__()

    def get_version(self, path, bind_ip_port):
        r = self.get(bind_ip_port, path)
        if exc.check_exception(r):
            return r.json()
        return None

    def delete_listener(self, path, setting):
        r = self.delete(setting, path)
        return exc.check_exception(r, (404,))
