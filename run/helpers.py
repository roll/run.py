# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os
import yaml
import click


# Module API

def read_config():

    # Bad file
    if not os.path.isfile('run.yml'):
        message = 'No "run.yml" found'
        print_message('general', message=message)
        exit(1)

    # Read contents
    with io.open('run.yml', encoding='utf-8') as file:
        contents = file.read()

    # Read config
    config = {'system': []}
    raw_config = yaml.load(contents)
    for line in contents.split('\n'):
        for key, value in raw_config.items():
            if line.startswith(key):
                config['system'].append({key: value})

    return config


def print_message(type, **data):
    text = click.style(data['message'], bold=True)
    click.echo(text)
