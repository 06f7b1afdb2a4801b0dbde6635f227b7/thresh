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
    """ Check that the parse_args() function behaves properly without aliases. """

    args = [str(val) for key, val in thresh_files.items()] + [task,]

    files_to_be_read_out, task_out, task_specific_args = thresh.parse_args(args)

    # This contains the filename and alias:
    #   files_to_be_read_out = [["filename.txt", "a"],
    #                           ["file2.txt", None]]

    assert task_out == task
    assert [_[0] for _ in files_to_be_read_out] == args[:-1]
    assert len(task_specific_args) == 0


@pytest.mark.parametrize('task', ['list', 'cat', 'burst'])
def test_parse_args_with_alias(thresh_files, task):
    """
    Check that the parse_args() function behaves properly with aliases.
    We're trying to check that we can pass args like
      A=pass_a.txt pass_b.txt z=pass_c.csv
    and get it parsed correctly.
    """

    files = [str(val) for key, val in thresh_files.items()]
    args = [_ for _ in files] + [task,]
    args[0] = "A=" + args[0]
    args[2] = "z=" + args[2]

    solution = [[_, None] for _ in files]
    solution[0][1] = "A"
    solution[2][1] = "z"

    files_to_be_read_out, task_out, task_specific_args = thresh.parse_args(args)

    assert task_out == task
    assert len(solution) == len(files_to_be_read_out)
    for idx in range(len(solution)):
        assert solution[idx] == files_to_be_read_out[idx]
    assert len(task_specific_args) == 0


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
def test_parse_args_gather_unused_arguments(task, thresh_files):
    """
    Check that the parse_args() correctly passes out unused arguments.
    """

    args = [str(val) for key, val in thresh_files.items()] + [task,]

    # Add something valid to the end to get an unused argument
    args = args + random.sample(args, 1)

    files, task, task_specific_args = thresh.parse_args(args)
    assert args[-1] == task_specific_args[0]
