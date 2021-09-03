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

__version__ = (0, 0, 2)


def print_help():
    print(
        """thresh (verb): to separate the wheat from the chaff.

The _thresh_ module is meant primarily as a python module for a
command-line tool for manipulating files containing data in columns so
that you can get rid of what you don't want (the chaff) and are left
with what you do want (the wheat).

Examples of possible operations are: extracting a single column from a
file, merging two files with columns, shifting or scaling a column.


## Quick Start Examples

```bash
# Read in a file and write it out in whitespace-delimited format.
# Using '-' as a filename instructs thresh to read from stdin.
$ thresh data_1.txt
$ cat data_1.txt | thresh -
```

```bash
# See what columns are in a file in human-readable format.
$ thresh data_1.txt list
```

```bash
# Print column names, one per line.
$ thresh data_1.txt headerlist
```

```bash
# Alias the file to A and print the whole file.
$ thresh A=data_1.txt cat A

# Cat only the columns 'time' and 'stress'.
# (output column headers are 'time' and 'stress' even when aliased)
$ thresh data_1.txt cat time stress
$ thresh A=data_1.txt cat Atime Astress

# Cat the whole file, plus a millisecond column 'mtime'
$ thresh A=data_1.txt cat A 'mtime=1000*time'

# Cat the whole file, minus column 'stress'
$ thresh A=data_1.txt cat A stress=None
```

```bash
# Make an analytic solution with columns 'time' and 'wave'.
$ thresh cat 'time=linspace(0,1,10)' 'wave=sin(t)'
```

```bash
# Interpolate data.
$ thresh data_1.txt cat \
  'time1=linspace(min(time),max(time),100)' \
  'stress1=interp(time1,time,stress)'
```

```bash
# Do a simple assert on the data (return code 0 if True, 1 if False).
$ thresh data_1.txt \
  cat 'stress_rate=np.diff(stress)/np.diff(time)' \
  assert 'np.max(np.abs(stress_rate)) < 2.0'
```


### Listing Column Headers

```bash
# See all columns in a file in a simple list.
$ thresh column_data_1.txt headerlist
time
strain
stress
```

```bash
# See all columns in a file with extra info in human-readable format.
$ thresh column_data_1.txt list
 col | length | header
----------------------
   0 |      4 | time
   1 |      4 | strain
   2 |      4 | stress
```

```bash
# See the columns of the file you create.
$ thresh A=data_1.txt cat A 'mtime=1000*time' list
 col | length | header
----------------------
   0 |      4 | time
   1 |      4 | strain
   2 |      4 | stress
   3 |      4 | mtime
```

Note: you cannot `list` more than one file at a time.

```bash
# loop over headers.
$ thresh column_data_1.txt headerlist | while read COL; do echo Found column $COL; done
Found column time
Found column strain
Found column stress
```

### Extracting Columns: Rules

Aliases are included to allow disambiguation of columns with the same
name in different files. For non-ambiguous column names, you can use
the aliased name or the non-aliased name.

Rules governing setting aliases:
* The alias must be one character followed by an equal sign '='.
* The alias must be a letter (a-zA-Z)
* The alias cannot conflict with a column name in any input file
* The alias cannot conflict with another alias

Some of these rules can be broken and will not cause any problems
unless you try to use an ambiguous name/alias. For example, if one
file has a column named 't' and you try to alias a file to 't', you
won't get an error unless you try to use the 't' descriptor.


### Extracting Columns

```bash
# These are all equivalent and print all the columns.
$ thresh data_1.txt
$ thresh data_1.txt cat time strain stress
$ thresh A=data_1.txt cat A
$ thresh A=data_1.txt cat Atime Astrain Astress
$ thresh A=data_1.txt cat Atime strain stress

# These are equivalent (concatenate both files together with no repeated
# column names).
$ thresh data_1.txt data_2.txt
$ thresh A=data_1.txt B=data_2.txt cat A B
$ thresh A=data_1.txt B=data_2.txt cat time Astrain stress Bt eps Bsig

# These are equivalent (all of one file and one column of another).
$ thresh A=data_1.txt data_2.txt cat A sig
$ thresh A=data_1.txt B=data_2.txt cat A sig
$ thresh A=data_1.txt B=data_2.txt cat A Bsig
$ thresh A=data_1.txt B=data_2.txt cat Atime Astrain Astress Bsig
$ thresh A=data_1.txt data_2.txt cat Atime strain stress sig
```


### Manipulating Columns
```bash
# create a new file with a single column called 'mtime' which is
# milliseconds (all equivalent).
$ thresh data_1.txt cat mtime=1000*time
$ thresh A=data_1.txt cat mtime=1000*time
$ thresh A=data_1.txt cat mtime=1000*Atime

# Create a new column based on data from a file and then use that
# new column to create another column.
$ thresh data_1.txt cat \
  'dstress=np.diff(stress)' \
  'dt=np.diff(time)' \
  'stress_rate=dstress / dt'
```


### Creating New Files With No Input File
```bash
# Create a new file that with numbers and their squares.
$ thresh cat 't=arange(1,6,1)' 'squares=t**2'
   t  squares
   1        1
   2        4
   3        9
   4       16
   5       25
```

```bash
# Create a new file that has a sine wave and a noisy sine wave.
$ thresh cat \
  't=linspace(0.0,pi,100)' \
  'sine=sin(t)' \
  'noisey=sine+random.uniform(-1.0,1.0,len(sine))'
```


### Performing an Assert

In some instances, you will want to make checks/asserts on the data and
get feedback in the form of a return code (like for automated tests).
One or more assert statements can be made and compound statements are
okay. The returned value is cast to a boolean and the program terminates
with a return code of 0 if it evaluates to True and 1 if it evaluates to
False.

```bash
# Do a simple assert on the data.
$ thresh data_1.txt \
  cat 'stress_rate=np.diff(stress)/np.diff(time)' \
  assert 'np.max(np.abs(stress_rate)) < 2.0'

# Use multiple asserts.
$ thresh data_1.txt \
  cat 'stress_rate=np.diff(stress)/np.diff(time)' \
  assert \
    'np.max(np.abs(stress_rate)) < 2.0' \
    'np.all(strain >= 0)'

# Use a compound statement.
$ thresh data_1.txt \
  cat 'stress_rate=np.diff(stress)/np.diff(time)' \
  assert 'np.max(np.abs(stress_rate)) < 2.0 and np.all(strain >= 0)'
```

### Saving output
Several different output formats are supported:

```bash
# Regular whitespace-delimited otuput to stdout
$ thresh data_1.txt print

# CSV output to stdout
$ thresh data_1.txt print .csv

# Regular whitespace-delimited otuput to foo.txt
$ thresh data_1.txt output foo.txt

# CSV output to foo.csv
$ thresh data_1.txt output foo.csv
```

### Manipulating columns with special characters
Some column names will have special characters that would make the
column name invalid in python syntax. The work-around requires that the
file in question is aliased. The column is accessed in this manner:

```bash
$ thresh A=data.txt cat "good_name=__aliases['A']['-bad_name%']" assert "max(good_name) > 1"
```

Notes:
* While columns with special names may be accessed this way, they
  cannot be assigned in this way.
* This is only available in the 'cat' section and not in the 'assert'
  section. If you wish to access a "bad" column for assert, give it
  a "good" name in the 'cat' section and use that name in the assert
  section.
"""
    )


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
       * "list"  --> list headers with extra, human-readable info
       * "headerlist"  --> list headers, one per line
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
    instructions = OrderedDict(
        (
            ("gather", []),
            ("process", []),
            ("postprocess", Postprocess(action="print", argument=".txt")),
        )
    )

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
        if arg in ["cat"]:
            stage = "process"
            task = "cat"
            continue

        elif arg in ["assert", "output", "burst", "print"]:
            stage = "postprocess"
            task = arg
            continue

        elif arg in ["list", "headerlist"]:
            stage = "postprocess"
            task = arg
            instructions[stage] = Postprocess(action=task, argument=None)
            if len(args) != 0:
                raise Exception(f"Unexpected extra arguments: {args}")
            continue

        # Task creation.
        if task == "gather":
            tentative_success = False
            if pathlib.Path(arg).is_file() or arg == "-" or arg.startswith("-."):
                # This catches the plain filename case, the stdin case
                # without suffix, and the stdin case with suffix.
                instructions[stage].append(Gather(filename=arg, alias=None))
                tentative_success = True
            elif "=" in arg:
                # We are probably dealing with an alias.
                alias, arg = arg.split("=", 1)
                if pathlib.Path(arg).is_file() or arg == "-" or arg.startswith("-."):
                    instructions[stage].append(Gather(filename=arg, alias=alias))
                    tentative_success = True

            if not tentative_success:
                raise FileNotFoundError(f"File not found or alias incorrectly formatted: {arg}")

        elif task == "cat":
            instructions[stage].append(arg)

        elif task == "assert":
            if instructions[stage].action != "assert":
                instructions[stage] = Postprocess(action=task, argument=[arg,])
            else:
                instructions[stage] = Postprocess(
                    action=task,
                    argument=instructions[stage].argument + [arg,],
                )

        elif task in ["output", "burst", "print"]:
            instructions[stage] = Postprocess(action=task, argument=arg)
            if len(args) != 0:
                raise Exception(f"Unexpected extra arguments: {args}")

        else:
            raise Exception(
                f"Unexpected state: stage={stage}, task={task}, args={args}"
            )

    return instructions


