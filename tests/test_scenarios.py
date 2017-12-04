# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import subprocess


# Tests

def test_scenario_tests(path, command, output, scenario):
    code = '%s ! --run-path %s' % (command.replace('run', 'python -m run.cli'), path)
    actual = subprocess.check_output(code, shell=True).decode()
    assert actual == output
