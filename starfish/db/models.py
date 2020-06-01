#    Copyright 2014 Rackspace
#    Copyright 2016 Blue Box, an IBM Company
#    Copyright 2017 Walmart Stores Inc.
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


import sqlalchemy as sa
from oslo_db.sqlalchemy import models

from starfish.common import data_models
from starfish.db import base_models
from starfish.frame_api.v1.types import test_entity


class TestEntity(base_models.BASE, base_models.IdMixin,
                 models.TimestampMixin, base_models.NameMixin):
    __data_model__ = data_models.TestEntity

    __tablename__ = "test_entity"

    __v1_wsme__ = test_entity.TestEntityResponse

    manage_ip = sa.Column('manage_ip', sa.String(64), nullable=False)

# class TestEntity1(base_models.BASE, base_models.IdMixin,
#                  models.TimestampMixin, base_models.NameMixin):
#     pass

# class TestEntity2(base_models.BASE, base_models.IdMixin,
#                  models.TimestampMixin, base_models.NameMixin):
#     pass
