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
from src.planner.nested_loop_join_plan import NestedLoopJoin


class NestedLoopJoinExecutor(AbstractExecutor):
    """
    Nested Loop Join executor:
    Returns the tuple joined from inner and outer tuples which
    satisfies the predicate clause.
    It scans the inner relation to join with current outer tuple.

    Arguments:
        node (AbstractPlan): The NestedLoopJoin

    """

    def __init__(self, node: NestedLoopJoin):
        super().__init__(node)
        self.predicate = node.join_predicate
        self.join_type = node.join_type

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:

        outer = self.children[0]
        inner = self.children[1]

        for outer_batch in outer.exec(*args, **kwargs):
            # grab the values from the outer tuple that are required to be
            # passed to the inner tuple
            # we are passing the entire output batch to the inner tree,
            # ideally pass only the cols required

            kwargs[UPSTREAM_BATCH] = outer_batch
            for inner_batch in inner.exec(*args, **kwargs):
                if not self.predicate:
                    yield inner_batch
                else:
                    # check if the tuples qualify
                    # TODO: write logic to apply join predicate
                    yield inner_batch
