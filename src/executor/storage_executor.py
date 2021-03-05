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
from src.planner.storage_plan import StoragePlan
from src.storage.storage_engine import StorageEngine


class StorageExecutor(AbstractExecutor):

    def __init__(self, node: StoragePlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        """
            Join upstream batch with current_batch.
            The upstream batch is received in case of lateral joins.
            upstream_batch = [u1, u2, u3, u4]
            current_batch = [c1, c2, c3]
            joined_batch = [c1-u1, c1-u2, c1-u3, c1-u4,
                            c2-u1, c2-u2, c2-u3, c2-u4]
        """
        for batch in StorageEngine.read(self.node.video):
            upstream_batch = kwargs.pop(UPSTREAM_BATCH, Batch())
            if not upstream_batch.empty():
                b1 = upstream_batch.frames
                b2 = batch.frames
                b1['__id'] = b2['__id'] = 0
                res = b1.merge(b2, how='outer')
                yield Batch(res)
