# -*- coding: utf-8 -*-
"""
The init file for the 'thresh' library.
"""
import pathlib
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

        self.content = OrderedDict(content.items())


    def list_headers(self, *, print_alias=True):
        """
        Print the list of headers and the header index of the ThreshFile. The
        header index starts at 1, not 0.
        """
        if print_alias:
            print("==> {0} <==".format(self.alias))

        for idx, key in enumerate(self.content.keys()):
            print("{0: 3d} {1:s}".format(idx+1, key))


    def as_text(self, *, delimiter=""):
        """
        Compile the contents of the ThreshFile and return as
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
        and return the corresponding ThreshFile object.
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

        # Set the alias to the filename if it is not given
        alias = str_filename if alias is None else str(alias)

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


def parse_args(args_in):
    """
    This parses the command-line inputs and organizes it in the following
    manner to be returned:

    1) list of filename to be read in
    2) a token specifying the task to be done with the files. Currently,
       the only tokens recognized are:
       * "list"  --> list headers
       * "cat"   --> cat together and output
       * "burst" --> split each column into its own file
    """

    # Make a copy of the input args
    args = [_ for _ in args_in]

    # Check if help is requested:
    if len(args) == 0 or "-h" in args or "--help" in args:
        return [], "help"

    files_to_be_read = []
    task = None
    while len(args) > 0:

        # Extract the argument
        arg = args.pop(0)

        if task is None:
            # Only files or the task can be defined while task is None
            if arg.lower() in ["list", "cat", "burst"]:
                task = arg.lower()
                break
            elif pathlib.Path(arg).is_file():
                files_to_be_read.append(arg)
            else:
                raise FileNotFoundError("File not found: " + arg)
        else:
            # Nothing should exist after the task (until it is implemented)
            break

    # If no files were defined
    if len(files_to_be_read) == 0:
        raise Exception("No files given to process.")

    # If no task was requested
    if task is None:
        raise Exception("No task requested.")

    # If all the args were not processed
    if len(args) > 0:
        raise Exception("Unused arguments following '{0}'.".format(task))

    return files_to_be_read, task


def main(args):
    """
    This is the main function which takes the command-line arguments and
    does all the work.
    """

    # Parse the given arguments.
    files_to_be_read, task = parse_args(args)

    # Read in the files and store them.
    list_of_data = [ThreshFile.from_file(_) for _ in files_to_be_read]

    # Perform the desired task.
    if task == 'list':
        for obj in list_of_data:
            obj.list_headers()
    elif task == 'cat':
        raise NotImplementedError("'cat' not implemented.")
    elif task == 'burst':
        raise NotImplementedError("'burst' not implemented.")
    else:
        raise Exception("Task not recognized: '{0}'.".format(task))
    