def verify_no_naming_collisions(list_of_data):
    """
    This ensures that there are no ambiguous entries
    """

    ambiguous_requests = set()

    # Aliases are first-class citizens inside of thresh.
    aliases = set()
    for dat in list_of_data:
        if dat.alias is not None:
            if dat.alias in aliases:
                raise Exception(f"Repeated aliases detected: {dat.alias}")
            aliases.add(dat.alias)

    column_names = set()
    aliased_column_names = set()
    for dat in list_of_data:
        for colname in dat.content.keys():
            # If a column name already exists then it's ambiguous.
            if (
                colname in aliases
                or colname in column_names
                or colname in aliased_column_names
            ):
                ambiguous_requests.add(colname)
            column_names.add(colname)

            if dat.alias is None:
                continue

            # If an aliased column name already exists then it's ambiguous.
            acolname = dat.alias + colname
            if (
                acolname in aliases
                or acolname in column_names
                or acolname in aliased_column_names
            ):
                ambiguous_requests.add(acolname)
            aliased_column_names.add(acolname)

    return aliases, column_names, aliased_column_names, ambiguous_requests


def eval_from_dict(source, eval_str):
    """
    Evaluates a string 'eval_str' on the arrays with the associated
    keys in the dictionary 'source'.

    This function is not perfectly safe (as it has an eval() in it),
    but is safe enough that non-malicious use will not cause any
    problems on the system.
    """

    safe_dict = OrderedDict(
        (
            ("sqrt", np.sqrt),
            ("sin", np.sin),
            ("cos", np.cos),
            ("tan", np.tan),
            ("asin", np.arcsin),
            ("acos", np.arccos),
            ("atan", np.arctan),
            ("atan2", np.arctan2),
            ("cosh", np.cosh),
            ("sinh", np.sinh),
            ("tanh", np.tanh),
            ("sinc", np.sinc),
            ("pi", np.pi),
            ("log", np.log),
            ("exp", np.exp),
            ("floor", np.floor),
            ("ceil", np.ceil),
            ("abs", np.abs),
            ("radians", np.radians),
            ("degrees", np.degrees),
            ("int", np.int64),
            ("float", np.float64),
            ("bool", np.bool8),
            ("clip", np.clip),
            ("hypot", np.hypot),
            ("mod", np.mod),
            ("round", np.round),
            # Functions that generate floats
            ("average", np.average),
            ("mean", np.mean),
            ("median", np.median),
            ("dot", np.dot),
            # Functions that generate arrays
            ("array", np.array),
            ("cumprod", np.cumprod),
            ("cumsum", np.cumsum),
            ("arange", np.arange),
            ("diff", np.diff),  # Returns an N-1 length array
            ("interp", np.interp),
            ("linspace", np.linspace),
            ("ones", np.ones),
            ("sort", np.sort),
            ("zeros", np.zeros),
            # Random
            ("random", np.random.random),
            ("uniform", np.random.uniform),
            ("normal", np.random.normal),
            # Just all of numpy
            ("np", np),
        )
    )

    conflicts = set(safe_dict.keys()) & set(source.keys())
    if len(conflicts) != 0:
        raise KeyError(
            "Series naming conflict with built-in functions:\n{0}".format(conflicts)
        )

    safe_dict.update(source)

    try:
        series = eval(eval_str, {}, safe_dict)
    except:
        print("+++ Error while attempting to evaluate '{0}' +++".format(eval_str))
        raise

    return series


