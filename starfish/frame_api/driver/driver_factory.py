from oslo_config import cfg
from oslo_log import log as logging
from stevedore import driver as stevedore_driver
from wsme import types as wtypes

from starfish.common import exceptions

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def get_driver(provider):
    """
    Choose and use different driver mod with argument provider
    :param provider: driver mod
    :return: driver
    """
    if isinstance(provider, wtypes.UnsetType):
        provider = 'test_provider'

    # There is only one mod for now
    try:
        driver = stevedore_driver.DriverManager(
            namespace='starfish.api.drivers',
            name=provider,
            invoke_on_load=True
        ).driver
        driver.name = provider
    except Exception as e:
        LOG.error('Unable to load provider driver %s due to: %s',
                  provider, e)
        raise exceptions.ProviderNotFound(prov=provider)
    return driver
