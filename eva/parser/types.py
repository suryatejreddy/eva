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
from enum import IntEnum, unique, Enum, auto


class ColumnConstraintEnum(IntEnum):
    NULLNOTNULL = 1
    DEFAULT = 2
    PRIMARY = 3
    UNIQUE = 4


@unique
class StatementType(IntEnum):
    """
    Manages enums for all the sql-like statements supported
    """
    SELECT = 1,
    CREATE = 2,
    INSERT = 3,
    CREATE_UDF = 4,
    LOAD_DATA = 5,
    UPLOAD = 6,
    CREATE_MATERIALIZED_VIEW = 7,
    # add other types


@unique
class ParserOrderBySortType(Enum):
    """
    Manages enums for all order by sort types
    """
    ASC = auto()
    DESC = auto()


@unique
class JoinType(Enum):
    LATERAL_JOIN = auto()
    HASH_JOIN = auto()
    ASC = 1
    DESC = 2


@unique
class FileFormatType(Enum):
    """
    Manages enums for all order by sort types
    """
    VIDEO = auto()
    CSV = auto()
