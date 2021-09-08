#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
# # Copyright (c) 2016
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
TODO
"""
import sys
import json
import pprint
import keyword
import pathlib
import numpy as np
from collections import OrderedDict


class TabularFile:
    """
    The basic representation of tabular files.
    """

    def __init__(self, *, content=None, alias=None, name=None, namespace_only=False, length_check=True):
        """
        A file, as represented in thresh, requires only two descriptors, the
        alias and the data itself. As the data has headers and columns it only
        seemed reasonable to store it as an OrderedDict of Numpy arrays.

        self.name = str or None
        self.alias = str or None
        self.content = OrderedDict((
                       ('Column1', np.array([ 0.0, 1.0, 2.0])),
                       ('Column2', np.array([ 1.2, 1.1, 1.0])),
                       ('Column3', np.array([-3.0, 1.4, 1.5])),
                                   )) or None
        """

        if not isinstance(namespace_only, bool):
            raise TypeError(f"`namespace_only` must be of type bool, not {type(namespace_only)}.")
        self.namespace_only = namespace_only

        if not isinstance(length_check, bool):
            raise TypeError(f"`length_check` must be of type bool, not {type(length_check)}.")
        self.length_check = length_check

        # Process 'content'. If 'None', initialize an empty OrderedDict
        if content is None:
            content = OrderedDict()

        # Process 'alias'. Must be either 'str' or 'None'
        if not isinstance(alias, str) and alias is not None:
            raise TypeError(
                "Variable 'alias' is not of type str or None: {0}".format(type(alias))
            )
        if isinstance(alias, str):
            if keyword.iskeyword(alias):
                raise SyntaxError(
                    "Alias can not be a python keyword. Got: {0}".format(repr(alias))
                )
            if not alias.isidentifier():
                raise SyntaxError(
                    "Alias must be a valid python identifier. Got: {0}".format(repr(alias))
                )

        self.alias = alias

        # Process 'name'. Must be either 'str' or 'None'
        if not isinstance(name, str) and name is not None:
            raise TypeError(
                "Variable 'name' is not of type str or None: {0}".format(type(name))
            )
        self.name = name

        # 'content' must be 'OrderedDict'
        if not isinstance(content, OrderedDict):
            raise TypeError(
                "Variable 'content' is not an OrderedDict: {0}".format(repr(content))
            )

        # All the keys in 'content' must be 'str'
        if not all([isinstance(_, str) for _ in content.keys()]):
            raise KeyError(
                "Variable 'content' has non-string key(s): {0}".format(
                    list(content.keys())
                )
            )

        # All values in 'content' must have the same length.
        if self.length_check and len(content) > 0 and len(set([len(_) for _ in content.values()])) != 1:
            raise IndexError(
                "arrays in 'content' have varying lengths: {0}".format(
                    [len(_) for _ in content.values()]
                )
            )

        self.content = OrderedDict(content.items())

    def list_headers(self):
        """
        Print the list of headers and the header index of the TabularFile. The
        header index starts at 1, not 0.
        """

        try:
            lines = [f"{'col':>4s} | {'length':>6s} | {'header':<s}"]
            lines.append("-" * len(lines[0]))
            for idx, key in enumerate(self.content.keys()):
                lines.append(f"{idx: 4d} | {len(self.content[key]): 6d} | {key:s}")
        except Exception as exc:

            obj_types = [[str(key), type(val).__name__] for key, val in self.content.items()]
            header_len = max([len(_[0]) for _ in obj_types]) + 1
            type_len = max([len(_[1]) for _ in obj_types]) + 1

            lines = [f"{'name':>{header_len}s} | {'type':>{type_len}s}"]
            lines.append("-" * len(lines[0]))
            for key, val in obj_types:
                lines.append(f"{key:>{header_len}s} | {val:>{type_len}s}")
        print("\n".join(lines))

    def basic_list_headers(self):
        """
        Print all the headers, one per line. This minimally-formatted option
        enables looping over headers in bash for-loops and other scripting
        fun.
        """
        for key in self.content.keys():
            print(key)

    def as_text(self, *, delimiter=""):
        """
        Compile the contents of the TabularFile and return as
        text. This allows easy uniform printing to the terminal
        or to a file.
        """

        if not self.length_check:
            return json.dumps(dict(self.content))

        # Requres 17 digits to prefectly re-create a double in-memory.
        n_chars_decimal = 17
        len_biggest_number = len("+1." + n_chars_decimal * "0" + "e+301")

        # Ensure that the columns are wide enough for the longest header.
        len_biggest_header = max(map(len, self.content.keys()))
        n_chars_per_column = max(len_biggest_number, len_biggest_header) + 1

        strfmt = "{0:>" + str(n_chars_per_column) + "s}"
        fltfmt = "{0:+" + str(n_chars_per_column) + "." + str(n_chars_decimal) + "e}"

        lines = []
        # Format the headers.
        lines.append(delimiter.join(strfmt.format(_) for _ in self.content))

        # Format the data lines
        keys = list(self.content.keys())
        for idx in range(len(self.content[keys[0]])):
            lines.append(
                delimiter.join(fltfmt.format(self.content[_][idx]) for _ in keys)
            )

        return "\n".join(lines) + "\n"

    @classmethod
    def format_if_history_file(cls, lines):
        """
        Look to see if it's formatted like a history file. If it is, then
        remove the comments at the top (if any) and then remove the two
        horizontal rules above and below the headers.

          Comments can go here
          Comments can go here
          ---------
          col1 col2
          =========
             1    2
             3    4
        """
        lines_lengths = [len(_) for _ in lines]
        lines_sets = [set(_) for _ in lines]

        # Look for two lines that are nothing but '-' or '='.
        if {"-", "\n"} not in lines_sets or {"=", "\n"} not in lines_sets:
            return lines

        # We are looking to grab the last set of '-' and '=' rules.
        N = len(lines_sets)
        top_idx = (N - 1) - list(reversed(lines_sets)).index({"-", "\n"})
        bottom_idx = (N - 1) - list(reversed(lines_sets)).index({"=", "\n"})

        # Those two lines must have one line between them (where the
        # headers go).
        if bottom_idx - top_idx != 2:
            return lines

        # The lengths of the top rule, bottom rule, and headers must
        # be the same.
        if len(set(lines_lengths[top_idx : bottom_idx + 1])) != 1:
            return lines

        # It is a history file - remove the extra lines.
        lines.pop(bottom_idx)
        for idx in range(top_idx + 1):
            lines.pop(0)

        return lines

    @classmethod
    def from_file(cls, filename, alias=None):
        """
        Read in a text-delimited or comma-delimited text file
        and return the corresponding TabularFile object.
        """

        # Convert the filename to a Path if it isn't already.
        if isinstance(filename, str):
            path_filename = pathlib.Path(filename)
        elif isinstance(filename, pathlib.Path):
            path_filename = filename
        else:
            raise TypeError(
                f"Argument 'filename' must be str or Path, not {type(filename)}"
            )

        # Set the alias to None if it is not given
        if alias is not None and not isinstance(alias, str):
            raise TypeError(f"Argument 'alias' must be None or str, not {type(alias)}")

        if path_filename.suffix.lower() == ".json":
            if str(path_filename).lower() == "-.json":
                json_data = json.load(sys.stdin)
            else:
                with open(path_filename, "r") as stream:
                    json_data = json.load(stream)
            if not isinstance(json_data, dict):
                raise TypeError(f"JSON data must be a dict, not {type(json_data)}.")
            return cls(
                content=OrderedDict(json_data),
                alias=alias,
                name=str(filename),
                namespace_only=True,
                length_check=False,
            )

        elif path_filename.suffix.lower() == ".csv":
            # Comma delimited text
            delimiter = ","
            if str(path_filename).lower() == "-.csv":
                lines = sys.stdin.readlines()
            else:
                with path_filename.open() as fobj:
                    lines = fobj.readlines()

        else:
            # whitespace delimited text.
            delimiter = None
            if str(path_filename) == "-":
                lines = sys.stdin.readlines()
            else:
                with path_filename.open() as fobj:
                    lines = fobj.readlines()

        lines = cls.format_if_history_file(lines)
        head = lines[0].rstrip().split(delimiter)
        head = [_.strip() for _ in head]

        def can_convert_to_float(x):
            try:
                float(x)
            except:
                return False
            return True

        if all([can_convert_to_float(_) for _ in head]):
            sys.stderr.write(
                f"WARNING: No headers detected in '{filename}'. Using auto-generated ones.\n"
            )
            head = [f"column_{_:d}" for _ in range(len(head))]

        # Verify that all headers are unique
        if len(head) != len(set(head)):
            raise KeyError(f"Non-unique headers detected in {path_filename}")

        # Read the data
        data = np.genfromtxt(lines, skip_header=1, unpack=True, delimiter=delimiter)
        if len(data.shape) == 1:
            # One column of data (1D). Need to make the array 2D.
            data = np.array([data,])

        # Put it together
        content = OrderedDict(zip(head, data))

        return cls(content=content, alias=alias, name=str(filename))
