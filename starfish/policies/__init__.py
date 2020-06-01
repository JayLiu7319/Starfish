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


import itertools

from starfish.policies import amphora
from starfish.policies import availability_zone
from starfish.policies import base
from starfish.policies import flavor_profile
from starfish.policies import healthmonitor
from starfish.policies import l7policy
from starfish.policies import l7rule
from starfish.policies import loadbalancer
from starfish.policies import member
from starfish.policies import provider, pool, provider_flavor, availability_zone_profile, listener, flavor
from starfish.policies import provider_availability_zone
from starfish.policies import quota


def list_rules():
    return itertools.chain(
        base.list_rules(),
        flavor.list_rules(),
        flavor_profile.list_rules(),
        availability_zone.list_rules(),
        availability_zone_profile.list_rules(),
        healthmonitor.list_rules(),
        l7policy.list_rules(),
        l7rule.list_rules(),
        listener.list_rules(),
        loadbalancer.list_rules(),
        member.list_rules(),
        pool.list_rules(),
        provider.list_rules(),
        quota.list_rules(),
        amphora.list_rules(),
        provider_flavor.list_rules(),
        provider_availability_zone.list_rules(),
    )
