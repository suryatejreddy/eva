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

from mock import MagicMock
from eva.optimizer.cost_model import CostModel

from eva.optimizer.optimizer_tasks import (
    TopDownRewrite, BottomUpRewrite, OptimizeGroup)
from eva.optimizer.optimizer_context import OptimizerContext
from eva.optimizer.operators import (
    LogicalGet, LogicalFilter, LogicalProject, LogicalQueryDerivedGet)
from eva.optimizer.property import PropertyType
from eva.optimizer.rules.rules import RulesManager
from eva.planner.seq_scan_plan import SeqScanPlan


class TestOptimizerTask(unittest.TestCase):
    def execute_task_stack(self, task_stack):
        while not task_stack.empty():
            task = task_stack.pop()
            task.execute()

    def top_down_rewrite(self, opr):
        opt_cxt = OptimizerContext(CostModel())
        grp_expr = opt_cxt.add_opr_to_group(
            opr
        )
        root_grp_id = grp_expr.group_id
        opt_cxt.task_stack.push(TopDownRewrite(
            grp_expr, RulesManager().rewrite_rules, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def bottom_up_rewrite(self, root_grp_id, opt_cxt):
        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]
        opt_cxt.task_stack.push(BottomUpRewrite(
            grp_expr, RulesManager().rewrite_rules, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def implement_group(self, root_grp_id, opt_cxt):
        grp = opt_cxt.memo.groups[root_grp_id]
        opt_cxt.task_stack.push(OptimizeGroup(grp, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def test_simple_top_down_rewrite(self):
        predicate = MagicMock()
        child_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        root_opr = LogicalFilter(predicate, [child_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_opr)

        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]

        self.assertEqual(type(grp_expr.opr), LogicalGet)
        self.assertEqual(grp_expr.opr.predicate, predicate)
        self.assertEqual(grp_expr.opr.children, [])

    def test_nested_top_down_rewrite(self):
        child_predicate = MagicMock()
        root_predicate = MagicMock()

        child_get_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        child_filter_opr = LogicalFilter(child_predicate, [child_get_opr])
        child_project_opr = LogicalProject([MagicMock()], [child_filter_opr])
        root_derived_get_opr = LogicalQueryDerivedGet(
            MagicMock(), children=[child_project_opr])
        root_filter_opr = LogicalFilter(root_predicate, [root_derived_get_opr])
        root_project_opr = LogicalProject([MagicMock()], [root_filter_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)

        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]

        self.assertEqual(type(grp_expr.opr), LogicalProject)
        self.assertEqual(len(grp_expr.children), 1)

        child_grp_id = grp_expr.children[0]
        child_expr = opt_cxt.memo.groups[child_grp_id].logical_exprs[0]
        self.assertEqual(type(child_expr.opr), LogicalQueryDerivedGet)
        self.assertEqual(child_expr.opr.predicate, root_predicate)
        self.assertEqual(len(child_expr.children), 1)

        child_grp_id = child_expr.children[0]
        child_expr = opt_cxt.memo.groups[child_grp_id].logical_exprs[0]
        self.assertEqual(type(child_expr.opr), LogicalGet)
        self.assertEqual(child_expr.opr.predicate, child_predicate)

    def test_nested_bottom_up_rewrite(self):
        child_predicate = MagicMock()
        root_predicate = MagicMock()

        child_get_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        child_filter_opr = LogicalFilter(child_predicate, [child_get_opr])
        child_project_opr = LogicalProject([MagicMock()], [child_filter_opr])
        root_derived_get_opr = LogicalQueryDerivedGet(
            MagicMock(), children=[child_project_opr])
        root_filter_opr = LogicalFilter(root_predicate, [root_derived_get_opr])
        root_project_opr = LogicalProject([MagicMock()],
                                          children=[root_filter_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)
        opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)

        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]

        self.assertEqual(type(grp_expr.opr), LogicalQueryDerivedGet)
        self.assertEqual(len(grp_expr.children), 1)
        self.assertEqual(grp_expr.opr.predicate, root_predicate)

        child_grp_id = grp_expr.children[0]
        child_expr = opt_cxt.memo.groups[child_grp_id].logical_exprs[0]
        self.assertEqual(type(child_expr.opr), LogicalGet)
        self.assertEqual(child_expr.opr.predicate, child_predicate)

    def test_simple_implementation(self):
        predicate = MagicMock()
        child_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        root_opr = LogicalFilter(predicate, [child_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_opr)
        opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)
        opt_cxt, root_grp_id = self.implement_group(root_grp_id, opt_cxt)

        root_grp = opt_cxt.memo.groups[root_grp_id]
        best_root_grp_expr = root_grp.get_best_expr(PropertyType.DEFAULT)

        self.assertEqual(type(best_root_grp_expr.opr), SeqScanPlan)
        self.assertEqual(best_root_grp_expr.opr.predicate, predicate)

    def test_nested_implementation(self):
        child_predicate = MagicMock()
        root_predicate = MagicMock()

        child_get_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        child_filter_opr = LogicalFilter(
            child_predicate, children=[child_get_opr])
        child_project_opr = LogicalProject(
            [MagicMock()], children=[child_filter_opr])
        root_derived_get_opr = LogicalQueryDerivedGet(
            MagicMock(), children=[child_project_opr])
        root_filter_opr = LogicalFilter(
            root_predicate, children=[root_derived_get_opr])
        root_project_opr = LogicalProject(
            [MagicMock()], children=[root_filter_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)
        opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)
        opt_cxt, root_grp_id = self.implement_group(root_grp_id, opt_cxt)

        root_grp = opt_cxt.memo.groups[root_grp_id]
        best_root_grp_expr = root_grp.get_best_expr(PropertyType.DEFAULT)

        root_opr = best_root_grp_expr.opr
        self.assertEqual(type(root_opr), SeqScanPlan)
        self.assertEqual(root_opr.predicate, root_predicate)

        child_grp_id = best_root_grp_expr.children[0]
        child_grp = opt_cxt.memo.groups[child_grp_id]
        best_child_grp_expr = child_grp.get_best_expr(PropertyType.DEFAULT)
        child_opr = best_child_grp_expr.opr
        self.assertEqual(type(child_opr), SeqScanPlan)
        self.assertEqual(child_opr.predicate, child_predicate)
