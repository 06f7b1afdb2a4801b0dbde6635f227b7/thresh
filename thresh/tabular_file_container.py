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
import pathlib
import numpy as np
from collections import OrderedDict

class TabularFile:
    """
    The basic representation of tabular files.
    """

    def __init__(self, *, content=None, alias=None):
        """
        A file, as represented in thresh, requires only two descriptors, the
        alias and the data itself. As the data has headers and columns it only
        seemed reasonable to store it as an OrderedDict of Numpy arrays.

        self.alias = str or None
        self.content = OrderedDict((
                       ('Column1', np.array([ 0.0, 1.0, 2.0])),
                       ('Column2', np.array([ 1.2, 1.1, 1.0])),
                       ('Column3', np.array([-3.0, 1.4, 1.5])),
                                   )) or None
        """

        # Process 'content'. If 'None', initialize an empty OrderedDict
        if content is None:
            content = OrderedDict()

        # Process 'alias'. Must be either 'str' or 'None'
        if not isinstance(alias, str) and alias is not None:
            raise TypeError("Variable 'alias' is not of type str or None: {0}"
                            .format(type(alias)))
        self.alias = alias

        # 'content' must be 'OrderedDict'
        if not isinstance(content, OrderedDict):
            raise TypeError("Variable 'content' is not an OrderedDict: {0}"
                            .format(repr(content)))

        # All the keys in 'content' must be 'str'
        if not all([isinstance(_, str) for _ in content.keys()]):
            raise KeyError("Variable 'content' has non-string key(s): {0}"
                           .format(list(content.keys())))

        # All values in 'content' must have the same length.
        if len(content) > 0 and len(set([len(_) for _ in content.values()])) != 1:
            raise IndexError("arrays in 'content' have varying lengths: {0}"
                             .format([len(_) for _ in content.values()]))

        self.content = OrderedDict(content.items())


    def list_headers(self, *, print_alias=True):
        """
        Print the list of headers and the header index of the TabularFile. The
        header index starts at 1, not 0.
        """
        if print_alias:
            print("==> {0} <==".format(self.alias))

        for idx, key in enumerate(self.content.keys()):
            print("{0: 3d} {1:s}".format(idx+1, key))


    def as_text(self, *, delimiter=""):
        """
        Compile the contents of the TabularFile and return as
        text. This allows easy uniform printing to the terminal
        or to a file.
        """
        n_chars_per_column = 23
        n_chars_decimal = n_chars_per_column - 9
        strfmt = "{0:>" + str(n_chars_per_column) + "s}"
        fltfmt = ("{0:+" + str(n_chars_per_column) +
                  "." + str(n_chars_decimal) + "e}")

        lines = []
        # Format the headers.
        lines.append(delimiter.join(strfmt.format(_) for _ in self.content))

        # Format the data lines
        keys = list(self.content.keys())
        for idx in range(len(self.content[keys[0]])):
            lines.append(delimiter.join(fltfmt.format(self.content[_][idx]) for _ in keys))

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
        if len(set(lines_lengths[top_idx:bottom_idx+1])) != 1:
            return lines

        # It is a history file - remove the extra lines.
        lines.pop(bottom_idx)
        for idx in range(top_idx+1):
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
            if filename == "-":
                # This actually means "read from stdin".
                path_filename = filename
            else:
                path_filename = pathlib.Path(filename)
        elif isinstance(filename, pathlib.Path):
            path_filename = filename
        else:
            raise TypeError(f"Argument 'filename' must be str or Path, not {type(filename)}")

        # Set the alias to None if it is not given
        if alias is not None and not isinstance(alias, str):
            raise TypeError(f"Argument 'alias' must be None or str, not {type(alias)}")


        if path_filename == "-":
            # Read the whole file in from stdin.
            delimiter = None
            lines = sys.stdin.readlines()
        else:
            # If .csv then comma-separated, otherwise whitespace-delimited
            delimiter = ',' if path_filename.suffix.lower() == ".csv" else None

            # Read the whole file in.
            with path_filename.open() as fobj:
                lines = fobj.readlines()

        lines = cls.format_if_history_file(lines)
        head = lines[0].rstrip().split(delimiter)

        # Verify that all headers are unique
        if len(head) != len(set(head)):
            raise KeyError(f"Non-unique headers detected in {path_filename}")

        # Read the data
        data = np.genfromtxt(lines, skip_header=1,
                          unpack=True, delimiter=delimiter)
        print("data", data, file=sys.stderr)

        # Put it together
        content = OrderedDict(zip(head, data))

        return cls(content=content, alias=alias)
