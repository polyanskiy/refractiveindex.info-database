"""Tests that all files can be parsed."""

import pathlib
import unittest
import yaml
from parameterized import parameterized

DATABASE_PATH = pathlib.Path(__file__).resolve().parent.parent / "database"
PATHS = list(DATABASE_PATH.rglob("*.yml"))


def custom_name_func(testcase_func, param_num, param):
    del param_num
    path = str(param.args[0])
    return f"{testcase_func.__name__}{parameterized.to_safe_name(path)}"


class ParseTest(unittest.TestCase):
    @parameterized.expand(PATHS, name_func=custom_name_func)
    def test_can_parse(self, path):
        with open(path, "r") as stream:
            yaml.safe_load(stream)
