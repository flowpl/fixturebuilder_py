# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['FixtureBuilderTest::test_return_builder_data_as_json 1'] = '{"list1": ["listvalue1"], "dict1": {"dictprop1": "dictvalue1"}, "prop1": "value1", "prop2": "value2", "list2": [{"listdictprop1": "listdictvalue1"}, {"listdictprop2": "listdictvalue2", "listdictprop3": "listdictvalue3"}]}'
