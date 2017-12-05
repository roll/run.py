# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from .task import Task
from . import helpers


# Main program

if __name__ == '__main__':

    # Arguments
    argv = sys.argv[1:]

    # Path argument
    path = 'run.yml'
    if '--run-path' in argv:
        index = argv.index('--run-path')
        path = argv.pop(index + 1)
        argv.pop(index)

    # Complete argument
    complete = False
    if '--run-complete' in argv:
        argv.remove('--run-complete')
        complete = True

    # Prepare
    config, options = helpers.read_config(path)
    task = Task(config, options=options)

    # Complete
    if complete:
        task.complete(argv)
        exit()

    # Run
    task.run(argv)
