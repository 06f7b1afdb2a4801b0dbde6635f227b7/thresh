# -*- coding: utf-8 -*-
"""
"""

import copy
import pytest
import thresh


db_good = [
    {
        "name": "with comments",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "-----\n",
            " a  b\n",
            "=====\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "without comments",
        "lines": [
            "-----\n",
            " a  b\n",
            "=====\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "with rules in comments",
        "lines": [
            "-----------------\n",
            "this is a comment\n",
            "=================\n",
            "this is a comment\n",
            "-----\n",
            " a  b\n",
            "=====\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
]


@pytest.mark.parametrize("db", db_good, ids=[_["name"] for _ in db_good])
def test_format_if_history_file_good(db):
    """
    This covers all the instances where we expect the formatting function
    will succeed because the strict formatting rules for a history file
    have been met.
    """
    lines = db["lines"]
    out = thresh.TabularFile.format_if_history_file(copy.deepcopy(lines))

    # make sure that it doesn't care about newlines at the end.
    out[-1] = out[-1].rstrip("\n")
    assert out == [" a  b\n", " 1  2\n", " 3  4"]


db_bad = [
    {
        "name": "no rules - not history file",
        "lines": [
            " a  b\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "missing '-' line",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            " a  b\n",
            "=====\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "missing '=' line",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "-----n",
            " a  b\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "too many header lines",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "-----n",
            " a  b\n",
            " a  b\n",
            "=====n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "too few header lines",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "-----\n",
            "=====\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "upper rule too long",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "------\n",
            " a  b\n"
            "=====n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "upper rule too short",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "----\n",
            " a  b\n"
            "=====\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "lower rule too long",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "-----\n",
            " a  b\n"
            "======\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "lower rule too short",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "-----\n",
            " a  b\n"
            "====\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "header line too long",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "-----\n",
            " a   b\n"
            "=====\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
    {
        "name": "header line too short",
        "lines": [
            "this is a comment\n",
            "this is a comment\n",
            "-----\n",
            " a b\n"
            "=====\n",
            " 1  2\n",
            " 3  4\n",
        ],
    },
]

@pytest.mark.parametrize("db", db_bad, ids=[_["name"] for _ in db_bad])
def test_format_if_history_file_bad(db):
    """
    This covers all the instances where we expect the formatting function
    will not do anything because the strict formatting required for the
    history file is not met.
    """
    lines = db["lines"]
    out = thresh.TabularFile.format_if_history_file(copy.deepcopy(lines))
    assert lines == out

