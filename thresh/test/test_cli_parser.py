# -*- coding: utf-8 -*-
"""
This file contains tests for the command line parser.
"""

import sys
import random
import pathlib
import pytest
import shlex

import thresh

db_gather = [
    {
        "name": "just stdin",
        "args": "-",
        "filenames": ["-"],
        "aliases": [None],
    },
    {
        "name": "aliased stdin",
        "args": "b=-",
        "filenames": ["-"],
        "aliases": ["b"],
    },

]

db_process = [
    {
        "name": "blank",
        "args": "",
        "actions": [],
    },
    {
        "name": "one arg",
        "args": "cat t=np.linspace(0,1,10)",
        "actions": ["t=np.linspace(0,1,10)"],
    },
    {
        "name": "two args",
        "args": "cat t=np.linspace(0,1,10) tshift=t+10",
        "actions": ["t=np.linspace(0,1,10)", "tshift=t+10"],
    },
]

db_postprocess = [
    {
        "name": "list",
        "args": "list",
        "action": "list",
        "argument": None,
    },
    {
        "name": "print",
        "args": "print .csv",
        "action": "print",
        "argument": ".csv",
    },
    {
        "name": "blank",
        "args": "",
        "action": "print",
        "argument": ".txt",
    },
    {
        "name": "assert",
        "args": "assert \"this==that\"",
        "action": "assert",
        "argument": ["this==that",],
    },
    {
        "name": "assert",
        "args": "assert \"this==that\" \"fizz != buzz\"",
        "action": "assert",
        "argument": ["this==that", "fizz != buzz",],
    },
    {
        "name": "output",
        "args": "output foobar.csv",
        "action": "output",
        "argument": "foobar.csv",
    },
    {
        "name": "burst",
        "args": "burst foobar.csv",
        "action": "burst",
        "argument": "foobar.csv",
    },
]


@pytest.mark.parametrize('gather', db_gather, ids=[_["name"] for _ in db_gather])
@pytest.mark.parametrize('process', db_process, ids=[_["name"] for _ in db_process])
@pytest.mark.parametrize('postprocess', db_postprocess, ids=[_["name"] for _ in db_postprocess])
def test_parse_args(gather, process, postprocess):
    """ """

    comp = thresh.parse_args(shlex.split(gather["args"] + " " + process["args"] + " " + postprocess["args"]))

    for idx in range(len(gather["filenames"])):
        assert comp["gather"][idx].filename == gather["filenames"][idx]
        assert comp["gather"][idx].alias == gather["aliases"][idx]

    assert len(comp["process"]) == len(process["actions"])
    for idx in range(len(process["actions"])):
        assert comp["process"][idx] == process["actions"][idx]

    assert comp["postprocess"].action == postprocess["action"]
    assert comp["postprocess"].argument == postprocess["argument"]
