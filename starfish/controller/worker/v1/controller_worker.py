from oslo_config import cfg
from oslo_log import log as logging
from taskflow.listeners import logging as tf_logging

from starfish.amphorae.driver_exceptions import exceptions
from starfish.common import base_taskflow
from starfish.controller.worker.v1.flows import test_entity_flows

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


# We do not need to log retry exception information. Warning "Could not connect
#  to instance" will be logged as usual.
def retryMaskFilter(record):
    if record.exc_info is not None and isinstance(
            record.exc_info[1], exceptions.AmpConnectionRetry):
        return False
    return True


LOG.logger.addFilter(retryMaskFilter)


class ControllerWorker(base_taskflow.BaseTaskFlowEngine):

    def __init__(self):
        self._te_flows = test_entity_flows.TestEntityFlows()
        super(ControllerWorker, self).__init__()

    def get_agent_info(self):
        get_info_tf = self._taskflow_load(
            self._te_flows.get_backend_info_flow(),
            store={}
        )
        with tf_logging.DynamicLoggingListener(get_info_tf, log=LOG):
            get_info_tf.run()
