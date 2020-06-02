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

    assert out == """                      a                      b                      c
  +7.00000000000000e+00  +8.00000000000000e+00  +2.00000000000000e+00
  +0.00000000000000e+00  +5.00000000000000e+00  +0.00000000000000e+00
  +1.00000000000000e+00  +2.00000000000000e+00  +3.00000000000000e+00
  +3.00000000000000e+00  +4.00000000000000e+00  +5.00000000000000e+00
  +7.00000000000000e+00  +1.00000000000000e+00  +4.00000000000000e+00
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

    assert out == """                      a                      b
  +7.00000000000000e+00  +8.00000000000000e+00
  +0.00000000000000e+00  +5.00000000000000e+00
  +1.00000000000000e+00  +2.00000000000000e+00
  +3.00000000000000e+00  +4.00000000000000e+00
  +7.00000000000000e+00  +1.00000000000000e+00
"""


@pytest.mark.parametrize('args', [' A d=a+b',
                                  ' A d=Aa+b',
                                  ' A d=a+Ab',
                                  ' A d=Aa+Ab',
                                  ' a b c d=a+b',
                                  ' a b c d=Aa+b',
                                  ' a b c d=a+Ab',
                                  ' a b c d=Aa+Ab',])
def test_cat3(capsys, thresh_files, args):
    """ Test the behavior of CAT on a simple file and creating a column"""

    args = ("A=" + str(thresh_files["pass_a.txt"]) + " cat" + args).split()
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                      a                      b                      c                      d
  +7.00000000000000e+00  +8.00000000000000e+00  +2.00000000000000e+00  +1.50000000000000e+01
  +0.00000000000000e+00  +5.00000000000000e+00  +0.00000000000000e+00  +5.00000000000000e+00
  +1.00000000000000e+00  +2.00000000000000e+00  +3.00000000000000e+00  +3.00000000000000e+00
  +3.00000000000000e+00  +4.00000000000000e+00  +5.00000000000000e+00  +7.00000000000000e+00
  +7.00000000000000e+00  +1.00000000000000e+00  +4.00000000000000e+00  +8.00000000000000e+00
"""


def test_cat4(capsys, thresh_files):
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


def test_cat5(capsys, thresh_files):
    """ Test the behavior of CAT on a simple file excluding certain columns """

    args = ["A="+str(thresh_files["pass_a.txt"]), "cat", "A", "c=None"]
    thresh.main(args)
    out, err = capsys.readouterr()

    assert out == """                      a                      b
  +7.00000000000000e+00  +8.00000000000000e+00
  +0.00000000000000e+00  +5.00000000000000e+00
  +1.00000000000000e+00  +2.00000000000000e+00
  +3.00000000000000e+00  +4.00000000000000e+00
  +7.00000000000000e+00  +1.00000000000000e+00
"""
