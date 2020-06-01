# """
#   @author liujiye
#   @create_time  12:11
#   @email 1299870737@qq.com
# """
#
# from wsme import types as wsme_types
# from wsme.rest import json as wsme_json
#
# from starfish.frame_api.v1.types import test_entity as te_type
# from starfish.tests.unit.frame_api.common import base
#
#
# class TestTestEntityPost(base.BaseTypesTest):
#     _type = te_type.TestEntityPOST
#
#     def test_te(self):
#         body = {"name": "test_name", "manage_ip": "0.0.0.0"}
#         testentity = wsme_json.fromjson(self._type, body)
#         self.assertEqual(wsme_types.Unset, testentity.id)
#         self.assertEqual(wsme_types.Unset, testentity.created_at)
#         self.assertEqual(wsme_types.Unset, testentity.updated_at)
