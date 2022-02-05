from typing import List

class ThreshParser:
    magic_words: List[str] = [
        "cat",
        "assert",
        "output",
        "burst",
        "print",
        "list",
        "headerlist",
    ]

    def __init__(self):
        self.task_gather: List[str] = []
        self.task_cat: List[str] = []
        self.task_assert: List[str] = []
        self.task_output: List[str] = []
        self.task_burst: List[str] = []
        self.task_print: List[str] = []
        self.task_list: bool = False
        self.task_headerlist: bool = False
        self.task_help: bool = False

    def __get_args(key: str, args: List[str]):
        """
        get the arguments associated with a given key. For example:

        >>> args = ["foo", "cat", "bar", "baz", "assert", "fizz"]
        >>> __get_args("gather", args)
        ["foo"]
        >>> __get_args("cat", args)
        ["bar", "baz"]
        >>> __get_args("assert", args)
        ["fizz"]
        """
        
