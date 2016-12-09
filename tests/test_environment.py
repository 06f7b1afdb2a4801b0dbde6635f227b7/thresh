# -*- coding: utf-8 -*-
"""
This file contains tests that focus on general set-up
of the python environment. They also check things that
probably don't need any checking.
"""

import sys
import pathlib


# Ensure that 'thresh' is imported from parent directory.
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))

try:
    import thresh
except ImportError:
    thresh = None


def test_absolute_truth():
    """Ensure that the testing library is working."""

    # Setup ###################################################################
    pass

    # Test ####################################################################
    assert True

    # Teardown ################################################################
    pass


def test_require_python3():
    """The module 'thresh' and these tests require  at least Python 3.0."""

    # Setup ###################################################################
    pass

    # Test ####################################################################
    assert sys.version_info > (3, 0)

    # Teardown ################################################################
    pass


def test_import():
    """Ensure that 'thresh' is imported."""

    # Setup ###################################################################
    pass

    # Test ####################################################################
    assert thresh is not None

    # Teardown ################################################################
    pass


def test_initialize():
    """Do something simple with 'thresh'."""

    # Setup ###################################################################
    pass

    # Test ####################################################################
    assert thresh.__version__ > (0, 0, 0)

    # Teardown ################################################################
    pass
