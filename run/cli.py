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
    config = helpers.read_config()
    tasks = Task(config)
    tasks.run(sys.argv[1:])
