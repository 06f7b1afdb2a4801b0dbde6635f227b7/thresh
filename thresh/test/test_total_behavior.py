# -*- coding: utf-8 -*-
"""
This file contains tests that focus on general set-up
of the python environment. They also check things that
probably don't need any checking.
"""

import io
import sys
import json
import itertools
import pathlib
from collections import OrderedDict
import numpy as np
import pytest
import basic_files


import thresh

#
# headerlist
#

def test_headerlist1(capsys, thresh_files):
    """ Test the behavior of headerlist"""

    args = [thresh_files["pass_a.txt"], "headerlist"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "a\nb\nc\n" == out
    assert retcode == 0

#
#  cat
#

@pytest.mark.parametrize('args', ['',
                                  '  a  b  c',
                                  ' A',
                                  ' Aa  b  c',
                                  '  a Ab  c',
                                  '  a  b Ac',
                                  ' Aa Ab  c',
                                  '  a Ab Ac',
                                  ' Aa  b Ac',
                                  ' Aa Ab Ac',])
def test_cat1(capsys, thresh_files, args):
    """ Test the behavior of CAT on a simple file """

    args = ("A=" + str(thresh_files["pass_a.txt"]) + " cat" + args).split()
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                         a                         b                         c
  +7.00000000000000000e+00  +8.00000000000000000e+00  +2.00000000000000000e+00
  +0.00000000000000000e+00  +5.00000000000000000e+00  +0.00000000000000000e+00
  +1.00000000000000000e+00  +2.00000000000000000e+00  +3.00000000000000000e+00
  +3.00000000000000000e+00  +4.00000000000000000e+00  +5.00000000000000000e+00
  +7.00000000000000000e+00  +1.00000000000000000e+00  +4.00000000000000000e+00
"""


@pytest.mark.parametrize('args', ['  a  b',
                                  ' Aa  b',
                                  '  a Ab',
                                  ' Aa Ab',])
def test_cat2(capsys, thresh_files, args):
    """ Test the behavior of CAT on a simple file extracting individual columns """

    args = ("A=" + str(thresh_files["pass_a.txt"]) + " cat" + args).split()
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                         a                         b
  +7.00000000000000000e+00  +8.00000000000000000e+00
  +0.00000000000000000e+00  +5.00000000000000000e+00
  +1.00000000000000000e+00  +2.00000000000000000e+00
  +3.00000000000000000e+00  +4.00000000000000000e+00
  +7.00000000000000000e+00  +1.00000000000000000e+00
"""


@pytest.mark.parametrize('args', [' A d=a+b',
                                  ' A d=Aa+b',
                                  ' A d=a+Ab',
                                  ' A d=Aa+Ab',
                                  ' A d=Aa+__aliases[\"A\"][\"b\"]',
                                  ' a b c d=a+b',
                                  ' a b c d=Aa+b',
                                  ' a b c d=a+Ab',
                                  ' a b c d=Aa+Ab',])
def test_cat3(capsys, thresh_files, args):
    """ Test the behavior of CAT on a simple file and creating a column"""

    args = ("A=" + str(thresh_files["pass_a.txt"]) + " cat" + args).split()
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                         a                         b                         c                         d
  +7.00000000000000000e+00  +8.00000000000000000e+00  +2.00000000000000000e+00  +1.50000000000000000e+01
  +0.00000000000000000e+00  +5.00000000000000000e+00  +0.00000000000000000e+00  +5.00000000000000000e+00
  +1.00000000000000000e+00  +2.00000000000000000e+00  +3.00000000000000000e+00  +3.00000000000000000e+00
  +3.00000000000000000e+00  +4.00000000000000000e+00  +5.00000000000000000e+00  +7.00000000000000000e+00
  +7.00000000000000000e+00  +1.00000000000000000e+00  +4.00000000000000000e+00  +8.00000000000000000e+00
"""


def test_cat4(capsys, thresh_files):
    """ Test the behavior of CAT completely building data """

    args = ["cat", "t=linspace(0,1,5)", "f=t**2"]
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                         t                         f
  +0.00000000000000000e+00  +0.00000000000000000e+00
  +2.50000000000000000e-01  +6.25000000000000000e-02
  +5.00000000000000000e-01  +2.50000000000000000e-01
  +7.50000000000000000e-01  +5.62500000000000000e-01
  +1.00000000000000000e+00  +1.00000000000000000e+00
"""


def test_cat5(capsys, thresh_files):
    """ Test the behavior of CAT on a simple file excluding certain columns """

    args = ["A="+str(thresh_files["pass_a.txt"]), "cat", "A", "c=None"]
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                         a                         b
  +7.00000000000000000e+00  +8.00000000000000000e+00
  +0.00000000000000000e+00  +5.00000000000000000e+00
  +1.00000000000000000e+00  +2.00000000000000000e+00
  +3.00000000000000000e+00  +4.00000000000000000e+00
  +7.00000000000000000e+00  +1.00000000000000000e+00
"""


def test_assert1(capsys, thresh_files):
    """ Test the behavior of the assert statement """

    args = ["A="+str(thresh_files["pass_a.txt"]), "assert", "max(a) == 7"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert retcode == 0

def test_assert2(capsys, thresh_files):
    """ Test the behavior of the assert statement with column accessed via __aliases object"""

    args = ["A="+str(thresh_files["pass_a.txt"]), "cat", "xyz=__aliases['A']['a']", "assert", "max(xyz) == 7"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert retcode == 0

def test_assert3(capsys, thresh_files):
    """ Test the behavior of the assert statement with no data given (expect fail)"""

    args = ["assert", "np.pi == 3"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to False" in err
    assert retcode == 1

def test_assert4(capsys, thresh_files):
    """ Test the behavior of the assert statement with no data given (expect pass)"""

    args = ["assert", "sum([1,2]) == 3"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert retcode == 0

def test_assert5(capsys):
    """ Test the behavior of multiple assert statements with no data given (expect pass)"""

    args = ["assert", "sum([1,2]) == 3", "np.pi != 3.0"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert retcode == 0

def test_assert6(capsys):
    """ Test the behavior of multiple assert statements with no data given (expect fail)"""

    args = ["assert", "sum([1,2]) == 3", "np.pi == 3.0"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert "Evaluated to False" in err
    assert retcode == 1



@pytest.mark.parametrize('args', [
    ["assert", "sum(a) == 18"],
    ["assert", "sum(Aa) == 18"],
    ["cat", "assert", "sum(a) == 18"],
    ["cat", "assert", "sum(Aa) == 18"],
    ["cat", "A", "assert", "sum(a) == 18"],
    ["cat", "A", "assert", "sum(Aa) == 18"],
    ["assert", "sum(a) == 18", "max(b) != 3.1"],
    ["assert", "sum(Aa) == 18", "max(Ab) != 3.1"],
    ["cat", "assert", "sum(a) == 18", "max(b) != 3.1"],
    ["cat", "assert", "sum(Aa) == 18", "max(Ab) != 3.1"],
    ["cat", "A", "assert", "sum(a) == 18", "max(b) != 3.1"],
    ["cat", "A", "assert", "sum(Aa) == 18", "max(Ab) != 3.1"],
])
def test_populate_namespace(capsys, thresh_files, args):
    """ Test to make sure we auto-populate the namespace if you don't name anything """

    args = ["A="+str(thresh_files["pass_a.txt"]),] + args
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    print("retcode", retcode)
    print("out", out)
    print("err", err)
    assert "Evaluated to True" in err
    assert "Evaluated to False" not in err
    assert retcode == 0



def test_json_load1(capsys, thresh_files):
    """ Test the ability to load json files. """

    with open("data.json", "w") as stream:
        json.dump({"approx_pi": 3.0}, stream)

    args = ["data.json", "assert", "approx_pi == 3.0"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert not "Evaluated to False" in err
    assert retcode == 0


def test_json_load2(capsys, thresh_files):
    """ Test the ability to load json files to aliases. """

    with open("data.json", "w") as stream:
        json.dump({"approx_pi": 3.0}, stream)

    args = ["JSON_=data.json", "assert", "JSON_approx_pi == 3.0"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert not "Evaluated to False" in err
    assert retcode == 0


########################################################################
############################### STDIN ##################################
########################################################################

@pytest.mark.parametrize('arg', ["-.json", "-.Json", "-.JSon", "-.jsoN", "-.JSON"])
@pytest.mark.parametrize('alias', ["foo", "bar2", "_", None])
def test_stdin_json(capsys, monkeypatch, alias, arg):
    """ Test the ability to load json files from stdin. """

    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps({"approx_pi": 3.0})))

    if alias is None:
        args = [arg, "assert", "approx_pi == 3.0"]
    else:
        args = [alias + "=" + arg, "assert", alias + "approx_pi == 3.0"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert not "Evaluated to False" in err
    assert retcode == 0

@pytest.mark.parametrize('arg', ["-.csv", "-.Csv", "-.CSv", "-.csV", "-.CSV"])
@pytest.mark.parametrize('alias', ["foo", "bar2", "_", None])
def test_stdin_csv(capsys, monkeypatch, alias, arg):
    """ Test the ability to load csv files from stdin. """

    monkeypatch.setattr('sys.stdin', io.StringIO("a,b\n1,3\n2,4"))

    if alias is None:
        args = [arg, "assert", "sum(a + b) == 10.0"]
    else:
        args = [alias + "=" + arg, "assert", f"sum({alias}a + {alias}b) == 10.0"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert not "Evaluated to False" in err
    assert retcode == 0

@pytest.mark.parametrize('arg', ["-"])
@pytest.mark.parametrize('alias', ["foo", "bar2", "_", None])
def test_stdin_text(capsys, monkeypatch, alias, arg):
    """ Test the ability to load whitespace delimited text files from stdin. """

    monkeypatch.setattr('sys.stdin', io.StringIO("a b\n1 3\n2 4"))

    if alias is None:
        args = [arg, "assert", "sum(a + b) == 10.0"]
    else:
        args = [alias + "=" + arg, "assert", f"sum({alias}a + {alias}b) == 10.0"]
    retcode = thresh.main(args)
    out, err = capsys.readouterr()
    assert "Evaluated to True" in err
    assert not "Evaluated to False" in err
    assert retcode == 0
