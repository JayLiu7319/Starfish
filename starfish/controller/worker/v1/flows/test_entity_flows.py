from oslo_log import log as logging
from taskflow.patterns import linear_flow

# from starfish.common import constants
# from starfish.controller.worker.v1.tasks import database_tasks
from starfish.controller.worker.v1.tasks import amphora_driver_tasks

LOG = logging.getLogger(__name__)


class TestEntityFlows(object):

    def get_backend_info_flow(self):
        get_info_flow = linear_flow.Flow('starfish-get-backend-info-flow')
        get_info_flow.add(amphora_driver_tasks.GetVersionInfo())
        # get_info_flow.add(database_tasks.DoSomething)
        LOG.info("TaskFlow for get backend info started.")
        return get_info_flow
