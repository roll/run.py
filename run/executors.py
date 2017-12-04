# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import click
import shlex
import select
import subprocess
from . import helpers


# Module API

def execute_variable(command, silent=False):

    # Execute process
    try:
        output = subprocess.check_output(command.code, shell=True)
    except subprocess.CalledProcessError:
        message = '[run] Command "%s" has failed' % command.code
        helpers.print_message('general', message=message)
        exit(1)
    return output.decode().strip()


def execute_directive(command, silent=False):

    # Execute process
    if not silent:
        print('[run] Launched "%s"' % command.code)
    returncode = subprocess.check_call(command.code, shell=True)
    if returncode != 0:
        message = '[run] Command "%s" has failed' % command.code
        helpers.print_message('general', message=message)
        exit(1)


def execute_sequence(commands, silent=False):

    # Execute process
    for command in commands:
        execute_directive(command, silent=silent)


def execute_parallel(commands, silent=False):

    # Start processes
    processes = []
    for command in commands:
        if not silent:
            print('[run] Launched "%s"' % command.code)
        process = subprocess.Popen(
            _prepare_command_code(command.code),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append((command, process))

    # Wait processes
    while processes:
        for index, (command, process) in enumerate(processes):
            try:
                output, errput = process.communicate(timeout=1000)
            except subprocess.TimeoutExpired:
                continue
            if process.returncode != 0:
                message = '[run] Command "%s" has failed' % command.code
                helpers.print_message('general', message=message)
            _print_bytes(output)
            _print_bytes(errput, stream=sys.stderr)
            if process.returncode != 0:
                for command, process in processes:
                    process.kill()
                exit(1)
            processes.pop(index)
            break


def execute_multiplex(commands, silent=False):

    # Launch processes
    processes = []
    color_iterator = helpers.iter_colors()
    for command in commands:
        if not silent:
            print('[run] Launched "%s"' % command.code)
        color = next(color_iterator)
        process = subprocess.Popen(
            _prepare_command_code(command.code),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        listener = select.poll()
        listener.register(process.stdout, select.POLLIN)
        processes.append((command, process, listener, color))

    # Wait processes
    while processes:
        for index, (command, process, listener, color) in enumerate(processes):

            # Process is writing
            if listener.poll(1000):
                line = process.stdout.readline()
                _print_prefix(command.name, color)
                _print_bytes(line)

            # Process is finished
            if process.poll() is not None:
                if process.returncode != 0:
                    message = '[run] Command "%s" has failed' % command.code
                    helpers.print_message('general', message=message)
                    exit(1)
                processes.pop(index)
                break


# Internal

def _prepare_command_code(code):
    return "python -m run.faketty /bin/bash -c %s" % shlex.quote(code)


def _print_prefix(prefix, color, max_prefix_width=None):
    click.echo(click.style('%s | ' % prefix, fg=color), nl=False)


def _print_bytes(bytes, stream=sys.stdout):
    buffer = getattr(stream, 'buffer', stream)
    buffer.write(bytes)
    stream.flush()
