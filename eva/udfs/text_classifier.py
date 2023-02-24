# coding=utf-8
# Copyright 2018-2022 EVA
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
from typing import List

import pandas as pd

from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF

try:
    from transformers import pipeline
except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install detoxify`"
    )


class TextClassifier(AbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "TextClassifier"

    def setup(self, threshold=0.2):
        self.model = pipeline(task="sentiment-analysis")

    @property
    def input_format(self) -> str:
        return str

    @property
    def labels(self) -> List[str]:
        return super().labels

    def forward(self, text_dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Performs predictions on input text
        Arguments:
            text (pd.DataFrame): Dataframe with text on which predictions need to be performed

            ['example text 1','example text 2']
            ['example text 3']
            ...
            ['example text 1','example text 5']

        Returns:
            outcome (List[Str])
        """
        model_input = text_dataframe.squeeze().values.tolist()
        model_output = self.model(model_input)
        final_out = pd.DataFrame.from_dict(model_output, orient="columns")
        # rename columns in final_out
        final_out.rename(columns={"label": "labels", "score": "scores"}, inplace=True)
        # reconstruct dimension of the input
        return final_out
