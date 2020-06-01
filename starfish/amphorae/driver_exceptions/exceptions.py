# Copyright 2011-2014 OpenStack Foundation,author: Min Wang,German Eichberger
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import six
from oslo_utils import excutils

from starfish.i18n import _


class AmphoraDriverError(Exception):
    message = _("A super class for all other exceptions and the catch.")

    def __init__(self, **kwargs):
        try:
            super(AmphoraDriverError, self).__init__(self.message % kwargs)
            self.msg = self.message % kwargs
        except Exception:
            with excutils.save_and_reraise_exception() as ctxt:
                if not self.use_fatal_exceptions():
                    ctxt.reraise = False
                    # at least get the core message out if something happened
                    super(AmphoraDriverError, self).__init__(self.message)

    def __unicode__(self):
        return six.text_type(self.msg)

    @staticmethod
    def use_fatal_exceptions():
        """Return True if use fatal exceptions by raising them."""
        return False


class NotFoundError(AmphoraDriverError):
    message = _('this amphora couldn\'t be found')


class InfoException(AmphoraDriverError):
    message = _('gathering information about this amphora failed')


class MetricsException(AmphoraDriverError):
    message = _('gathering metrics failed')


class UnauthorizedException(AmphoraDriverError):
    message = _('the driver can\'t access the amphora')


class StatisticsException(AmphoraDriverError):
    message = _('gathering statistics failed')


class TimeOutException(AmphoraDriverError):
    message = _('contacting the amphora timed out')


class DeleteFailed(AmphoraDriverError):
    message = _('this load balancer couldn\'t be deleted')


class SuspendFailed(AmphoraDriverError):
    message = _('this load balancer couldn\'t be suspended')


class EnableFailed(AmphoraDriverError):
    message = _('this load balancer couldn\'t be enabled')


class ArchiveException(AmphoraDriverError):
    message = _('couldn\'t archive the logs')


class ProvisioningErrors(AmphoraDriverError):
    message = _('Super class for provisioning amphora errors')


class ListenerProvisioningError(ProvisioningErrors):
    message = _('couldn\'t provision Listener')


class LoadBalancerProvisoningError(ProvisioningErrors):
    message = _('couldn\'t provision LoadBalancer')


class HealthMonitorProvisioningError(ProvisioningErrors):
    message = _('couldn\'t provision HealthMonitor')


class NodeProvisioningError(ProvisioningErrors):
    message = _('couldn\'t provision Node')


class AmpDriverNotImplementedError(AmphoraDriverError):
    message = _('Amphora does not implement this feature.')


class AmpConnectionRetry(AmphoraDriverError):
    message = _('Could not connect to amphora, exception caught: '
                '%(exception)s')
