#    Copyright (c) 2014 Rackspace
#    Copyright (c) 2016 Blue Box, an IBM Company
#    All Rights Reserved.
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

import re

import six
from sqlalchemy.orm import collections


class BaseDataModel(object):
    def to_dict(self, calling_classes=None, recurse=False, **kwargs):
        """Converts a data model to a dictionary."""
        calling_classes = calling_classes or []
        ret = {}
        for attr in self.__dict__:
            if attr.startswith('_') or not kwargs.get(attr, True):
                continue
            value = self.__dict__[attr]
            if attr == 'tags':
                # tags is a list, it doesn't need recurse
                ret[attr] = value
                continue

            if recurse:
                if isinstance(getattr(self, attr), list):
                    ret[attr] = []
                    for item in value:
                        if isinstance(item, BaseDataModel):
                            if type(self) not in calling_classes:
                                ret[attr].append(
                                    item.to_dict(calling_classes=(
                                            calling_classes + [type(self)]),
                                        recurse=recurse))
                            else:
                                # TODO(rm_work): Is the idea that if this list
                                #  contains ANY BaseDataModel, that all of them
                                #  are data models, and we may as well quit?
                                #  Or, were we supposed to append a `None` for
                                #  each one? I assume the former?
                                ret[attr] = None
                                break
                        else:
                            ret[attr].append(item)
                elif isinstance(getattr(self, attr), BaseDataModel):
                    if type(self) not in calling_classes:
                        ret[attr] = value.to_dict(
                            calling_classes=calling_classes + [type(self)],
                            recurse=recurse)
                    else:
                        ret[attr] = None
                elif six.PY2 and isinstance(value, six.text_type):
                    ret[attr.encode('utf8')] = value.encode('utf8')
                else:
                    ret[attr] = value
            else:
                if isinstance(getattr(self, attr), BaseDataModel):
                    ret[attr] = None
                elif isinstance(getattr(self, attr), list):
                    ret[attr] = []
                else:
                    ret[attr] = value

        return ret

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.to_dict() == other.to_dict()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_dict(cls, dict):
        return cls(**dict)

    @classmethod
    def _name(cls):
        """Returns class name in a more human readable form."""
        # Split the class name up by capitalized words
        return ' '.join(re.findall('[A-Z][^A-Z]*', cls.__name__))

    def _get_unique_key(self, obj=None):
        """Returns a unique key for passed object for data model building."""
        obj = obj or self
        # First handle all objects with their own ID, then handle subordinate
        # objects.
        if obj.__class__.__name__ in ['Member', 'Pool', 'LoadBalancer',
                                      'Listener', 'Amphora', 'L7Policy',
                                      'L7Rule']:
            return obj.__class__.__name__ + obj.id
        if obj.__class__.__name__ in ['SessionPersistence', 'HealthMonitor']:
            return obj.__class__.__name__ + obj.pool_id
        if obj.__class__.__name__ in ['ListenerStatistics']:
            return obj.__class__.__name__ + obj.listener_id + obj.amphora_id
        if obj.__class__.__name__ in ['ListenerCidr']:
            return obj.__class__.__name__ + obj.listener_id + obj.cidr
        if obj.__class__.__name__ in ['VRRPGroup', 'Vip']:
            return obj.__class__.__name__ + obj.load_balancer_id
        if obj.__class__.__name__ in ['AmphoraHealth']:
            return obj.__class__.__name__ + obj.amphora_id
        if obj.__class__.__name__ in ['SNI']:
            return (obj.__class__.__name__ +
                    obj.listener_id + obj.tls_container_id)
        raise NotImplementedError

    def _find_in_graph(self, key, _visited_nodes=None):
        """Locates an object with the given unique key in the current

        object graph and returns a reference to it.
        """
        _visited_nodes = _visited_nodes or []
        mykey = self._get_unique_key()
        if mykey in _visited_nodes:
            # Seen this node already, don't traverse further
            return None
        if mykey == key:
            return self
        _visited_nodes.append(mykey)
        attr_names = [attr_name for attr_name in dir(self)
                      if not attr_name.startswith('_')]
        for attr_name in attr_names:
            attr = getattr(self, attr_name)
            if isinstance(attr, BaseDataModel):
                result = attr._find_in_graph(
                    key, _visited_nodes=_visited_nodes)
                if result is not None:
                    return result
            elif isinstance(attr, (collections.InstrumentedList, list)):
                for item in attr:
                    if isinstance(item, BaseDataModel):
                        result = item._find_in_graph(
                            key, _visited_nodes=_visited_nodes)
                        if result is not None:
                            return result
        # If we are here we didn't find it.
        return None

    def update(self, update_dict):
        """Generic update method which works for simple,

        non-relational attributes.
        """
        for key, value in update_dict.items():
            setattr(self, key, value)


class TestEntity(BaseDataModel):
    def __init__(self, id=None, name=None, manage_ip=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.manage_ip = manage_ip
        self.created_at = created_at
        self.updated_at = updated_at


# class TestEntity1(BaseDataModel):
#     def __init__(self):
#         pass

# class TestEntity2(BaseDataModel):
#     def __init__(self):
#         pass


class LoadBalancer(BaseDataModel):
    """
    !!! This data model is for reference!!!
    !!! Not For Using !!!
    """

    def __init__(self, id=None, project_id=None, name=None, description=None,
                 provisioning_status=None, operating_status=None, enabled=None,
                 topology=None, vip=None, listeners=None, amphorae=None,
                 pools=None, vrrp_group=None, server_group_id=None,
                 created_at=None, updated_at=None, provider=None, tags=None,
                 flavor_id=None, availability_zone=None):

        self.id = id
        self.project_id = project_id
        self.name = name
        self.description = description
        self.provisioning_status = provisioning_status
        self.operating_status = operating_status
        self.enabled = enabled
        self.vip = vip
        self.vrrp_group = vrrp_group
        self.topology = topology
        self.listeners = listeners or []
        self.amphorae = amphorae or []
        self.pools = pools or []
        self.server_group_id = server_group_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.provider = provider
        self.tags = tags or []
        self.flavor_id = flavor_id
        self.availability_zone = availability_zone

    def update(self, update_dict):
        for key, value in update_dict.items():
            if key == 'vip':
                if self.vip is not None:
                    self.vip.update(value)
                else:
                    value.update({'load_balancer_id': self.id})
                    # self.vip = Vip(**value)
            else:
                setattr(self, key, value)
