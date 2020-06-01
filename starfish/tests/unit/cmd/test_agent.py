"""
  @author liujiye
  @create_time  11:22
  @email 1299870737@qq.com
"""

import ssl
from unittest import mock

from starfish.cmd import agent
from starfish.tests.unit import base


class TestBackendAgentCMD(base.TestCase):

    def setUp(self):
        super(TestBackendAgentCMD, self).setUp()

    @mock.patch('starfish.cmd.agent.AmphoraAgent')
    @mock.patch('starfish.amphorae.backends.agent.api_server.server.Server')
    @mock.patch('multiprocessing.Process')
    @mock.patch('starfish.common.service.prepare_service')
    def test_main(self, mock_service, mock_process, mock_server, mock_amp):
        mock_health_proc = mock.MagicMock()
        mock_server_instance = mock.MagicMock()
        mock_amp_instance = mock.MagicMock()

        mock_process.return_value = mock_health_proc
        mock_server.return_value = mock_server_instance
        mock_amp.return_value = mock_amp_instance
        agent.main()

        self.assertEqual(
            ssl.CERT_REQUIRED,
            mock_amp.call_args[0][1]['cert_reqs']
        )

        mock_health_proc.start.assert_called_once_with()
        mock_amp_instance.run.assert_called_once()