def gen_aliases_object(*, list_of_data):
    """
    This function creates the __aliases object that enables access to
    columns with bad column names.
    """
    obj = {}
    for dat in list_of_data:
        for column_name in dat.content.keys():
            if dat.alias is None:
                continue
            if dat.alias not in obj:
                obj[dat.alias] = {}
            obj[dat.alias][column_name] = dat.content[column_name]
    return obj


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

    def generic_warn(msg):
        sys.stderr.write("WARNING: {0}\n".format(msg))

    def clobber_warn(label):
        generic_warn("clobbering column '{0}'.".format(label))

    def remove_warn(label):
        generic_warn("removing column '{0}'.".format(label))

    a = verify_no_naming_collisions(list_of_data)
    aliases, column_names, aliased_column_names, ambiguous_requests = a

    # Load the unique columns
    unique_columns = (column_names | aliased_column_names) - ambiguous_requests
    input_source = {}

    # If there is anything named "__aliases", don't populate the special object.
    include_aliases_dict = ("__aliases" not in (column_names | aliased_column_names | ambiguous_requests))
    if include_aliases_dict:
        input_source["__aliases"] = gen_aliases_object(list_of_data=list_of_data)
    else:
        generic_warn(
            "detected column named '__aliases'."
            " Will not populate special object of same name."
        )

    for dat in list_of_data:
        for column_name in dat.content.keys():
            if column_name in unique_columns:
                input_source[column_name] = dat.content[column_name]

            if dat.alias is not None and dat.alias + column_name in unique_columns:
                input_source[dat.alias + column_name] = dat.content[column_name]

    # If no arguments are given, include every column without checking for ambiguities
    if len(args) == 0:
        for dat in list_of_data:
            if dat.namespace_only:
                continue
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
                    raise Exception("Failed to remove '{0}': not found.".format(head))
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

    # We want the namespace we were working with so that it can be used in the
    # assert statement.
    namespace = OrderedDict(input_source)
    namespace.update(output)

    return TabularFile(content=output), namespace


