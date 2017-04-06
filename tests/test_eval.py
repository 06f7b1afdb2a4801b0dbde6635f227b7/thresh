# -*- coding: utf-8 -*-
"""
This file contains tests for the command line parser.
"""

import sys
import pathlib
from collections import OrderedDict
import pytest

import numpy as np

# Ensure that 'thresh' is imported from parent directory.
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))

import thresh


#
#  thresh.eval_from_dict()
#

base = OrderedDict((
    ("A",       np.array([  8,  5,  8,  2, -3])),
    ("B",       np.array([  2,  8,  2,  5,  3])),
    ("C",       np.array([  3,  7, -2, -5,  4])),
     ))

solutions = OrderedDict((
    # Addition
    ("A+1",     np.array([  9,  6,  9,  3, -2])),
    ("A+B",     np.array([ 10, 13, 10,  7,  0])),
    ("A+C",     np.array([ 11, 12,  6, -3,  1])),
    ("B+C",     np.array([  5, 15,  0,  0,  7])),
    ("A+B+C",   np.array([ 13, 20,  8,  2,  4])),
    # Subtraction
    ("A-1",     np.array([  7,  4,  7,  1, -4])),
    ("A-B",     np.array([  6, -3,  6, -3, -6])),
    ("A-C",     np.array([  5, -2, 10,  7, -7])),
    ("B-C",     np.array([ -1,  1,  4, 10, -1])),
    ("A-B-C",   np.array([  3,-10,  8,  2,-10])),
    # Multipliation
    ("A*2",     np.array([ 16, 10, 16,  4, -6])),
    ("A*B",     np.array([ 16, 40, 16, 10, -9])),
    ("A*C",     np.array([ 24, 35,-16,-10,-12])),
    ("B*C",     np.array([  6, 56, -4,-25, 12])),
    # Division
    ("B/10",    np.array([0.2,0.8,0.2,0.5,0.3])),
    # Power
    ("A**2",    np.array([ 64, 25, 64,  4,  9])),
    ("A**B",    np.array([ 64, 390625, 64, 32, -27])),
     ))


@pytest.mark.parametrize('task', solutions.keys())
def test_eval_from_dict(task):
    """
    Check that the 'eval_from_dict()' function behaves correctly.
    """

    out = thresh.eval_from_dict(base, task)

    assert np.allclose(out, solutions[task])


def test_eval_from_dict_bad_lengths():
    """ When there's a length mismatch it should complain """
    with pytest.raises(ValueError):
        tmp = {"A": np.array([0, 1]),
               "B": np.array([0, 1, 2])}
        thresh.eval_from_dict(tmp, "A+B")

def test_eval_from_dict_zero_lengths():
    """
    When there's a length mismatch and one has zero length it
    should complain.
    """
    with pytest.raises(ValueError):
        tmp = {"A": np.array([]),
               "B": np.array([0, 1, 2])}
        thresh.eval_from_dict(tmp, "A+B")


def test_eval_from_dict_variable_not_defined():
    """ When an unset value is referenced it should fail """
    with pytest.raises(NameError):
        thresh.eval_from_dict(base, "D+Z")

def test_eval_from_dict_function_not_defined():
    """ When an unset value is referenced it should fail """
    with pytest.raises(NameError):
        thresh.eval_from_dict(base, "D(A)")
