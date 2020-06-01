from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from starfish.frame_api.v1.controller import base
from starfish.frame_api.v1.controller import test_entity


class V1Controller(base.BaseController):
    testentities = None

    def __init__(self):
        super(V1Controller, self).__init__()
        self.testentities = test_entity.TestEntitiesController()
        self.agent = test_entity.TestAgentController()

    @wsme_pecan.wsexpose(wtypes.text)
    def get(self):
        return "v1"
