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
from time import perf_counter

from gpt4all import GPT4All
from unidecode import unidecode
from util import download_story, read_text_line, try_execute

import evadb


def ask_question(path):
    # Initialize early to exclude download time.
    llm = GPT4All("ggml-gpt4all-j-v1.3-groovy")

    cursor = evadb.connect().cursor()

    story_table = "TablePPText"
    story_feat_table = "FeatTablePPText"
    index_table = "IndexTable"

    timestamps = {}
    t_i = 0

    timestamps[t_i] = perf_counter()
    print("Setup UDF")

    Text_feat_udf_query = """CREATE UDF IF NOT EXISTS SentenceFeatureExtractor
            IMPL  'evadb/udfs/sentence_feature_extractor.py';
            """

    cursor.query("DROP UDF IF EXISTS SentenceFeatureExtractor;").execute()
    cursor.query(Text_feat_udf_query).execute()

    try_execute(cursor, f"DROP TABLE IF EXISTS {story_table};")
    try_execute(cursor, f"DROP TABLE IF EXISTS {story_feat_table};")

    t_i = t_i + 1
    timestamps[t_i] = perf_counter()
    print(f"Time: {(timestamps[t_i] - timestamps[t_i - 1]) * 1000:.3f} ms")

    print("Create table")

    cursor.query(f"CREATE TABLE {story_table} (id INTEGER, data TEXT(1000));").execute()

    # Insert text chunk by chunk.
    for i, text in enumerate(read_text_line(path)):
        print("text: --" + text + "--")
        ascii_text = unidecode(text)
        cursor.query(
            f"""INSERT INTO {story_table} (id, data)
                VALUES ({i}, '{ascii_text}');"""
        ).execute()

    t_i = t_i + 1
    timestamps[t_i] = perf_counter()
    print(f"Time: {(timestamps[t_i] - timestamps[t_i - 1]) * 1000:.3f} ms")

    print("Extract features")

    # Extract features from text.
    cursor.query(
        f"""CREATE TABLE {story_feat_table} AS
        SELECT SentenceFeatureExtractor(data), data FROM {story_table};"""
    ).execute()

    t_i = t_i + 1
    timestamps[t_i] = perf_counter()
    print(f"Time: {(timestamps[t_i] - timestamps[t_i - 1]) * 1000:.3f} ms")

    print("Create index")

    # Create search index on extracted features.
    cursor.query(
        f"CREATE INDEX {index_table} ON {story_feat_table} (features) USING FAISS;"
    ).execute()

    t_i = t_i + 1
    timestamps[t_i] = perf_counter()
    print(f"Time: {(timestamps[t_i] - timestamps[t_i - 1]) * 1000:.3f} ms")

    print("Query")

    # Search similar text as the asked question.
    question = "Who is Cyril Vladmirovich?"
    ascii_question = unidecode(question)

    res_batch = cursor.query(
        f"""SELECT data FROM {story_feat_table}
        ORDER BY Similarity(SentenceFeatureExtractor('{ascii_question}'),features)
        LIMIT 5;"""
    ).execute()

    t_i = t_i + 1
    timestamps[t_i] = perf_counter()
    print(f"Time: {(timestamps[t_i] - timestamps[t_i - 1]) * 1000:.3f} ms")

    print("Merge")

    # Merge all context information.
    context_list = []
    for i in range(len(res_batch)):
        context_list.append(res_batch.frames[f"{story_feat_table.lower()}.data"][i])
    context = "; \n".join(context_list)

    t_i = t_i + 1
    timestamps[t_i] = perf_counter()
    print(f"Time: {(timestamps[t_i] - timestamps[t_i - 1]) * 1000:.3f} ms")

    print("LLM")

    # LLM
    messages = [
        {"role": "user", "content": f"Here is some context:{context}"},
        {
            "role": "user",
            "content": f"Answer this question based on context: {question}",
        },
    ]
    llm.chat_completion(messages)

    t_i = t_i + 1
    timestamps[t_i] = perf_counter()
    print(f"Time: {(timestamps[t_i] - timestamps[t_i - 1]) * 1000:.3f} ms")

    print(f"Total Time: {(timestamps[t_i] - timestamps[0]) * 1000:.3f} ms")


def main():
    path = download_story()

    ask_question(path)


if __name__ == "__main__":
    main()
