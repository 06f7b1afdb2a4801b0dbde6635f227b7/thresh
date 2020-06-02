#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2016
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
This file contains all the components necessary to run 'thresh'.
"""
import sys
import copy
import pathlib
from collections import OrderedDict, namedtuple
from .tabular_file_container import TabularFile
import numpy as np

__version__ = (0, 0, 1)

def print_help():
    print("""thresh:
verb: to separate the wheat from the chaff.

This program was written to help process tabular text files in
a quick and easy way, giving you the pieces you care about
and discarding the rest.

Usage:
------

The following files will be used in examples:

$ cat file1.txt
a b
0 3
1 4
2 5

$ cat file2.txt
a c
6 9
7 10
8 11

Process the whole file and print to stdout (all are equivalent):
$ thresh.py file1.txt cat             # No args = print whole file
$ thresh.py file1.txt cat a b         # Can request specific columns
$ thresh.py A=file1.txt cat A         # Just an alias requests the whole file
$ thresh.py A=file1.txt cat Aa Ab     # Use aliases when columns are in multiple files
$ thresh.py A=file1.txt cat Aa  b     # Aliases are optional
$ thresh.py A=file1.txt cat  a Ab     # Aliases are optional
$ thresh.py A=file1.txt cat  a  b     # Aliases are optional

Extract only one column:
$ thresh.py file1.txt cat b
$ thresh.py Z=file1.txt cat b
$ thresh.py Z=file1.txt cat Zb

Get one column from each file:
$ thresh.py   file1.txt   file2.txt cat  a  c
$ thresh.py   file1.txt Q=file2.txt cat  a Qc
$ thresh.py M=file1.txt Q=file2.txt cat Ma Qc

Handle columns that exist in multiple files:
$ thresh.py X=file1.txt Y=file2.txt cat Xa c  # Specify column 'a' from file1.txt
$ thresh.py X=file1.txt Y=file2.txt cat Ya b  # Specify column 'a' from file2.txt

Create a new file (using '' so the parentheses are passed correctly):
$ thresh.py cat 't=linspace(0,1,5)' f=t**2

