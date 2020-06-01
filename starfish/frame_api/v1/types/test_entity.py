from wsme import types as wtypes

from starfish.frame_api.common import types


class BaseTestEntityType(types.BaseType):
    _type_to_model_map = {}
    _child_map = {}


class TestEntityResponse(BaseTestEntityType):
    """Defines which attributes are to be shown on any response."""
    id = wtypes.wsattr(wtypes.UuidType())
    name = wtypes.wsattr(wtypes.StringType())
    manage_ip = wtypes.wsattr(wtypes.IPv4AddressType())
    created_at = wtypes.wsattr(wtypes.datetime.datetime)
    updated_at = wtypes.wsattr(wtypes.datetime.datetime)

    @classmethod
    def from_data_model(cls, data_model, children=False):
        testentity = super(TestEntityResponse, cls).from_data_model(
            data_model, children=children
        )
        return testentity


class TestEntityRootResponse(types.BaseType):
    testentity = wtypes.wsattr(TestEntityResponse)


class TestEntitiesRootResponse(types.BaseType):
    testentities = wtypes.wsattr([TestEntityResponse])
    testentities_links = wtypes.wsattr([types.PageType])


class TestEntityPOST(BaseTestEntityType):
    """Defines mandatory and optional attributes of a POST request."""
    name = wtypes.wsattr(wtypes.StringType(max_length=255), mandatory=True)
    manage_ip = wtypes.wsattr(wtypes.IPv4AddressType(), mandatory=True)


class TestEntityRootPOST(types.BaseType):
    testentity = wtypes.wsattr(TestEntityPOST)


class TestEntityPUT(BaseTestEntityType):
    """Defines the attributes of a PUT request."""
    name = wtypes.wsattr(wtypes.StringType(max_length=255))


class TestEntityRootPUT(types.BaseType):
    testentity = wtypes.wsattr(TestEntityPUT)
