from oslo_config import cfg
from oslo_log import log as logging
from stevedore import driver as stevedore_driver
from taskflow import task

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class BaseAmphoraTask(task.Task):
    """Base task to load drivers common to all tasks"""

    def __init__(self, **kwargs):
        super(BaseAmphoraTask, self).__init__(**kwargs)
        self.amphora_driver = stevedore_driver.DriverManager(
            namespace='starfish.amphora.drivers',
            name='amphora_rest_driver',
            invoke_on_load=True
        ).driver


class GetVersionInfo(BaseAmphoraTask):
    """Task to Get backend agent version info"""

    def execute(self, *args, **kwargs):
        """Excute get backend info in an amphora"""

        try:
            # bind the ip and port of the remote agent host
            bind_ip_port = {'ip': '192.168.240.147',
                            'port': '9443'}
            info = self.amphora_driver.get_version_info(bind_ip_port=bind_ip_port)
            LOG.info('Get info as %s ', info)

        except Exception as e:
            LOG.error('Failed to get info from backend agent')
