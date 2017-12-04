# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import operator
import datetime
import subprocess
from itertools import zip_longest


# Tests

def test_scenario_tests(config_path, scenario):

    # Prepare command
    command = scenario['command']
    command = command.replace('run', 'python -m run.cli')
    command = '%s --run-path %s' % (command, config_path)

    # Execute command
    start = datetime.datetime.now()
    output = subprocess.check_output(command, shell=True).decode()
    stop = datetime.datetime.now()
    time = round((stop - start).total_seconds(), 3)
    print(output)

    # Assert result
    predicat = getattr(operator, scenario.get('operator', 'eq'))
    assert predicat(output, scenario['output'])
    assert time <= scenario.get('faster', time)
