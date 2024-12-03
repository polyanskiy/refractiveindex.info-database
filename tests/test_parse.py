"""Tests that all files can be parsed.

This test can be run by the command

    pytest tests/test_parse.py

or simply `pytest` from the repo directory. (The latter will automatically discover
all test files.) This test recursively discovers all `.yml` files in the `database`
directory and then loads them with the python `yaml` package.

A test is generated individually for each `.yml` file, with the test name derived from
the `.yml` file path. For example, the test for file `database/data/nk/main/KBr/Li.yml`
will be `test_can_parase_database_data_nk_main_KBr_Li_yml`.
"""

import pathlib
import unittest
import yaml
from parameterized import parameterized

# Discover the paths for all `.yml` files.
DATABASE_PATH = pathlib.Path(__file__).resolve().parent.parent / "database"
PATHS = list(DATABASE_PATH.rglob("*.yml"))


def custom_name_func(testcase_func, param_num, param):
    # Generate the custom test name from the test arguments.
    del param_num
    path = str(param.args[0])
    path = path.replace("\\", "/")  # On windows, directories are separated by `\`.
    assert "/database/" in path
    path = path[path.index("/database/") :]
    return f"{testcase_func.__name__}{parameterized.to_safe_name(path)}"


class ParseTest(unittest.TestCase):
    @parameterized.expand(PATHS, name_func=custom_name_func)
    def test_can_parse(self, path):
        with open(path, "r", encoding="utf-8") as stream:
            yaml.safe_load(stream)
