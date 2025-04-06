"""Tests to verify that there is a data yaml file for each entry in the catalog-nk.yml and catalog-n2.yml files,
and that all files can be parsed and conform to the expected schema.

This test can be run by the command

    pytest tests/test_yaml.py

or simply `pytest` from the repo directory. (The latter will automatically discover
all test files.)
"""

from __future__ import annotations

import pathlib
import re

import pytest
import yaml
from cerberus import Validator


# Extract all YAML paths from the catalog
def extract_paths(catalog: str | list, base_path: str = "") -> list:
    paths = []
    for item in catalog:
        if isinstance(item, dict):
            for key, value in item.items():
                if key == "data":
                    paths.append(base_path + value)
                elif key == "content":
                    paths.extend(extract_paths(value, base_path))
                elif key == "DIVIDER":
                    continue
                else:
                    paths.extend(extract_paths([value], base_path))
    return paths


# Path to the catalog files
CATALOG_ROOT_PATH = pathlib.Path(__file__).resolve().parent.parent / "database"
CATALOG_NK_PATH = CATALOG_ROOT_PATH / "catalog-nk.yml"
CATALOG_N2_PATH = CATALOG_ROOT_PATH / "catalog-n2.yml"

# Load the catalog files
with open(CATALOG_NK_PATH, "r", encoding="utf-8") as stream:
    catalog_nk = yaml.safe_load(stream)

with open(CATALOG_N2_PATH, "r", encoding="utf-8") as stream:
    catalog_n2 = yaml.safe_load(stream)

# Get all paths from the catalogs
ALL_NK_PATHS = extract_paths(catalog_nk)
ALL_N2_PATHS = extract_paths(catalog_n2)

# Define the regex pattern for URLs, this is used to validate the URLs in the YAML files
url_regex = re.compile(
    r"(?i)^(?:http|ftp)s?://"  # http:// or https://  also ignore case
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # ...or ipv4
    r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # ...or ipv6
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$"
)

# Define the schema for the YAML nk data files. This could be extended to test other levels of the yaml files and/or test
# the content of each field more thoroughly. E.g. check that temperature is a number, that 'tabulated n' is a list with two columns, etc.
schema = {
    "REFERENCES": {"type": "string", "required": True},
    "COMMENTS": {"type": "string", "required": False},
    "DATA": {"type": "list", "required": True},
    "CONDITIONS": {
        "oneof": [{"type": "string"}, {"type": "list"}, {"type": "dict"}],
        "required": False,
    },
    "PROPERTIES": {
        "oneof": [{"type": "string"}, {"type": "list"}, {"type": "dict"}],
        "required": False,
    },
}

validator = Validator(schema)

# Define the schema for the 'about.yaml' files
about_scheme = {
    "NAMES": {"type": "list", "schema": {"type": "string"}},
    "ABOUT": {"type": "string"},
    "LINKS": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "url": {"type": "string", "regex": url_regex.pattern},
                "text": {"type": "string"},
            },
        },
        "required": False,
    },
}
validator_about = Validator(about_scheme)

# Discover the paths for all `.yml` files.
DATABASE_PATH = pathlib.Path(__file__).resolve().parent.parent / "database" / "data"
ALL_YAML_FILES = list(DATABASE_PATH.rglob("*.yml"))


# Verify that each about.yml file conforms to the expected schema
@pytest.mark.parametrize(
    "yaml_file",
    ALL_YAML_FILES,
    ids=lambda x: str(x).replace(str(DATABASE_PATH), "")[1:].replace(".yml", ""),
)
def test_yaml_schema(yaml_file):
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)
        if yaml_file.name == "about.yml":
            assert validator_about.validate(data), (
                f"Schema validation failed for {yaml_file.name}: {validator_about.errors}"
            )
        else:
            assert validator.validate(data), (
                f"Schema validation failed for {yaml_file.name}: {validator.errors}"
            )


# Verify that each yaml path referenced in the catalog files exists in the database/data directory
@pytest.mark.parametrize(
    "path",
    ALL_NK_PATHS + ALL_N2_PATHS,
    ids=lambda x: str(x).replace(str(DATABASE_PATH), "").replace(".yml", ""),
)
def test_paths_exist(path):
    full_path = (
        pathlib.Path(__file__).resolve().parent.parent / "database" / "data" / path
    )
    assert full_path.exists(), f"Path does not exist: {full_path}"
