import oslo_messaging as messaging
from octavia_lib.api.drivers import provider_base as driver_base
from oslo_config import cfg
from oslo_log import log as logging

from starfish.common import constants
from starfish.common import rpc

CONF = cfg.CONF
CONF.import_group('oslo_messaging', 'starfish.common.config')
LOG = logging.getLogger(__name__)


class TestProviderDriver(driver_base.ProviderDriver):
    def __init__(self):
        super(TestProviderDriver, self).__init__()
        # topic = cfg.CONF.oslo_messaging.topic
        topic = constants.TOPIC_AMPHORA_V2
        self.target = messaging.Target(
            namespace=constants.RPC_NAMESPACE_CONTROLLER_AGENT,
            topic=topic, version='1.0', fanout=False)
        self.client = rpc.get_client(self.target)

    def get_agent_test_info(self):
        # return "hello"
        payload = {}
        self.client.cast({}, 'get_agent_info', **payload)
        return 'Getting the backend agent info ...'
