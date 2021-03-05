# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest

from src.executor.nested_loop_join_executor import NestedLoopJoinExecutor
from src.executor.table_function_scan_executor import TableFunctionScanExecutor
from src.expression.function_expression import FunctionExpression
from src.parser.types import JoinType
from src.models.storage.batch import Batch
from test.util import create_dataframe
from test.executor.utils import DummyExecutor


class NestedJoinExecutorTest(unittest.TestCase):

    def test_should_work_with_lateral_join(self):
        dataframe = create_dataframe(3)
        batch = Batch(frames=dataframe)
        outer = DummyExecutor([batch])
        expression = FunctionExpression(lambda x: x['data'])
        plan = type('TableFunctionPlan', (), {'func_expr': expression})
        inner = TableFunctionScanExecutor(node=plan)
        nested_loop_plan = type('NestedLoopJoin', (), {
                                'join_type': JoinType.LATERAL_JOIN,
                                'join_predicate': None})
        nested_loop_executor = NestedLoopJoinExecutor(nested_loop_plan)
        nested_loop_executor.append_child(outer)
        nested_loop_executor.append_child(inner)

        expected = batch.project(['data'])
        actual = list(nested_loop_executor.exec())[0]
        self.assertEqual(expected, actual)
