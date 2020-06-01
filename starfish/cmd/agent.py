# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

# make sure PYTHONPATH includes the home directory if you didn't install

import gunicorn.app.base
import multiprocessing as multiproc
# import ssl
import sys
from oslo_config import cfg
from oslo_reports import guru_meditation_report as gmr

from starfish import version
from starfish.amphorae.backends.agent.api_server import server
# from health_daemon import health_daemon
from starfish.common import service
from starfish.common import utils

CONF = cfg.CONF

HM_SENDER_CMD_QUEUE = multiproc.Queue()
HM_SENDER_CMD_QUEUE.put("shutdown")


class AmphoraAgent(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(AmphoraAgent, self).__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


# start api server
def main():
    # comment out to improve logging
    service.prepare_service(sys.argv)

    gmr.TextGuruMeditation.setup_autorun(version)

    # Initiate server class
    server_instance = server.Server()

    # bind the ip address in your host
    bind_ip_port = utils.ip_port_str('192.168.240.147',
                                     CONF.haproxy_amphora.bind_port)
    options = {
        'bind': bind_ip_port,
        'workers': 1,
        'timeout': CONF.amphora_agent.agent_request_read_timeout,
        'preload_app': True,
        'accesslog': '/var/log/amphora-agent.log',
        'errorlog': '/var/log/amphora-agent.log',
        'loglevel': 'debug',
        'syslog': True,
        'syslog_facility': 'local{}'.format(
            CONF.amphora_agent.administrative_log_facility),
        # 'syslog_addr': 'unix://run/rsyslog/octavia/log#dgram',

    }
    AmphoraAgent(server_instance.app, options).run()


main()
