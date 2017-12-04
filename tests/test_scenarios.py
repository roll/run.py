# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import subprocess


# Tests

def test_scenario_tests(config_path, scenario):
    command = scenario['command']
    command = command.replace('run', 'python -m run.cli')
    command = '%s --run-path %s' % (command, config_path)
    actual = subprocess.check_output(command, shell=True).decode()
    assert actual == scenario['output']
