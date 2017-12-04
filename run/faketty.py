# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import pexpect


# Main

child = pexpect.spawn(sys.argv[1], sys.argv[2:])
child.logfile_read = sys.stdout.buffer
child.expect(pexpect.EOF)
