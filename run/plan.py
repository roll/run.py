# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import datetime
from copy import copy
from . import executors


# Module API

class Plan(object):

    # Public

    def __init__(self, commands, mode):
        self._commands = commands
        self._mode = mode

    def explain(self):

        # Explain
        lines = []
        plain = True
        for command in self._commands:
            if self._mode in ['sequence', 'parallel', 'multiplex']:
                if not command.variable:
                    if plain:
                        lines.append('[%s]' % self._mode.upper())
                    plain = False
            code = command.code
            if command.variable:
                code = '%s="%s"' % (command.variable, command.code)
            lines.append('%s$ %s' % (' '*(0 if plain else 4), code))

        return '\n'.join(lines)

    def execute(self, argv, quiet=False, faketty=False):
        commands = copy(self._commands)

        # Variables
        varnames = []
        variables = []
        for command in copy(commands):
            if command.variable:
                variables.append(command)
                varnames.append(command.variable)
                commands.remove(command)
        executors.execute_sync(variables,
            environ=os.environ, quiet=quiet)
        if not commands:
            print(os.environ[varnames[-1]])
            return

        # Update environ
        os.environ['RUNARGS'] = ' '.join(argv)
        runvars = os.environ.get('RUNVARS')
        if runvars:
            import dotenv
            dotenv.load_dotenv(runvars)

        # Log prepared
        if not quiet:
            items = []
            start = datetime.datetime.now()
            for name in varnames + ['RUNARGS']:
                items.append('%s=%s' % (name, os.environ.get(name)))
            print('[run] Prepared "%s"' % '; '.join(items))

        # Directive
        if self._mode == 'directive':
            executors.execute_sync(commands,
                environ=os.environ, quiet=quiet)

        # Sequence
        elif self._mode == 'sequence':
            executors.execute_sync(commands,
                environ=os.environ, quiet=quiet)

        # Parallel
        elif self._mode == 'parallel':
            executors.execute_async(commands,
                environ=os.environ, quiet=quiet, faketty=faketty)

        # Multiplex
        elif self._mode == 'multiplex':
            executors.execute_async(commands,
                environ=os.environ, multiplex=True, quiet=quiet, faketty=faketty)

        # Log finished
        if not quiet:
            stop = datetime.datetime.now()
            time = round((stop - start).total_seconds(), 3)
            message = '[run] Finished in %s seconds'
            print(message % time)
