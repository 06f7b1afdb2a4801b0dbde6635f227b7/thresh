# -*- coding: utf-8 -*-
"""
This file contains tests for the command line parser.
"""

import sys
import random
import pathlib
import pytest

# Ensure that 'thresh' is imported from parent directory.
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))

import thresh


#
#  thresh.parse_args()
#

@pytest.mark.parametrize('task', ['list', 'cat', 'burst'])
def test_parse_args(thresh_files, task):
    """ Check that the parse_args() function behaves properly. """

    args = [str(val) for key, val in thresh_files.items()] + [task,]

    files_to_be_read_out, task_out = thresh.parse_args(args)

    assert task_out == task
    assert files_to_be_read_out == args[:-1]


@pytest.mark.parametrize('args', [[], ['-h'], ['--help']])
def test_parse_args_get_help(args, thresh_files):
    """
    Check that the parse_args() asks for the help text when no inputs
    are given or when '-h' or '--help' is given.
    """

    # If '-h' or '--help', add other arguments and shuffle
    if len(args) > 0:
        args = list(thresh_files) + args
        random.shuffle(args)

    files_to_be_read_out, task_out = thresh.parse_args(args)

    assert len(files_to_be_read_out) == 0
    assert task_out == "help"


@pytest.mark.parametrize('args', [['list'], ['cat'], ['burst']])
def test_from_file_fail_no_files(args):
    """
    Test thresh.parse_args() for when no files are found. When no
    arguments are given, it is a request for help and not an error.
    """

    with pytest.raises(Exception):
        thresh.parse_args(args)


def test_parse_args_fail_no_task(thresh_files):
    """
    Check that the parse_args() fails when no task is given.
    """

    args = [str(val) for key, val in thresh_files.items()]

    with pytest.raises(Exception):
        thresh.parse_args(args)


@pytest.mark.parametrize('task', ['list', 'cat', 'burst'])
def test_parse_args_fail_unused_arguments(task, thresh_files):
    """
    Check that the parse_args() fails when unused arguments are given.
    """

    args = [str(val) for key, val in thresh_files.items()] + [task,]

    # Add something valid to the end to get an unused argument
    args = args + random.sample(args, 1)

    with pytest.raises(Exception):
        thresh.parse_args(args)