Produce a file with interpolated data (create new column called 't' and overwrite
column 'b' with the interpolated data corresponding to 't').
$ thresh.py file1.txt cat 't=linspace(min(a),max(a),9)' 'b=interp(t,a,b)'
""")

def parse_args(args_in):
    """
    This parses the command-line inputs and organizes it in the following
    manner to be returned:

    1) "gather" stage arguments

    2) "process/cat" stage arguments

    3) "postprocess" stage arguments

    return OrderedDict((
        ("gather": [list of namedtuple()] ),
        ("process": [list of strings]),
        ("postprocess": namedtuple()),
    ))



    1) list of file names to be read in along with any defined aliases:
          a = [['file1.txt', None],
               ['file2.txt', 'A']]

    2) a token specifying the task to be done with the files. Currently,
       the only tokens recognized are:
       * "list"  --> list headers
       * "cat"   --> cat together and output
       * "burst" --> split each column into its own file
       * "help"  --> user requested the help message; do nothing

    3) A list of all the remaining arguments after the token from #2.
    """

    # Make a copy of the input args
    args = copy.deepcopy(args_in)

    # Make the returned object
    Gather = namedtuple("Gather", ["filename", "alias"])
    Postprocess = namedtuple("Postprocess", ["action", "argument"])
    instructions = OrderedDict((
        ("gather", []),
        ("process", []),
        ("postprocess", Postprocess(action="print", argument=".txt")),

    ))

    # Check if help is requested:
    if len(args) == 0 or "-h" in args or "--help" in args or "help" in args:
        instructions["postprocess"] = Postprocess(action="help", argument=None)
        return instructions

    stage = "gather"
    task = "gather"
    while len(args) > 0:

        # Extract the argument.
        arg = args.pop(0)

        # Stage changing.
        if arg in ["cat",]:
            stage = "process"
            task = "cat"
            continue

        elif arg in ["check", "output", "burst", "print"]:
            stage = "postprocess"
            task = arg
            continue

        elif arg in ["list"]:
            stage = "postprocess"
            task = arg
            instructions[stage] = Postprocess(action=task, argument=None)
            if len(args) != 0:
                raise Exception(f"Unexpected extra arguments: {args}")
            continue

        # Task creation.
        if task == "gather":
            if pathlib.Path(arg).is_file() or arg == "-":
                instructions[stage].append(Gather(filename=arg, alias=None))
            elif (arg[0].isalpha() and
                  arg[1] == "=" and
                  (pathlib.Path(arg[2:]).is_file() or arg[2:] == "-")):
                instructions[stage].append(Gather(filename=arg[2:], alias=arg[0]))
            else:
                raise FileNotFoundError(f"File not found: {arg}")

        elif task == "cat":
            instructions[stage].append(arg)

        elif task in ["check", "output", "burst", "print"]:
            instructions[stage] = Postprocess(action=task, argument=arg)
            if len(args) != 0:
                raise Exception(f"Unexpected extra arguments: {args}")

        else:
            raise Exception(f"Unexpected state: stage={stage}, task={task}, args={args}")


    return instructions


def verify_no_naming_collisions(list_of_data):
    """
    This ensures that there are no ambiguous entries
    """

    # Generate all the names
    aliases = set()
    column_names = set()
    aliased_column_names = set()
    for dat in list_of_data:

        if dat.alias is not None:
            aliases.add(dat.alias)

        for column_header in dat.content.keys():
            column_names.add(column_header)
            if dat.alias is not None:
                aliased_column_names.add(dat.alias + column_header)

    # Check for collisions between aliases and any column name
    ambiguous_requests = set(list(aliases.intersection(column_names))
                           + list(aliases.intersection(aliased_column_names))
                           + list(column_names.intersection(aliased_column_names))
                            )

    return aliases, column_names, aliased_column_names, ambiguous_requests


def eval_from_dict(source, eval_str):
    """
    Evaluates a string 'eval_str' on the arrays with the associated
    keys in the dictionary 'source'.

    This function is not perfectly safe (as it has an eval() in it),
    but is safe enough that non-malicious use will not cause any
    problems on the system.
    """

    safe_dict = OrderedDict((
      ('sqrt', np.sqrt),
      ('sin', np.sin),
      ('cos', np.cos),
      ('tan', np.tan),
      ('asin', np.arcsin),
      ('acos', np.arccos),
      ('atan', np.arctan),
      ('atan2', np.arctan2),
      ('cosh', np.cosh),
      ('sinh', np.sinh),
      ('tanh', np.tanh),
      ('sinc', np.sinc),
      ('pi',   np.pi),
      ('log', np.log),
      ('exp', np.exp),
      ('floor', np.floor),
      ('ceil', np.ceil),
      ('abs', np.abs),
      ('radians', np.radians),
      ('degrees', np.degrees),
      ('int', np.int64),
      ('float', np.float64),
      ('bool', np.bool8),
      ('clip', np.clip),
      ('hypot', np.hypot),
      ('mod', np.mod),
      ('round', np.round),
      # Functions that generate floats
      ('average', np.average),
      ('mean', np.mean),
      ('median', np.median),
      ('dot', np.dot),
      # Functions that generate arrays
      ('array', np.array),
      ('cumprod', np.cumprod),
      ('cumsum', np.cumsum),
      ('arange', np.arange),
      ('diff', np.diff),   # Returns an N-1 length array
      ('interp', np.interp),
      ('linspace', np.linspace),
      ('ones', np.ones),
      ('sort', np.sort),
      ('zeros', np.zeros),
      # Random
      ('random', np.random.random),
      ('uniform', np.random.uniform),
      ('normal', np.random.normal),
      # Just all of numpy
      ('np', np),
      ))

    conflicts = set(safe_dict.keys()) & set(source.keys())
    if len(conflicts) != 0:
        raise KeyError("Series naming conflict with built-in functions:\n{0}"
                       .format(conflicts))

    safe_dict.update(source)

    try:
        series = eval(eval_str, {}, safe_dict)
    except:
        print("+++ Error while attempting to evaluate '{0}' +++".format(eval_str))
        raise

    return series


def cat_control(*, list_of_data, args):
    """
    This function controls the behavior when 'cat' is invoked.
    At the current time, it is expected that 'args' is a list
    of aliases, column headers, or column headers with prepended
    aliases.

    returns a TabularFile for output.

    Each column must be uniquely defined in the input 'args' and
    have a unique header for the output.
    """

    def clobber_warn(label):
        sys.stderr.write("WARNING: clobbering column '{0}'\n".format(label))

    def remove_warn(label):
        sys.stderr.write("WARNING: removing column '{0}'\n".format(label))

    a = verify_no_naming_collisions(list_of_data)
    aliases, column_names, aliased_column_names, ambiguous_requests = a

    # Load the unique columns
    unique_columns = (column_names | aliased_column_names) - ambiguous_requests
    input_source = {}
    for dat in list_of_data:
        for column_name in dat.content.keys():
            if column_name in unique_columns:
                input_source[column_name] = dat.content[column_name]
            if dat.alias is not None and dat.alias + column_name in unique_columns:
                input_source[dat.alias + column_name] = dat.content[column_name]

    # If no arguments are given, include every column without checking for ambiguities
    if len(args) == 0:
        for dat in list_of_data:
            for column_header in dat.content.keys():
                args.append(column_header)

    output = OrderedDict()
    for arg in args:

        # The input is requesting something ambiguous
        if arg in ambiguous_requests:
            raise Exception("Ambiguous request: {0}".format(arg))

        # The input is requesting an entire input file
        elif arg in aliases:
            for dat in list_of_data:
                if arg != dat.alias:
                    continue
                for column_name in dat.content.keys():
                    if column_name in output:
                        clobber_warn(column_name)
                    output[column_name] = dat.content[column_name]
                break

        # The input is requesting a column by name
        elif arg in column_names:
            for dat in list_of_data:
                if arg not in dat.content:
                    continue
                if arg in output:
                    clobber_warn(arg)
                output[arg] = dat.content[arg]
                break

        # The input is requesting a column by aliased name
        elif arg in aliased_column_names:
            for dat in list_of_data:
                if arg[0] != dat.alias:
                    continue
                if arg[1:] in output:
                    clobber_warn(arg[1:])
                output[arg[1:]] = dat.content[arg[1:]]
                break

        # The input is requesting to create a column
        elif "=" in arg:

            head, eval_str = [_.strip() for _ in arg.split("=", maxsplit=1)]
            if len(head) == 0:
                raise Exception("No column label given: {0}".format(arg))
            if len(eval_str) == 0:
                raise Exception("No eval string given: {0}".format(arg))

            tmp_dict = OrderedDict(input_source)
            tmp_dict.update(output)
            s = eval_from_dict(tmp_dict, eval_str)


            if s is None:
                # User requested deleting a column
                if head not in output.keys():
                    raise Exception("Failed to remove '{0}': not found."
                                    .format(head))
                else:
                    remove_warn(head)
                    output.pop(head)
            else:
                # We only clobber if it already exists
                if head in output:
                    clobber_warn(head)
                output[head] = s

        else:
            raise Exception("Alias/column not found: '{0}'".format(arg))

    return TabularFile(content=output)



def main(args):
    """
    This is the main function which takes the command-line arguments and
    does all the work.
    """

    # Parse the given arguments.
    instructions = parse_args(args)

    #
    # Read in the files and store them.
    #
    if len(instructions["gather"]) == 0 and instructions["postprocess"].action != "help":
        sys.stderr.write("WARNING: No files to read in.")

    if [_.filename for _ in instructions["gather"]].count("-") > 1:
        raise Exception("Cannot have more than one instance of reading from stdin ('-').")

    list_of_data = [TabularFile.from_file(_.filename, alias=_.alias)
                    for _ in instructions["gather"]]

    #
    # Process
    #
    if len(instructions["process"]) > 0:
        output = cat_control(list_of_data=list_of_data,
                             args=instructions["process"])
        list_of_data = [output]

    # It only really makes sense to output a single file.
    if len(list_of_data) > 1:
        sys.stderr.write(f"WARNING: discarding {len(list_of_data)-1} files of data")
    if len(list_of_data) == 0:
        sys.stderr.write(f"WARNING: No files read in.")
    output_data = list_of_data[0] if len(list_of_data) > 0 else None

    #
    # Postprocess
    #
    if instructions["postprocess"].action == 'help':
        print_help()

    elif instructions["postprocess"].action == 'list':
        output_data.list_headers()

    elif instructions["postprocess"].action == "print":
        # If you're trying to fix the warnings and the bad exit code
        # when this gets piped to `head`, stop trying. You can't fix
        # it. Python is just dies noisily when `head` closes the pipe.
        delimiter = "," if instructions["postprocess"].argument == ".csv" else ""
        sys.stdout.write(output_data.as_text(delimiter=delimiter))

    elif instructions["postprocess"].action == "output":
        delimiter = "," if instructions["postprocess"].argument.endswith(".csv") else ""
        with open(instructions["postprocess"].argument, 'w') as F:
            F.write(output_data.as_text(delimiter=delimiter))
        sys.stderr.write(f"Wrote data to {instructions['postprocess'].argument}")

    elif instructions["postprocess"].action == 'check':
        val = eval_from_dict(output_data.content, instructions["postprocess"].argument)
        return_code = (0 if bool(val) else 1)
        sys.stderr.write(
            f"Thresh - Performing check:\n"
            f"{instructions['postprocess'].argument}\n"
            f"Evaluated to {repr(val)} and {bool(val)} as a boolean.\n"
            f"Exiting with return code {return_code}.\n"
        )
        sys.exit(return_code)

    elif instructions["postprocess"].action == 'burst':
        raise NotImplementedError("'burst' not implemented.")

    else:
        raise Exception(
            f"Postprocessing step not recognized:"
            f" action={repr(instructions['postprocess'].action)}"
            f" argument={repr(instructions['postprocess'].argument)}"
        )


if __name__ == '__main__':
    main(sys.argv[1:])
