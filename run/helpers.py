# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import click


# Module API

def print_message(type, **data):
    text = click.style(data['message'], bold=True)
    click.echo(text)
