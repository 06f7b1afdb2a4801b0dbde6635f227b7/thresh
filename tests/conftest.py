# -*- coding: utf-8 -*-
"""
This file contains the fixtures to be used for the _thresh_ tests. These
make it easier to write tests by giving ready access to variables and data
structures.
"""
from collections import OrderedDict
import numpy as np
import pytest

@pytest.fixture
def content_1():
    """ Sample content, version 1. """
    return OrderedDict((
        ('a', np.array([1.0, 2.0, 3.0, 4.0])),
        ('b', np.array([0.0, 0.1, 0.2, 0.3])),
        ('c', np.array([1.4, 2.3, 3.2, 4.1])),
        ))

@pytest.fixture
def content_2():
    """ Sample content, version 2. """
    return OrderedDict((
        ('d', np.array([1.0, 0.0, 2.0, 0.0])),
        ('e', np.array([0.0, 3.0, 0.0, 4.0])),
        ('f', np.array([5.0, 0.0, 6.0, 0.0])),
        ))
