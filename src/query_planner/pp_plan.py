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
from src.expression.abstract_expression import AbstractExpression
from src.query_planner.abstract_scan_plan import AbstractScan
from src.query_planner.types import PlanNodeType


class PPScanPlan(AbstractScan):
    """
    This plan is used for storing information required for probabilistic
    predicate.

    Arguments:
        predicate (AbstractExpression): A predicate expression used for
        filtering frames
    """

    def __init__(self, predicate: AbstractExpression):
        super().__init__(PlanNodeType.PP_FILTER_TYPE, predicate)
