# -*- coding: utf-8 -*-
"""
This file contains the fixtures to be used for the _thresh_ tests. These
make it easier to write tests by giving ready access to variables and data
structures.
"""
import copy
import pathlib
from collections import OrderedDict
import numpy as np
import pytest

import basic_files

import thresh

obj_content_1 = OrderedDict((
        ('a', np.array([1.0, 2.0, 3.0, 4.0])),
        ('b', np.array([0.0, 0.1, 0.2, 0.3])),
        ('c', np.array([1.4, 2.3, 3.2, 4.1])),
        ))
obj_content_2 = OrderedDict((
        ('time', np.array([0.0, 1.0, 2.0, 3.0])),
        ('strain', np.array([0.0, 0.2, 0.3, 0.3])),
        ('stress', np.array([0.0, 2.0, 3.0, 3.0])),
        ))

obj_content_3 = OrderedDict((
        ('var1', np.array([0.5, 1.0, 1.5]) * np.pi),
        ('var2', np.array([1.0, 2.0, 3.0]) / 9.0),
        ))

@pytest.fixture
def content_1():
    """ Sample content, version 1. """
    return copy.deepcopy(obj_content_1)


@pytest.fixture
def content_2():
    """ Sample content, version 2. """
    return copy.deepcopy(obj_content_2)


@pytest.fixture
def content_3():
    """ Sample content, version 3. """
    return copy.deepcopy(obj_content_3)


@pytest.fixture
def tabularfile_1():
    """ A TabularFile object built on 'content_1'. """
    return thresh.TabularFile(content=copy.deepcopy(obj_content_1), alias="tabularfile_1")


@pytest.fixture
def tabularfile_2():
    """ A TabularFile object built on 'content_2'. """
    return thresh.TabularFile(content=copy.deepcopy(obj_content_2), alias="tabularfile_2")


@pytest.fixture
def tabularfile_3():
    """ A TabularFile object built on 'content_3'. """
    return thresh.TabularFile(content=copy.deepcopy(obj_content_3), alias="tabularfile_3")


@pytest.fixture
def thresh_files(tmpdir_factory):
    """ Create a temporary directory and write basic files """
    tmpdir = tmpdir_factory.mktemp('tmp_thresh')

    qobj = dict()
    qobj.update(basic_files.base_files)
    qobj.update(basic_files.fail_files)

    filenames = {}
    for file_name in qobj:
        fpath = pathlib.Path(str(tmpdir.join(file_name)))
        filenames[file_name] = fpath
        # [0] = text, [1] = OrderedDict
        fpath.write_text(qobj[file_name][0], encoding="utf-8")

    return filenames
