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


# Ensure that 'thresh' is imported from parent directory.
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))

try:
    import thresh
except ImportError:
    thresh = None


#
#  cat
#

def test_cat1(capsys, thresh_files):
    """ Test the behavior of CAT on a simple file """

    args = ["A="+str(thresh_files["pass_a.txt"]), "cat"]
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                      a                      b                      c
  +7.00000000000000e+00  +8.00000000000000e+00  +2.00000000000000e+00
  +0.00000000000000e+00  +5.00000000000000e+00  +0.00000000000000e+00
  +1.00000000000000e+00  +2.00000000000000e+00  +3.00000000000000e+00
  +3.00000000000000e+00  +4.00000000000000e+00  +5.00000000000000e+00
  +7.00000000000000e+00  +1.00000000000000e+00  +4.00000000000000e+00
"""


def test_cat2(capsys, thresh_files):
    """ Test the behavior of CAT on a simple file extracting one column"""

    args = ["A="+str(thresh_files["pass_a.txt"]), "cat", "Aa", "b"]
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                      a                      b
  +7.00000000000000e+00  +8.00000000000000e+00
  +0.00000000000000e+00  +5.00000000000000e+00
  +1.00000000000000e+00  +2.00000000000000e+00
  +3.00000000000000e+00  +4.00000000000000e+00
  +7.00000000000000e+00  +1.00000000000000e+00
"""


def test_cat2(capsys, thresh_files):
    """ Test the behavior of CAT on a simple file and creating a column"""

    args = ["A="+str(thresh_files["pass_a.txt"]), "cat", "A", "d=a+Ab"]
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                      a                      b                      c                      d
  +7.00000000000000e+00  +8.00000000000000e+00  +2.00000000000000e+00  +1.50000000000000e+01
  +0.00000000000000e+00  +5.00000000000000e+00  +0.00000000000000e+00  +5.00000000000000e+00
  +1.00000000000000e+00  +2.00000000000000e+00  +3.00000000000000e+00  +3.00000000000000e+00
  +3.00000000000000e+00  +4.00000000000000e+00  +5.00000000000000e+00  +7.00000000000000e+00
  +7.00000000000000e+00  +1.00000000000000e+00  +4.00000000000000e+00  +8.00000000000000e+00
"""


def test_cat3(capsys, thresh_files):
    """ Test the behavior of CAT completely building data """

    args = ["cat", "t=linspace(0,1,5)", "f=t**2"]
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                      t                      f
  +0.00000000000000e+00  +0.00000000000000e+00
  +2.50000000000000e-01  +6.25000000000000e-02
  +5.00000000000000e-01  +2.50000000000000e-01
  +7.50000000000000e-01  +5.62500000000000e-01
  +1.00000000000000e+00  +1.00000000000000e+00
"""
