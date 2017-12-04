# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os
import glob
import yaml
import pytest


def pytest_generate_tests(metafunc):
    if 'scenario' in metafunc.fixturenames:

        # Tests
        scenarios = []
        config_paths = glob.glob('tests/scenarios/*.yml')
        for config_path in config_paths:
            with io.open(config_path, encoding='utf-8') as file:
                documents = list(yaml.load_all(file))
                for scenario in documents[2] or []:
                    scenarios.append([config_path, scenario])

        # Params
        params = []
        for scenario in scenarios:
            params.append(scenario)
        metafunc.parametrize('config_path, scenario', params)
