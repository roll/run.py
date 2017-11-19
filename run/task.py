# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import click
import select
import random
import subprocess
from . import helpers


# Module API

class Task(object):

    # Public

    def __init__(self, descriptor, parent=None, parent_type=None):
        name, contents = list(descriptor.items())[0]

        # Optional
        optional = False
        if name.startswith('/'):
            name = name[1:]
            optional = True

        # Name/type/tasks
        tasks = []
        type = 'instruction'
        if name.isupper():
            type = 'variable'
        elif isinstance(contents, list):
            type = 'sequence'
            if name == 'system':
                type = 'system'
            if parent_type in ['parallel', 'multiplex']:
                type = parent_type
            if name.startswith('(') and name.endswith(')'):
                name = name[1:-1]
                type = 'parallel'
            if name.startswith('(') and name.endswith(')'):
                name = name[1:-1]
                type = 'multiplex'
            for index, descriptor in enumerate(contents):
                number = index + 1
                if not isinstance(descriptor, dict):
                    descriptor = {str(number): descriptor}
                descriptor = Task(descriptor, parent=self, parent_type=type)
                tasks.append(descriptor)

        # Command
        command = None
        if type in ['variable', 'instruction']:
            command = contents
        elif type in ['parallel', 'multiplex']:
            command = []
            for task in tasks:
                task_command = task._command if isinstance(task._command, list) else [(task._name, task._command)]
                command.extend(task_command)

        # Set attributes
        self._name = name
        self._type = type
        self._tasks = tasks
        self._parent = parent
        self._command = command
        self._optional = optional

    def run(self, argv):

        # Delegate
        if len(argv) > 0:
            for task in self._tasks:
                if task._name == argv[0]:
                    return task.run(argv[1:])

        # Not found
        if len(argv) > 0:
            if len(self._tasks) > 1:
                message = 'Task "%s" not found' % argv[0]
                helpers.print_message('general', message=message)
                exit(1)

        # Process
        self._setup()
        self._execute(argv)

    # Internal

    def _setup(self):

        # Collect parents
        parents = []
        task = self
        while True:
            if not task._parent:
                break
            parents.append(task._parent)
            task = task._parent

        # Collect variables
        variables = []
        for parent in reversed(parents):
            for task in parent._tasks:
                if task._type == 'variable':
                    variables.append(task)

        # Execute variables
        for variable in variables:
            variable._execute()

    def _execute(self, argv=[]):

        # System
        if self._type == 'system':
            for task in self._tasks:
                if not task._type == 'variable':
                    print(task._name)

        # Variable
        elif self._type == 'variable':
            try:
                output = subprocess.check_output(self._command, shell=True)
            except subprocess.CalledProcessError:
                message = 'Command "%s" has failed' % self._command
                helpers.print_message('general', message=message)
                exit(1)
            os.environ[self._name] = output.decode('utf-8').strip()

        # Instruction
        elif self._type == 'instruction':
            command = self._command
            if '$ARGUMENTS' not in command:
                command = '%s $ARGUMENTS' % command
            if argv:
                os.environ['ARGUMENTS'] = ' '.join(argv)
            returncode = subprocess.check_call(command, shell=True)
            if returncode != 0:
                message = 'Command "%s" has failed' % self._command
                helpers.print_message('general', message=message)
                exit(1)

        # Sequence
        elif self._type == 'sequence':
            argv = argv if len(self._tasks) == 1 else []
            for task in self._tasks:
                if not task._optional:
                    task._execute(argv)

        # Parallel
        elif self._type == 'parallel':
            processes = []
            for name, command in self._command:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                processes.append(process)
            for process in processes:
                output, errput = process.communicate()
                sys.stdout.write(output.decode('utf-8'))
                if process.returncode != 0:
                    message = 'Command "%s" has failed' % process.args
                    helpers.print_message('general', message=message)
                    exit(1)

        # Multiplex
        elif self._type == 'multiplex':
            processes = []
            for name, command in self._command:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                poll = select.poll()
                processes.append((name, process, poll, random.choice(['red', 'green'])))
                poll.register(process.stdout, select.POLLIN)
            while True:
                if not processes:
                    break
                for index, (name, process, poll, color) in list(enumerate(processes)):
                    if poll.poll(1):
                        line = process.stdout.readline().decode('utf-8')
                        text = click.style('%s: %s' % (name, line), fg=color)
                        click.echo(text, nl=False)
                    if process.poll() is not None:
                        processes.pop(index)
                        if process.returncode != 0:
                            message = 'Command "%s" has failed' % process.args
                            helpers.print_message('general', message=message)
                            exit(1)
