# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os
import yaml
from . import helpers


# Module API

class Config(object):

    # Public

    def __init__(self, path):

        # Prepare
        contents = _read_config(path)
        descriptor = _parse_config(contents)

        # Set attributes
        self._descriptor = descriptor

    @property
    def descriptor(self):
        return self._descriptor


# Internal

def _read_config(path):

    # Bad file
    if not os.path.isfile(path):
        message = 'No "%s" found' % path
        helpers.print_message('general', message=message)
        exit(1)

    # Read contents
    with io.open('run.yml', encoding='utf-8') as file:
        contents = file.read()

    return contents


def _parse_config(contents):

    # Parse config
    comments = []
    config = {'run': []}
    raw_config = yaml.load(contents)
    for line in contents.split('\n'):
        if line.startswith('# '):
            comments.append(line.replace('# ', ''))
            continue
        for key, value in raw_config.items():
            if line.startswith(key):
                config['run'].append({key: {'code': value, 'desc': '\n'.join(comments)}})
        if not line.startswith('# '):
            comments = []

    return config
