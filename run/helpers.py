# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os
import yaml
import click
from itertools import cycle


# Module API

def read_config(path='run.yml'):

    # Bad file
    if not os.path.isfile(path):
        message = 'No "%s" found' % path
        print_message('general', message=message)
        exit(1)

    # Read documents
    with io.open(path, encoding='utf-8') as file:
        contents = file.read()
    documents = list(yaml.load_all(contents))

    # Get config
    comments = []
    config = {'run': []}
    raw_config = documents[0]
    for line in contents.split('\n'):
        if line.startswith('# '):
            comments.append(line.replace('# ', ''))
            continue
        for key, value in raw_config.items():
            if line.startswith(key):
                config['run'].append({key: {'code': value, 'desc': '\n'.join(comments)}})
        if not line.startswith('# '):
            comments = []

    # Get options
    options = {}
    if len(documents) > 1:
        options = documents[1] or {}

    return config, options


def print_message(type, **data):
    text = click.style(data['message'], bold=True)
    click.echo(text)


def iter_colors():
    for color in cycle(_COLORS):
        yield color


# Internal

_COLORS = [
    'cyan',
    'yellow',
    'green',
    'magenta',
    'red',
    'blue',
    'intense_cyan',
    'intense_yellow',
    'intense_green',
    'intense_magenta',
    'intense_red',
    'intense_blue',
]
