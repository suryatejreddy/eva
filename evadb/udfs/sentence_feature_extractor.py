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
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe
from evadb.udfs.gpu_compatible import GPUCompatible


class SentenceTransformerFeatureExtractor(AbstractUDF, GPUCompatible):
    @setup(cacheable=False, udf_type="FeatureExtraction", batchable=False)
    def setup(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def to_device(self, device: str) -> GPUCompatible:
        self.model = self.model.to(device)
        return self

    @property
    def name(self) -> str:
        return "SentenceTransformerFeatureExtractor"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.STR],
                column_shapes=[(1)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["features"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(1, 384)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        def _forward(row: pd.Series) -> np.ndarray:
            data = row
            embedded_list = self.model.encode(data)
            return embedded_list

        ret = pd.DataFrame()
        ret["features"] = df.apply(_forward, axis=1)
        return ret
