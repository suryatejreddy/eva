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
from typing import Iterator

from src.models.storage.batch import Batch
from src.executor.abstract_executor import AbstractExecutor
from src.executor.abstract_executor import UPSTREAM_BATCH
from src.planner.function_scan import FunctionScanPlan


class TableFunctionScanExecutor(AbstractExecutor):
    """
    Executes functional expression which yields a table of rows
    Arguments:
        node (AbstractPlan): FunctionScanPlan

    """

    def __init__(self, node: FunctionScanPlan):
        super().__init__(node)
        self.func_expr = node.func_expr

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:

        # check if leaf node
        if len(self.children) == 0:
            batch = kwargs.pop(UPSTREAM_BATCH, Batch())
            if not batch.empty():
                yield self.func_expr.evaluate(batch)
            else:
                yield batch
