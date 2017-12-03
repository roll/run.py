# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# Module API

class Command(object):

    # Public

    def __init__(self, name, code, variable=None):
        self._name = name
        self._code = code
        self._variable = variable

    def __repr__(self):
        return self._name

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def primary(self):
        return '$RUNARGS' in self._code

    @property
    def variable(self):
        return self._variable
