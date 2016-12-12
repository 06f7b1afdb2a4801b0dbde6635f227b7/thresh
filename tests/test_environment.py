# -*- coding: utf-8 -*-
"""
This file contains tests that focus on general set-up
of the python environment. They also check things that
probably don't need any checking.
"""

import sys
import pathlib
import numpy as np
from collections import OrderedDict
import pytest


# Ensure that 'thresh' is imported from parent directory.
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))

try:
    import thresh
except ImportError:
    thresh = None


def test_absolute_truth():
    """Ensure that the testing library is working."""
    assert True


def test_require_python3():
    """The module 'thresh' and these tests require  at least Python 3.0."""
    assert sys.version_info > (3, 0)


def test_import():
    """Ensure that 'thresh' is imported."""
    assert thresh is not None


def test_initialize():
    """Do something simple with 'thresh'."""
    assert thresh.__version__ > (0, 0, 0)


#
# Initialize ThreshFile Object
#

def test_initialize_ThreshFile_no_alias(content_1):
    """ Do a basic initialization of a ThreshFile without an alias. """
    tf = thresh.ThreshFile(content=content_1)
    assert tf.alias == None
    assert tf.content == content_1


def test_initialize_ThreshFile_with_alias(content_1):
    """ Do a basic initialization of a ThreshFile. """
    alias = "A"
    tf = thresh.ThreshFile(content=content_1, alias=alias)
    assert tf.alias == alias
    assert tf.content == content_1


def test_initialize_ThreshFile_with_bad_alias(content_1):
    """ ThreshFile initialization with bad alias - not str. """
    alias = 3.14
    with pytest.raises(TypeError):
        thresh.ThreshFile(content=content_1, alias=alias)


def test_initialize_ThreshFile_with_bad_content_1():
    """ ThreshFile initialization with bad content - not OrderedDict. """
    with pytest.raises(TypeError):
        thresh.ThreshFile(content=3.14)


def test_initialize_ThreshFile_with_bad_content_2(content_1):
    """ ThreshFile initialization with bad content - non-text key. """
    content_1[3.14] = content_1['a']
    with pytest.raises(KeyError):
        thresh.ThreshFile(content=content_1)


def test_initialize_ThreshFile_with_bad_content_3(content_1):
    """ ThreshFile initialization with bad content - uneven column lengths. """
    content_1['a'] = np.append(content_1['a'], content_1['a'])
    with pytest.raises(IndexError):
        thresh.ThreshFile(content=content_1)
