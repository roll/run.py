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
        tests = []
        paths = glob.glob('tests/scenarios/*.yml')
        for path in paths:
            name = os.path.splitext(os.path.basename(path))[0]
            with io.open(path, encoding='utf-8') as file:
                scenario = list(yaml.load_all(file))
                for test in scenario[1]:
                    tests.append([path, test['command'], test['output'], True])

        # Params
        params = []
        for test in tests:
            params.append(test)
        metafunc.parametrize('path, command, output, scenario', params)
