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

        # Prepare
        desc = None
        name, code = list(descriptor.items())[0]
        if isinstance(code, dict):
            desc = code['desc']
            code = code['code']
        self._parent = parent
        if not parent:
            desc = 'General run description'

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
                if len(self.parents) >= 2:
                    message = 'Subtask descriptions and execution control not supported'
                    helpers.print_message('general', message=message)
                    exit(1)
                name = name[1:-1]
                type = 'parallel'
            if name.startswith('(') and name.endswith(')'):
                name = name[1:-1]
                type = 'multiplex'
            for descriptor in code:
                if not isinstance(descriptor, dict):
                    descriptor = {'': descriptor}
                child = Task(descriptor, parent=self, parent_type=type)
                childs.append(child)
            code = None

        # Set attributes
        self._name = name
        self._code = code
        self._type = type
        self._desc = desc
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
    def desc(self):
        return self._desc

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
    def is_root(self):
        return bool(not self._parent)

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
            if parent.name:
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

    @property
    def flatten_childs_with_composite(self):
        tasks = []
        for task in self.childs:
            tasks.append(task)
            if task.composite:
                tasks.extend(task.flatten_childs_with_composite)
        return tasks

    def find_child_tasks(self, name):
        tasks = []
        for task in self.flatten_general_tasks:
            if task.name == name:
                tasks.append(task)
        return tasks

    def run(self, argv):
        commands = []

        # Delegate
        if len(argv) > 0:
            for task in self.childs:
                if task.name == argv[0]:
                    return task.run(argv[1:])

        # Bad task
        if self.is_root and len(argv) > 0:
            message = 'Task "%s" not found' % self.name
            helpers.print_message('general', message=message)
            exit(1)

        # Root task
        if self.is_root:
            _print_help(self, self)
            return True

        # Prepare filters
        filters = {'pick': [], 'enable': [], 'disable': []}
        for name, prefix in [['pick', '='], ['enable', '+'], ['disable', '-']]:
            for arg in list(argv):
                if arg.startswith(prefix):
                    childs = self.find_child_tasks(arg[1:])
                    if childs:
                        filters[name].extend(childs)
                        argv.remove(arg)

        # Detect help
        help = False
        if argv == ['?']:
            argv.pop()
            help = True

        # Collect setup commands
        for task in self.flatten_setup_tasks:
            command = Command(task.qualified_name, task.code, variable=task.name)
            commands.append(command)

        # Collect general commands
        for task in self.flatten_general_tasks:
            if task not in filters['pick']:
                if task.optional and task not in filters['enable']:
                    continue
                if task in filters['disable']:
                    continue
                if filters['pick']:
                    continue
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
            task = self if len(self.parents) < 2 else self.parents[1]
            selected_task = self
            _print_help(task, selected_task, execution_plan, filters)
            exit()

        # Execute commands
        os.environ['ARGUMENTS'] = ' '.join(argv)
        execution_plan.execute()

        return True


# Internal

def _print_help(task, selected_task, execution_plan=None, filters=None):
    helpers.print_message('general', message=task.qualified_name)
    helpers.print_message('general', message='\n---')
    if task.desc:
        helpers.print_message('general', message='\nDescription\n')
        print(task.desc)
    if task.composite:
        helpers.print_message('general', message='\nCommands\n')
        for child in [task] + task.flatten_childs_with_composite:
            if not child.name:
                continue
            if child.type == 'variable':
                continue
            message = child.qualified_name
            if child.optional:
                message += ' (optional)'
            if child in filters['pick']:
                message += ' (picked)'
            if child in filters['enable']:
                message += ' (enabled)'
            if child in filters['disable']:
                message += ' (disabled)'
            if child is selected_task:
                message += ' (selected)'
                helpers.print_message('general', message=message)
            else:
                print(message)
    if execution_plan:
        helpers.print_message('general', message='\nExecution Plan\n')
        print(execution_plan.explain())