def read_file(filename):
    """
    This is a wrapper function around TabularFile.from_file(filename)
    and returns the dict of numpy arrays in .content.
    """
    return TabularFile.from_file(filename).content


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
    if (
        len(instructions["gather"]) == 0
        and instructions["postprocess"].action != "help"
    ):
        sys.stderr.write("WARNING: No files to read in.\n")

    if [_.filename for _ in instructions["gather"]].count("-") > 1:
        raise Exception(
            "Cannot have more than one instance of reading from stdin ('-')."
        )

    list_of_data = [
        TabularFile.from_file(_.filename, alias=_.alias) for _ in instructions["gather"]
    ]

    #
    # Doing the things that don't require processing.
    #
    if instructions["postprocess"].action == "help":
        print_help()
        return 0

    elif instructions["postprocess"].action in ["list", "headerlist"]:
        # Make sure we're only dealing with one file.
        if len(list_of_data) == 0:
            sys.stderr.write(f"ERROR: No file given - nothing to list\n")
            return 1
        elif len(list_of_data) > 1:
            sys.stderr.write(f"ERROR: Can only list one file at a time, got {len(list_of_data)}.\n")
            return 1

        if instructions["postprocess"].action == "list":
            list_of_data[0].list_headers()
        elif instructions["postprocess"].action == "headerlist":
            list_of_data[0].basic_list_headers()

        return 0

    #
    # Process
    #
    output, namespace = cat_control(list_of_data=list_of_data, args=instructions["process"])
    list_of_data = [output]

    if len(list_of_data) == 0:
        sys.stderr.write(f"WARNING: No files read in.\n")
    output_data = list_of_data[0] if len(list_of_data) > 0 else None

    #
    # Postprocess
    #

    if instructions["postprocess"].action == "print":
        # If you're trying to fix the warnings and the bad exit code
        # when this gets piped to `head`, stop trying. You can't fix
        # it. Python is just dies noisily when `head` closes the pipe.
        delimiter = "," if instructions["postprocess"].argument == ".csv" else ""
        sys.stdout.write(output_data.as_text(delimiter=delimiter))

    elif instructions["postprocess"].action == "output":
        delimiter = "," if instructions["postprocess"].argument.endswith(".csv") else ""
        with open(instructions["postprocess"].argument, "w") as F:
            F.write(output_data.as_text(delimiter=delimiter))
        sys.stderr.write(f"Wrote data to {instructions['postprocess'].argument}\n")

    elif instructions["postprocess"].action == "assert":

        # Allow for the possibility that we don't have any data to
        # operate on (like doing `thresh assert "$VAL==$OTHER_VAL"`)
        if hasattr(output_data, "content"):
            eval_data = output_data.content
        else:
            eval_data = OrderedDict()
        eval_data = namespace

        return_code = 0
        sys.stderr.write(f"Thresh - Performing assert:\n")
        for assert_statement in instructions["postprocess"].argument:
            val = eval_from_dict(
                eval_data,
                assert_statement,
            )
            return_code = max(return_code, 0 if bool(val) else 1)
            sys.stderr.write(
                f"{repr(assert_statement)} --> {repr(val)}\n"
                f"    Evaluated to {repr(val)} and {bool(val)} when converted to a boolean.\n"
                f"    Assert {'PASS' if bool(val) else 'FAIL'}\n"
            )
        sys.stderr.write(f"Exiting with return code {return_code}.\n")
        return return_code

    elif instructions["postprocess"].action == "burst":
        raise NotImplementedError("'burst' not implemented.")

    else:
        raise Exception(
            f"Postprocessing step not recognized:"
            f" action={repr(instructions['postprocess'].action)}"
            f" argument={repr(instructions['postprocess'].argument)}"
        )

    return 0


if __name__ == "__main__":
    retcode = main(sys.argv[1:])
    sys.exit(retcode)
