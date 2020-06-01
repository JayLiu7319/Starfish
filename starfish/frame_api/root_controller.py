from oslo_log import log as logging
from pecan import request as pecan_request
from pecan import rest
from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from starfish.frame_api.v1 import controller as v1_controller

LOG = logging.getLogger(__name__)


class RootController(rest.RestController):
    def __init__(self):
        super(RootController, self).__init__()
        setattr(self, 'v1', v1_controller.V1Controller())

    def _add_a_version(self, versions, version, url_version, status,
                       timestamp, base_url):
        versions.append(
            {
                'id': version,
                'status': status,
                'updated': timestamp,
                'links': [{
                    'href': base_url + url_version,
                    'rel': 'self'
                }]
            }
        )

    @wsme_pecan.wsexpose(wtypes.text)
    def get(self):
        host_url = pecan_request.path_url

        if not host_url.endswith('/'):
            host_url = '{}/'.format(host_url)

        versions = []
        self._add_a_version(versions, 'v1.0', 'v1', 'CURRENT',
                            '2020-02-26T00:00:00:00Z', host_url)
        return {'versions': versions}
