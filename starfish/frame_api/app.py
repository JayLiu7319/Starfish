import pecan
import sys
from oslo_config import cfg
from oslo_log import log as logging

# from frame_api.driver import driver_factory
# from common import keystone
from starfish.common import service as octavia_service
from starfish.frame_api import config as app_config

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def get_pecan_config():
    """Returns the pecan config."""
    filename = app_config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


# def _init_drivers():
#     """Initialize provider drivers."""

#     for provider in CONF.api_settings.enabled_provider_drivers:
#         driver_factory.get_driver(provider)


def setup_app(pecan_config=None, debug=True, argv=None):
    """Creates and returns a pecan wsgi app."""
    if argv is None:
        argv = sys.argv
    octavia_service.prepare_service(argv)
    cfg.CONF.log_opt_values(LOG, logging.DEBUG)

    # _init_drivers()

    if not pecan_config:
        pecan_config = get_pecan_config()
    pecan.configuration.set_config(dict(pecan_config), overwrite=True)

    return pecan.make_app(
        pecan_config.app.root,
        # wrap_app=_w
        debug=debug,
        hooks=pecan_config.app.hooks,
        wsme=pecan_config.wsme
    )
