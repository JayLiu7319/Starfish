# Copyright 2014 Rackspace
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import oslo_messaging as messaging
from oslo_config import cfg
from oslo_log import log as logging

from starfish.common import constants
from starfish.controller.worker.v1 import controller_worker

# from stevedore import driver as stevedore_driver

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Endpoints(object):
    # API version history:
    #   1.0 - Initial version.
    target = messaging.Target(
        namespace=constants.RPC_NAMESPACE_CONTROLLER_AGENT,
        version='1.0')

    def __init__(self):
        self.worker = controller_worker.ControllerWorker()

    def get_agent_info(self, context):
        LOG.info('Getting the backend agent info ...')
        self.worker.get_agent_info()

    # def create_load_balancer(self, context, load_balancer_id,
    #                          flavor=None, availability_zone=None):
    #     LOG.info('Creating load balancer \'%s\'...', load_balancer_id)
    #     self.worker.create_load_balancer(load_balancer_id, flavor,
    #                                      availability_zone)
