from oslo_config import cfg
from oslo_config import fixture as oslo_fixture
from oslo_db.sqlalchemy import session as db_session
from oslo_db.sqlalchemy import test_base
from oslo_utils import uuidutils

from starfish.common import config
from starfish.db import api as db_api
from starfish.db import base_models


class DBTest(test_base.DbTestCase):

    def setUp(self, connection_string='sqlite://'):
        super(DBTest, self).setUp()
        conf = self.useFixture(oslo_fixture.Config(config.cfg.CONF))
        conf.config(group="database", connection=connection_string)

        if 'sqlite:///' in connection_string:
            facade = db_session.EngineFacade.from_config(cfg.CONF,
                                                         sqlite_fk=True)
            engine = facade.get_engine()
            self.session = facade.get_session(expire_on_commit=True,
                                              autocommit=True)
        else:
            engine = db_api.get_engine()
            self.session = db_api.get_session()

        base_models.BASE.metadata.create_all(engine)
        self._seed_lookup_tables(self.session)


if __name__ == '__main__':
    sqlite_db_file = '/tmp/starfish-{}.sqlite.db'.format(
        uuidutils.generate_uuid()
    )
    sqlite_db_connection = 'sqlite:///{}'.format(sqlite_db_file)

    db_test = DBTest()
    db_test.setUp(connection_string=sqlite_db_connection)
