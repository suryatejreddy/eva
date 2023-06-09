# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from lark import Token, Tree

from evadb.expression.abstract_expression import ExpressionType
from evadb.expression.aggregation_expression import AggregationExpression
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.create_udf_statement import CreateUDFStatement


##################################################################
# Functions - UDFs, Aggregate Windowed functions
##################################################################
class Functions:
    def udf_function(self, tree):
        udf_name = None
        udf_output = None
        udf_args = None

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "simple_id":
                    udf_name = self.visit(child)
                elif child.data == "dotted_id":
                    udf_output = self.visit(child)
                elif child.data == "function_args":
                    udf_args = self.visit(child)

        func_expr = FunctionExpression(None, name=udf_name, output=udf_output)
        for arg in udf_args:
            func_expr.append_child(arg)

        return func_expr

    def function_args(self, tree):
        args = []
        for child in tree.children:
            if isinstance(child, Tree):
                args.append(self.visit(child))
        return args

    # Create UDF
    def create_udf(self, tree):
        udf_name = None
        if_not_exists = False
        input_definitions = []
        output_definitions = []
        impl_path = None
        udf_type = None
        metadata = []

        create_definitions_index = 0
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "udf_name":
                    udf_name = self.visit(child)
                elif child.data == "if_not_exists":
                    if_not_exists = True
                elif child.data == "create_definitions":
                    # There should be 2 createDefinition
                    # idx 0 describing udf INPUT
                    # idx 1 describing udf OUTPUT
                    if create_definitions_index == 0:
                        input_definitions = self.visit(child)
                        create_definitions_index += 1
                    elif create_definitions_index == 1:
                        output_definitions = self.visit(child)
                elif child.data == "udf_type":
                    udf_type = self.visit(child)
                elif child.data == "udf_impl":
                    impl_path = self.visit(child).value
                elif child.data == "udf_metadata":
                    # Each UDF metadata is a key value pair
                    key_value_pair = self.visit(child)
                    # value can be an integer or string
                    value = key_value_pair[1]
                    if isinstance(value, ConstantValueExpression):
                        value = value.value
                    metadata.append((key_value_pair[0].value, value)),

        return CreateUDFStatement(
            udf_name,
            if_not_exists,
            impl_path,
            input_definitions,
            output_definitions,
            udf_type,
            metadata,
        )

    def get_aggregate_function_type(self, agg_func_name):
        agg_func_type = None
        if agg_func_name == "COUNT":
            agg_func_type = ExpressionType.AGGREGATION_COUNT
        elif agg_func_name == "MIN":
            agg_func_type = ExpressionType.AGGREGATION_MIN
        elif agg_func_name == "MAX":
            agg_func_type = ExpressionType.AGGREGATION_MAX
        elif agg_func_name == "SUM":
            agg_func_type = ExpressionType.AGGREGATION_SUM
        elif agg_func_name == "AVG":
            agg_func_type = ExpressionType.AGGREGATION_AVG
        elif agg_func_name == "FIRST":
            agg_func_type = ExpressionType.AGGREGATION_FIRST
        elif agg_func_name == "LAST":
            agg_func_type = ExpressionType.AGGREGATION_LAST
        elif agg_func_name == "SEGMENT":
            agg_func_type = ExpressionType.AGGREGATION_SEGMENT
        return agg_func_type

    def aggregate_windowed_function(self, tree):
        agg_func_arg = None
        agg_func_name = None

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "function_arg":
                    agg_func_arg = self.visit(child)
                elif child.data == "aggregate_function_name":
                    agg_func_name = self.visit(child).value
            elif isinstance(child, Token):
                token = child.value
                # Support for COUNT(*)
                if token != "*":
                    agg_func_name = token
                else:
                    agg_func_arg = TupleValueExpression(col_name="id")

        agg_func_type = self.get_aggregate_function_type(agg_func_name)
        agg_expr = AggregationExpression(agg_func_type, None, agg_func_arg)
        return agg_expr
