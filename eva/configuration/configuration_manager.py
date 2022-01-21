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

import os
import importlib.resources as importlib_resources
import yaml
from pathlib import Path

from eva.configuration.dictionary import EVA_INSTALLATION_DIR, \
    EVA_DEFAULT_DIR, EVA_DATASET_DIR, DB_DEFAULT_URI


class ConfigurationManager(object):
    _instance = None
    _cfg = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)

            ymlpath = None
            if importlib_resources.is_resource('eva', 'eva.yml'):
                with importlib_resources.path('eva', 'eva.yml')as path:
                    ymlpath = path
            else:  # For local dev environments without package installed
                ymlpath = os.path.join(EVA_INSTALLATION_DIR, "eva.yml")

            with open(ymlpath, 'r') as ymlfile:
                cls._cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

            dataset_location = cls._instance.get_value("core", "location")
            database_uri = cls._instance.get_value("core",
                                                   "sqlalchemy_database_uri")
            if not dataset_location or not database_uri:
                # create directory if doesn't exist
                Path(EVA_DEFAULT_DIR).mkdir(parents=True, exist_ok=True)

                if not dataset_location:
                    dataset_location = EVA_DEFAULT_DIR + EVA_DATASET_DIR
                    cls._instance.update_value("core", "location",
                                               dataset_location)
                if not database_uri:
                    database_uri = DB_DEFAULT_URI
                    cls._instance.update_value("core",
                                               "sqlalchemy_database_uri",
                                               database_uri)

                # update config on disk
                with open(ymlpath, 'w') as ymlfile:
                    ymlfile.write(yaml.dump(cls._cfg))

        return cls._instance

    def get_value(self, category, key):
        # get category information
        category_data = self._cfg.get(category, None)

        # get key information
        value = None
        if category_data is not None:
            value = category_data.get(key, None)
            return value

    def update_value(self, category, key, value):
        category_data = self._cfg.get(category, None)

        if category_data:
            category_data[key] = value