# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_function_from_statement[SELECT name FROM users;] 1'] = '''
_some_function_name_STATEMENT = r"""
SELECT name FROM users;
"""
def some_function_name(connection, **kwargs):
    return core.execute(connection, _some_function_name_STATEMENT, kwargs)
'''
