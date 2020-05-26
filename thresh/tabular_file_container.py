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
TODO
"""
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

        return "\n".join(lines)


    @classmethod
    def from_file(cls, filename, alias=None):
        """
        Read in a text-delimited or comma-delimited text file
        and return the corresponding TabularFile object.
        """

        # Convert the filename to a string
        if isinstance(filename, str):
            str_filename = filename
        elif (isinstance(filename, pathlib.PosixPath) or
              isinstance(filename, pathlib.WindowsPath)):
            str_filename = str(filename)
        else:
            # Unknown input. Raise exception.
            raise TypeError("Unrecognized input: {0}".format(repr(filename)))

        # Set the alias to None if it is not given
        alias = None if alias is None else str(alias)

        # If .csv then comma-separated, otherwise whitespace-delimited
        delimiter = ',' if str_filename[-4:].lower() == ".csv" else None

        # Read the headers (first line)
        with open(str_filename, 'r') as fobj:
            head = fobj.readline().rstrip().split(delimiter)

        # Verify that all headers are unique
        if len(head) != len(set(head)):
            raise KeyError("Non-unique headers detected in " + str_filename)

        # Read the data
        data = np.loadtxt(str_filename, skiprows=1,
                          unpack=True, delimiter=delimiter)

        # Put it together
        content = OrderedDict(zip(head, data))

        return cls(content=content, alias=alias)
