import pecan
from oslo_db import api as oslo_db_api
from oslo_db import exception as odb_exceptions
from oslo_log import log as logging
from oslo_utils import uuidutils, excutils
from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from starfish.common import constants
from starfish.common import exceptions
from starfish.db import api as db_api
from starfish.frame_api.driver import driver_factory
from starfish.frame_api.driver import utils as driver_utils
from starfish.frame_api.v1.controller import base
from starfish.frame_api.v1.types import test_entity as te_types

LOG = logging.getLogger(__name__)


class TestEntitiesController(base.BaseController):

    def __init__(self):
        super(TestEntitiesController, self).__init__()

    @wsme_pecan.wsexpose(te_types.TestEntityResponse, wtypes.text,
                         [wtypes.text], ignore_extra_args=True)
    def get_one(self, id, fields=None):
        """Get a single test entity's details."""
        context = pecan.request.context.get('octavia_context')
        test_entity_db = self._get_db_te(context.session, id)

        if id == constants.NIL_UUID:
            raise exceptions.NotFound(resource='Test Entity', id=constants.NIL_UUID)

        result = self._convert_db_to_type(
            test_entity_db, te_types.TestEntityResponse)
        if fields is not None:
            result = self._filter_fields([result], fields)[0]
        # return te_types.TestEntityResponse(test_entity=result)
        return result

    @wsme_pecan.wsexpose(te_types.TestEntitiesRootResponse, wtypes.text,
                         [wtypes.text], ignore_extra_args=True)
    def get_all(self, fields=None):
        """List all test entities"""
        pcontext = pecan.request.context
        context = pcontext.get('octavia_context')
        test_entity_db, links = self.repositories.test_entity.get_all(
            context.session,
            # pagination_helper=pcontext.get(constants.PAGINATION_HELPER)
        )

        result = self._convert_db_to_type(
            test_entity_db, [te_types.TestEntityResponse])
        if fields is not None:
            result = self._filter_fields([result], fields)[0]

        return te_types.TestEntitiesRootResponse(
            testentities=result, testentities_links=links
        )

    @wsme_pecan.wsexpose(te_types.TestEntityResponse,
                         body=te_types.TestEntityRootPOST, status_code=201)
    def post(self, test_entity_):
        """create a test entity in db and agent"""
        test_entity_post = test_entity_.testentity
        # context = pecan.request.context.get('octavia_context')

        lock_session = db_api.get_session(autocommit=True)
        try:
            test_entity_dict = test_entity_post.to_dict(render_unsets=True)
            # test_entity_dict[id] = uuidutils.generate_uuid()
            test_entity_dict.update(id=uuidutils.generate_uuid())
            test_entity_db = self.repositories.test_entity.create(lock_session,
                                                                  **test_entity_dict)
        except odb_exceptions.DBDuplicateEntry:
            lock_session.rollback()
            raise exceptions.RecordAlreadyExists(field='test_entity',
                                                 name=test_entity_post.name)
        except Exception:
            with excutils.save_and_reraise_exception():
                lock_session.rollback()

        result = self._convert_db_to_type(test_entity_db,
                                          te_types.TestEntityResponse)

        return result

    @wsme_pecan.wsexpose(te_types.TestEntityRootResponse,
                         wtypes.text, status_code=200,
                         body=te_types.TestEntityRootPUT)
    def put(self, id, test_entity):
        pass

    @oslo_db_api.wrap_db_retry(max_retries=5, retry_on_deadlock=True)
    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, id):
        pass


class TestAgentController(base.BaseController):

    def __init__(self):
        super(TestAgentController, self).__init__()

    @wsme_pecan.wsexpose(wtypes.text)
    def get(self):
        driver = driver_factory.get_driver("test_provider")
        info = driver_utils.call_provider(driver.name, driver.get_agent_test_info)

        return info
