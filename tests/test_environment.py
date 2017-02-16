# -*- coding: utf-8 -*-
"""
This file contains tests that focus on general set-up
of the python environment. They also check things that
probably don't need any checking.
"""

import sys
import itertools
import pathlib
import numpy as np
import pytest
import basic_files


# Ensure that 'thresh' is imported from parent directory.
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))

try:
    import thresh
except ImportError:
    thresh = None


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
# Initialize ThreshFile Object
#

def test_initialize_ThreshFile_no_alias(content_1):
    """ Do a basic initialization of a ThreshFile without an alias. """
    threshfile = thresh.ThreshFile(content=content_1)
    assert threshfile.alias is None
    assert threshfile.content == content_1


def test_initialize_ThreshFile_with_alias(content_1):
    """ Do a basic initialization of a ThreshFile. """
    alias = "A"
    threshfile = thresh.ThreshFile(content=content_1, alias=alias)
    assert threshfile.alias == alias
    assert threshfile.content == content_1


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

#
#  ThreshFile.list_headers()
#

def test_list_headers_default(capsys, threshfile_2):
    """ Check the default behavior of the list_headers() function. """
    threshfile_2.list_headers()
    out, err = capsys.readouterr()
    assert out == "==> threshfile_2 <==\n  1 time\n  2 strain\n  3 stress\n"
    assert err == ""

def test_list_headers_no_alias(capsys, threshfile_2):
    """ Check the non-default behavior of the list_headers() function. """
    threshfile_2.list_headers(print_alias=False)
    out, err = capsys.readouterr()
    assert out == "  1 time\n  2 strain\n  3 stress\n"
    assert err == ""

def test_list_headers_with_alias(capsys, threshfile_2):
    """ Check the non-default behavior of the list_headers() function. """
    threshfile_2.list_headers(print_alias=True)
    out, err = capsys.readouterr()
    assert out == "==> threshfile_2 <==\n  1 time\n  2 strain\n  3 stress\n"
    assert err == ""

#
#  ThreshFile.as_text()
#
def test_as_text_default(threshfile_3):
    """ Verifies the conversion to text with default delimiter. """
    txt = threshfile_3.as_text()
    assert txt == '                   var1                   var2\n  +1.57079632679490e+00  +1.11111111111111e-01\n  +3.14159265358979e+00  +2.22222222222222e-01\n  +4.71238898038469e+00  +3.33333333333333e-01'

def test_as_text_whitespace_delimiter(threshfile_3):
    """ Verifies the conversion to text with whitespace delimiter. """
    txt = threshfile_3.as_text(delimiter='')
    assert txt == '                   var1                   var2\n  +1.57079632679490e+00  +1.11111111111111e-01\n  +3.14159265358979e+00  +2.22222222222222e-01\n  +4.71238898038469e+00  +3.33333333333333e-01'

def test_as_text_comma_delimiter(threshfile_3):
    """ Verifies the conversion to text with comma delimiter. """
    txt = threshfile_3.as_text(delimiter=',')
    assert txt == '                   var1,                   var2\n  +1.57079632679490e+00,  +1.11111111111111e-01\n  +3.14159265358979e+00,  +2.22222222222222e-01\n  +4.71238898038469e+00,  +3.33333333333333e-01'

#
#  ThreshFile.from_file()
#

def test_from_file_string(thresh_files):
    """ Check that the ThreshFile.from_file() function behaves properly. """

    for thresh_file, dopath in itertools.product(thresh_files.values(), [True, False]):

        if not thresh_file.name.startswith("pass_"):
            continue
        solution_content = basic_files.base_files[thresh_file.name][1]

        # Do every test with pathlib and without
        file_obj = pathlib.Path(thresh_file) if dopath else thresh_file

        tf_obj = thresh.ThreshFile.from_file(file_obj)
        for key in tf_obj.content:
            assert np.allclose(tf_obj.content[key], solution_content[key],
                               atol=1.0e-12, rtol=1.0e-12)

def test_from_file_fail_nonunique_headers(thresh_files):
    """ Test the ThreshFile.from_file() for non-unique headers. """
    filename = thresh_files["fail_nonunique_headers.txt"]
    with pytest.raises(KeyError):
        thresh.ThreshFile.from_file(filename)

def test_from_file_fail_unknown_filename_input():
    """ Test the ThreshFile.from_file() for unknown filename input. """
    with pytest.raises(TypeError):
        thresh.ThreshFile.from_file(lambda x: x+1)

def test_from_file_fail_file_not_found():
    """ Test the ThreshFile.from_file() for nonexistant files. """

    with pytest.raises(FileNotFoundError):
        thresh.ThreshFile.from_file("c75fc775d1439c3f3d9212d5c813b594.txt")
