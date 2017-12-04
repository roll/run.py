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
    argv = sys.argv[1:]

    # Path
    path = 'run.yml'
    if '--run-path' in argv:
        index = argv.index('--run-path')
        path = argv.pop(index + 1)
        argv.pop(index)

    # Complete
    complete = False
    if '--run-complete' in argv:
        argv.remove('--run-complete')
        complete = True

    # Prepare
    config, options = helpers.read_config(path)
    task = Task(config, options=options)

    # Run
    if complete:
        task.complete(argv)
        exit()
    task.run(argv)
