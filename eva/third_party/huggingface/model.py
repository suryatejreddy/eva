# coding=utf-8
# Copyright 2018-2023 EVA
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
from typing import Any

import decord
import numpy as np
from PIL import Image

from eva.udfs.abstract.hf_abstract_udf import AbstractHFUdf
from eva.utils.generic_utils import EVAEnum


class HFInputTypes(EVAEnum):
    TEXT  # noqa: F821
    IMAGE  # noqa: F821
    AUDIO  # noqa: F821
    VIDEO  # noqa: F821
    MULTIMODAL_TEXT_IMAGE  # noqa: F821


class TextHFModel(AbstractHFUdf):
    """
    Base Model for all HF Models that take in text as input
    """

    def input_formatter(self, inputs: Any):
        return inputs.values.flatten().tolist()


class ImageHFModel(AbstractHFUdf):
    """
    Base Model for all HF Models that take in images as input
    """

    def input_formatter(self, inputs: Any):
        frames_list = inputs.values.tolist()
        frames = np.vstack(frames_list)
        images = [Image.fromarray(row) for row in frames]
        return images


class AudioHFModel(AbstractHFUdf):
    """
    Base Model for all HF Models that take in audio as input
    """

    def input_formatter(self, inputs: Any):
        # if audio is being passed using decord reader, we already have the audio as numpy arrays,
        # merge into single array and return
        if inputs.columns.str.contains("audio").any():
            return np.concatenate(inputs.iloc[:, 0].values)
        # else expect that the user passed an array of video file paths, get audio as numpy array
        audio = []
        files = inputs.iloc[:, 0].tolist()
        for file in files:
            # must read audio at 16000Hz because most models were trained at this sampling rate
            reader = decord.AudioReader(file, mono=True, sample_rate=16000)
            audio.append(reader[0:].asnumpy()[0])
        return audio


class ASRHFModel(AudioHFModel):
    """
    Specific model for Automatic Speech Recognition that extends AudioHFModel
    """

    @property
    def default_pipeline_args(self) -> dict:
        # https://huggingface.co/blog/asr-chunking
        return {
            "chunk_length_s": 30,
        }

    def output_formatter(self, outputs: Any):
        # If the model is run with return_timestamps=True, the data is stored in a key called "chunks"
        if "chunks" in outputs:
            return super().output_formatter(outputs["chunks"])
        return super().output_formatter(outputs)
