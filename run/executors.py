# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import click
import select
import random
import subprocess
from . import helpers


# Module API

def execute_variable(command, silent=False):

    # Execute process
    try:
        output = subprocess.check_output(command.code, shell=True)
    except subprocess.CalledProcessError:
        message = 'Command "%s" has failed' % command.code
        helpers.print_message('general', message=message)
        exit(1)
    return output.decode().strip()


def execute_directive(command, silent=False):

    # Execute process
    if not silent:
        print('[run] Launched "%s"' % command.code)
    returncode = subprocess.check_call(command.code, shell=True)
    if returncode != 0:
        message = 'Command "%s" has failed' % command.code
        helpers.print_message('general', message=message)
        exit(1)


def execute_sequence(commands, silent=False):

    # Execute process
    for command in commands:
        if command.variable:
            execute_variable(command, silent=silent)
            continue
        execute_directive(command, silent=silent)


def execute_parallel(commands, silent=False):

    # Start processes
    processes = []
    for command in commands:
        if not silent:
            print('[run] Launched "%s"' % command.code)
        code = _wrap_command_code(command.code)
        process = subprocess.Popen(
            code, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append((command, process))

    # Wait processes
    for command, process in processes:
        output, errput = process.communicate()
        _print_bytes(output)
        _print_bytes(errput, stream=sys.stderr)
        if process.returncode != 0:
            message = 'Command "%s" has failed' % command.code
            helpers.print_message('general', message=message)
            exit(1)


def execute_multiplex(commands, silent=False):

    # Start processes
    processes = []
    for command in commands:
        if not silent:
            print('[run] Launched "%s"' % command.code)
        code = _wrap_command_code(command.code)
        process = subprocess.Popen(
            code, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        poll = select.poll()
        processes.append((command, poll, random.choice(['red', 'green'])))
        poll.register(process.stdout, select.POLLIN)

    # Wait processes
    while True:
        if not processes:
            break
        for index, (command, poll, color) in list(enumerate(processes)):
            if poll.poll(1):
                line = process.stdout.readline()
                click.echo(click.style('%s: ' % command.name, fg=color), nl=False)
                _print_bytes(line)
            if process.poll() is not None:
                processes.pop(index)
                if process.returncode != 0:
                    message = 'Command "%s" has failed' % command.code
                    helpers.print_message('general', message=message)
                    exit(1)


# Internal

def _wrap_command_code(command):
    return 'script -qefc "%s" /dev/null' % command


def _print_bytes(bytes, stream=sys.stdout):
    buffer = getattr(stream, 'buffer', stream)
    buffer.write(bytes)
    stream.flush()
