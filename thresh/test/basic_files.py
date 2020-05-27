"""
This file contains the basic files used to benchmark *thresh*.
"""
from collections import OrderedDict
import numpy as np

base_files = {
    "pass_a.txt": [
        (
            "a b c\n"
            "7 8 2\n"
            "0 5 0\n"
            "1 2 3\n"
            "3 4 5\n"
            "7 1 4\n"
        ),
        OrderedDict((
            ("a", np.array([7, 0, 1, 3, 7], dtype=float)),
            ("b", np.array([8, 5, 2, 4, 1], dtype=float)),
            ("c", np.array([2, 0, 3, 5, 4], dtype=float)),
        ))
    ],
    "pass_b.txt": [
        (
            "d e f\n"
            "5 6 6\n"
            "1 7 4\n"
            "3 1 2\n"
            "2 3 4\n"
            "1 8 5\n"
        ),
        OrderedDict((
            ("d", np.array([5, 1, 3, 2, 1], dtype=float)),
            ("e", np.array([6, 7, 1, 3, 8], dtype=float)),
            ("f", np.array([6, 4, 2, 4, 5], dtype=float)),
        ))
    ],
    "pass_c.csv": [
        (
            "g,h,i\n"
            "4,0,1\n"
            "8,3,2\n"
            "7,8,5\n"
            "4,6,2\n"
            "4,8,5\n"
        ),
        OrderedDict((
            ("g", np.array([4, 8, 7, 4, 4], dtype=float)),
            ("h", np.array([0, 3, 8, 6, 8], dtype=float)),
            ("i", np.array([1, 2, 5, 2, 5], dtype=float)),
        ))
    ],
    "pass_d.csv": [
        (
            "This is a comment and should be thrown away.\n"
            "-----\n"
            "g,h,i\n"
            "=====\n"
            "4,0,1\n"
            "8,3,2\n"
            "7,8,5\n"
            "4,6,2\n"
            "4,8,5\n"
        ),
        OrderedDict((
            ("g", np.array([4, 8, 7, 4, 4], dtype=float)),
            ("h", np.array([0, 3, 8, 6, 8], dtype=float)),
            ("i", np.array([1, 2, 5, 2, 5], dtype=float)),
        ))
    ],
}


fail_files = {
    "fail_nonunique_headers.txt": [
        (
            "a a c\n"
            "7 8 2\n"
            "0 5 0\n"
            "1 2 3\n"
            "3 4 5\n"
            "7 1 4\n"
        ),
    ]
}
