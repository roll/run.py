# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from .execution import ExecutionPlan, Command
from . import helpers


# Module API

class Task(object):

    # Public

    def __init__(self, descriptor, parent=None, parent_type=None):
        name, code = list(descriptor.items())[0]

        # Optional
        optional = False
        if name.startswith('/'):
            name = name[1:]
            optional = True

        # Name/type/childs
        childs = []
        type = 'directive'
        if name.isupper():
            type = 'variable'
        elif isinstance(code, list):
            type = 'sequence'
            if parent_type in ['parallel', 'multiplex']:
                type = parent_type
            if name.startswith('(') and name.endswith(')'):
                name = name[1:-1]
                type = 'parallel'
            if name.startswith('(') and name.endswith(')'):
                name = name[1:-1]
                type = 'multiplex'
            for index, descriptor in enumerate(code):
                number = index + 1
                if not isinstance(descriptor, dict):
                    descriptor = {str(number): descriptor}
                descriptor = Task(descriptor, parent=self, parent_type=type)
                childs.append(descriptor)
            code = None

        # Set attributes
        self._name = name
        self._code = code
        self._type = type
        self._parent = parent
        self._childs = childs
        self._optional = optional

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code

    @property
    def type(self):
        return self._type

    @property
    def parent(self):
        return self._parent

    @property
    def childs(self):
        return self._childs

    @property
    def optional(self):
        return self._optional

    @property
    def composite(self):
        return bool(self._childs)

    @property
    def executable(self):
        return bool(self._parent)

    @property
    def parents(self):
        parents = []
        task = self
        while True:
            if not task.parent:
                break
            parents.append(task.parent)
            task = task.parent
        return list(reversed(parents))

    @property
    def qualified_name(self):
        names = []
        for parent in (self.parents + [self]):
            names.append(parent.name)
        return ' '.join(names)

    @property
    def flatten_setup_tasks(self):
        tasks = []
        for parent in self.parents:
            # TODO: skip vars below
            for task in parent.childs:
                if task.type == 'variable':
                    tasks.append(task)
        return tasks

    @property
    def flatten_general_tasks(self):
        tasks = []
        for task in self.childs or [self]:
            if task.composite:
                tasks.extend(task.flatten_general_tasks)
                continue
            tasks.append(task)
        return tasks

    def run(self, argv, help=False):
        commands = []

        # Help requested
        if len(argv) > 0:
            if argv[-1] == '?':
                argv.pop()
                help = True

        # Delegate
        if len(argv) > 0:
            for task in self.childs:
                if task.name == argv[0]:
                    return task.run(argv[1:], help=help)

        # Not executable task
        if not self.executable:
            if len(argv) > 0:
                message = 'Task "%s" not found' % argv[0]
                helpers.print_message('general', message=message)
                exit(1)
            for task in self.childs:
                if task.type != 'variable':
                    helpers.print_message('general', message=task.qualified_name)
            return True

        # Collect setup commands
        for task in self.flatten_setup_tasks:
            command = Command(task.qualified_name, task.code, variable=task.name)
            commands.append(command)

        # Collect general commands
        for task in self.flatten_general_tasks:
            if not task.optional:
                variable = task.name if task.type == 'variable' else None
                command = Command(task.qualified_name, task.code, variable=variable)
                commands.append(command)

        # Normalize arguments
        arguments_index = None
        for index, command in enumerate(commands):
            if '$ARGUMENTS' in command.code:
                if not command.variable:
                    arguments_index = index
                    continue
            if arguments_index is not None:
                command.code = command.code.replace('$ARGUMENTS', '')

        # Provide arguments
        if arguments_index is None:
            for index, command in enumerate(commands):
                if not command.variable:
                    command.code = '%s $ARGUMENTS' % command.code
                    break

        # Create plan
        execution_plan = ExecutionPlan(commands, self.type)

        # Show help
        if help:
            helpers.print_message('general', message=self.qualified_name)
            if self.composite:
                helpers.print_message('general', message='---')
                for task in self.childs:
                    message = task.qualified_name
                    if task.optional:
                        message += ' (optional)'
                    helpers.print_message('general', message=message)
            helpers.print_message('general', message='---')
            print(execution_plan.explain())
            exit()

        # Execute commands
        os.environ['ARGUMENTS'] = ' '.join(argv)
        execution_plan.execute()

        return True
