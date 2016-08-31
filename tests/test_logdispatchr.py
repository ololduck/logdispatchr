#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_logdispatchr
----------------------------------

Tests for `logdispatchr` module.
"""


import sys
import unittest
from contextlib import contextmanager
from click.testing import CliRunner

import logdispatchr
from logdispatchr import cli


class TestLogdispatchr(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_something(self):
        pass

    def test_command_line_interface(self):
        # runner = CliRunner()
        # result = runner.invoke(cli.main)
        # assert result.exit_code == 0
        # assert 'logdispatchr.cli.main' in result.output
        # help_result = runner.invoke(cli.main, ['--help'])
        # assert help_result.exit_code == 0
        # assert '--help  Show this message and exit.' in help_result.output
        pass


if __name__ == '__main__':
    sys.exit(unittest.main())
