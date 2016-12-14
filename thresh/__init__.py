# -*- coding: utf-8 -*-
"""
The init file for the 'thresh' library.
"""
from collections import OrderedDict
import numpy as np

__version__ = (0, 0, 1)


class ThreshFile:
    """
    The basic representation of tabular files.
    """

    def __init__(self, *, content, alias=None):
        """
        A file, as represented in thresh, requires only two descriptors, the
        alias and the data itself. As the data has headers and columns it only
        seemed reasonable to store it as an OrderedDict of Numpy arrays.

        self.alias = str or None
        self.content = OrderedDict((
                       ('Column1', np.array([ 0.0, 1.0, 2.0])),
                       ('Column2', np.array([ 1.2, 1.1, 1.0])),
                       ('Column3', np.array([-3.0, 1.4, 1.5])),
                                   ))
        """

        # Process 'alias'
        if not isinstance(alias, str) and alias is not None:
            raise TypeError("Variable 'alias' is not of type str or None: {0}"
                            .format(type(alias)))
        self.alias = alias

        # Consistency checks on variable 'content'
        if not isinstance(content, OrderedDict):
            raise TypeError("Variable 'content' is not an OrderedDict: {0}"
                            .format(repr(content)))

        if not all([isinstance(_, str) for _ in content.keys()]):
            raise KeyError("Variable 'content' has non-string key(s): {0}"
                           .format(list(content.keys())))

        if len(set([len(_) for _ in content.values()])) != 1:
            raise IndexError("arrays in 'content' have varying lengths: {0}"
                             .format([len(_) for _ in content.values()]))

        self.content = content

    def list_headers(self, *, print_alias=False):
        """
        Print the list of headers and the header index of the ThreshFile. The
        header index starts at 1, not 0.
        """
        if print_alias:
            print("==> {0} <==".format(self.alias))

        for idx, key in enumerate(self.content.keys()):
            print("{0: 3d} {1:s}".format(idx+1, key))


#import pathlib
#    @classmethod
#    def from_file(cls, *, filename):
#
#        if type(filename) == str:
#            # Do something
#            str_filename = filename
#        elif type(filename) in [pathlib.PosixPath, pathlib.WindowsPath]:
#            # Do something
#            str_filename = str(filename)
#        else:
#            # Unknown input. Raise exception.
#            raise TypeError("Unrecognized input: {0}".format(repr(filename)))
#
#        # Either comma or whitespace delimited
#        delimiter = ',' if str_filename[-4:].lower() == ".csv" else None
#
#        # Read the headers
#        with open(str_filename, 'r') as F:
#            head = F.readline.rstrip().split(delimiter)
#
#        # Read the data
#        data = np.loadtxt(str_filename, skiprows=1, unpack=True, delimiter=delimiter)
#
#        # Put it together
#        content = OrderedDict(zip(head, data))
#
#        return cls(content=content)
