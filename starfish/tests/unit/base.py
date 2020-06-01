"""
  @author liujiye
  @create_time  11:24
  @email 1299870737@qq.com
"""
import fixtures
import oslo_messaging as messaging
import testtools
from oslo_config import cfg
from oslo_messaging import conffixture as messaging_conffixture
from unittest import mock

from starfish.common import rpc


class TestCase(testtools.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.addCleanup(mock.patch.stopall)
        self.addCleanup(self.clean_caches)

    def clean_caches(self):
        # TODO: add keystone auth
        pass


class TestRpc(testtools.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestRpc, self).__init__(*args, **kwargs)
        self._buses = {}

    def _fake_create_transport(self, url):
        if url not in self._buses:
            self._buses[url] = messaging.get_rpc_transport(
                cfg.CONF,
                url=url)
        return self._buses[url]

    def setUp(self):
        super(TestRpc, self).setUp()
        self.addCleanup(rpc.cleanup)
        self.messaging_conf = messaging_conffixture.ConfFixture(cfg.CONF)
        self.messaging_conf.transport_url = 'fake:/'
        self.useFixture(self.messaging_conf)
        self.useFixture(fixtures.MonkeyPatch(
            'octavia.common.rpc.create_transport',
            self._fake_create_transport))
        with mock.patch('octavia.common.rpc.get_transport_url') as mock_gtu:
            mock_gtu.return_value = None
            rpc.init()
