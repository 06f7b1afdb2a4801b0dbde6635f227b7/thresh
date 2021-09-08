# -*- coding: utf-8 -*-
"""
This file contains tests that focus on general set-up
of the python environment. They also check things that
probably don't need any checking.
"""

import sys
import itertools
import pathlib
from collections import OrderedDict
import numpy as np
import pytest
import basic_files


import thresh


def test_absolute_truth():
    """Ensure that the testing library is working."""
    assert True

def test_capture_output(capsys):
    """Test that the capturing of stdout works."""
    print("hello world")
    out, err = capsys.readouterr()
    assert out == "hello world\n"
    assert err == ""


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
# Initialize TabularFile Object
#

def test_initialize_TabularFile_no_content():
    """ Do a basic initialization of a TabularFile without content. """
    tabularfile = thresh.TabularFile()
    assert tabularfile.alias is None
    assert tabularfile.content == OrderedDict()

def test_initialize_TabularFile_no_alias(content_1):
    """ Do a basic initialization of a TabularFile without an alias. """
    tabularfile = thresh.TabularFile(content=content_1)
    assert tabularfile.alias is None
    assert tabularfile.content == content_1


def test_initialize_TabularFile_with_alias(content_1):
    """ Do a basic initialization of a TabularFile. """
    alias = "A"
    tabularfile = thresh.TabularFile(content=content_1, alias=alias)
    assert tabularfile.alias == alias
    assert tabularfile.content == content_1


@pytest.mark.parametrize("bad_alias", [3.14, ".foo", "fizz.buzz", "1baz", "hello*world", ""])
def test_initialize_TabularFile_with_bad_alias(content_1, bad_alias):
    """ TabularFile initialization with bad alias - not str. """
    if isinstance(bad_alias, str):
        with pytest.raises(SyntaxError):
            thresh.TabularFile(content=content_1, alias=bad_alias)
    else:
        with pytest.raises(TypeError):
            thresh.TabularFile(content=content_1, alias=bad_alias)


def test_initialize_TabularFile_with_bad_content_1():
    """ TabularFile initialization with bad content - not OrderedDict. """
    with pytest.raises(TypeError):
        thresh.TabularFile(content=3.14)


def test_initialize_TabularFile_with_bad_content_2(content_1):
    """ TabularFile initialization with bad content - non-text key. """
    content_1[3.14] = content_1['a']
    with pytest.raises(KeyError):
        thresh.TabularFile(content=content_1)


def test_initialize_TabularFile_with_bad_content_3(content_1):
    """ TabularFile initialization with bad content - uneven column lengths. """
    content_1['a'] = np.append(content_1['a'], content_1['a'])
    with pytest.raises(IndexError):
        thresh.TabularFile(content=content_1)

#
#  TabularFile.list_headers()
#

def test_list_headers_default(capsys, tabularfile_2):
    """ Check the default behavior of the list_headers() function. """
    tabularfile_2.list_headers()
    out, err = capsys.readouterr()
    assert out == """ col | length | header
----------------------
   0 |      4 | time
   1 |      4 | strain
   2 |      4 | stress
"""
    assert err == ""

def test_list_headers_json(capsys, jsonfile_1):
    """ Check the default behavior of the list_headers() function. """
    jsonfile_1.list_headers()
    out, err = capsys.readouterr()
    assert out == """name | type\n-----------\n bar |  int\n foo |  int\n"""
    assert err == ""



#
#  TabularFile.basic_list_headers()
#

def test_basic_list_headers_default(capsys, tabularfile_2):
    """ Check the default behavior of the basic_list_headers() function. """
    tabularfile_2.basic_list_headers()
    out, err = capsys.readouterr()
    assert out == """time
strain
stress
"""
    assert err == ""


#
#  TabularFile.as_text()
#
def test_as_text_default(tabularfile_3):
    """ Verifies the conversion to text with default delimiter. """
    txt = tabularfile_3.as_text()
    print("comp", repr(txt))
    assert txt == '                      var1                      var2\n  +1.57079632679489656e+00  +1.11111111111111105e-01\n  +3.14159265358979312e+00  +2.22222222222222210e-01\n  +4.71238898038468967e+00  +3.33333333333333315e-01\n'

def test_as_text_whitespace_delimiter(tabularfile_3):
    """ Verifies the conversion to text with whitespace delimiter. """
    txt = tabularfile_3.as_text(delimiter='')
    print("comp", repr(txt))
    assert txt == '                      var1                      var2\n  +1.57079632679489656e+00  +1.11111111111111105e-01\n  +3.14159265358979312e+00  +2.22222222222222210e-01\n  +4.71238898038468967e+00  +3.33333333333333315e-01\n'

def test_as_text_comma_delimiter(tabularfile_3):
    """ Verifies the conversion to text with comma delimiter. """
    txt = tabularfile_3.as_text(delimiter=',')
    print("comp", repr(txt))
    assert txt == '                      var1,                      var2\n  +1.57079632679489656e+00,  +1.11111111111111105e-01\n  +3.14159265358979312e+00,  +2.22222222222222210e-01\n  +4.71238898038468967e+00,  +3.33333333333333315e-01\n'

#
#  TabularFile.from_file()
#
@pytest.mark.parametrize("thresh_file", [_ for _ in basic_files.base_files if _.startswith("pass_")])
@pytest.mark.parametrize("do_path", [True, False])
def test_from_file_string(thresh_file, do_path):
    """ Check that the TabularFile.from_file() function behaves properly. """

    solution_content = basic_files.base_files[thresh_file][1]

    # Do every test with pathlib and without
    file_obj = pathlib.Path(thresh_file) if do_path else thresh_file

    pathlib.Path(thresh_file).write_text(basic_files.base_files[thresh_file][0])

    tf_obj = thresh.TabularFile.from_file(file_obj)
    print("tf_obj.content", tf_obj.content)
    for key in tf_obj.content:
        assert np.allclose(tf_obj.content[key], solution_content[key],
                           atol=1.0e-12, rtol=1.0e-12)

def test_from_file_fail_nonunique_headers(thresh_files):
    """ Test the TabularFile.from_file() for non-unique headers. """
    filename = thresh_files["fail_nonunique_headers.txt"]
    with pytest.raises(KeyError):
        thresh.TabularFile.from_file(filename)

def test_from_file_fail_unknown_filename_input():
    """ Test the TabularFile.from_file() for unknown filename input. """
    with pytest.raises(TypeError):
        thresh.TabularFile.from_file(lambda x: x+1)

def test_from_file_fail_file_not_found():
    """ Test the TabularFile.from_file() for nonexistant files. """

    with pytest.raises(FileNotFoundError):
        thresh.TabularFile.from_file("c75fc775d1439c3f3d9212d5c813b594.txt")
