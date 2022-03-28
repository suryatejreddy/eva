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

from eva.parser.statement import AbstractStatement
from eva.expression.abstract_expression import AbstractExpression
from eva.parser.types import StatementType
from eva.parser.table_ref import TableRef
from pathlib import Path
from typing import List


class LoadDataStatement(AbstractStatement):
    """
    Load Data Statement constructed after parsing the input query

    Arguments:
    table (TableRef): table reference to load into
    path (str): path from where data needs to be loaded
    """

    def __init__(self, 
                 table: TableRef,
                 path: str,
                 column_list: List[AbstractExpression] = None,
                 file_options: dict = None):
        super().__init__(StatementType.LOAD_DATA)
        self._table = table
        self._path = Path(path)
        self._column_list = column_list
        self._file_options = file_options

    def __str__(self) -> str:
        print_str = "LOAD DATA INFILE {} INTO {}({})".format(
            self._path.name, self._table, self._column_list)
        return print_str

    @property
    def table(self) -> TableRef:
        return self._table

    @property
    def path(self) -> Path:
        return self._path

    @property
    def column_list(self) -> List[AbstractExpression]:
        return self._column_list

    @property
    def file_options(self) -> dict:
        return self._file_options

    def __eq__(self, other):
        if not isinstance(other, LoadDataStatement):
            return False
        return (self.table == other.table
                and self.path == other.path
                and self.column_list == other.column_list
                and self.file_options == other.file_options)
