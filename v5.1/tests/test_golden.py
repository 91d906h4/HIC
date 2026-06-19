"""Golden regression tests: the example programs must keep their outputs."""

import os

import pytest

from .conftest import EXAMPLES_DIR, run_file

GOLDEN = [
    ("fibonacci.hy", ["55", "55"]),
    ("math.hy", ["100", "1024", "10"]),
    ("perceptron.hy", ["true"]),
    ("arrays_strings.hy", [
        "[0, 1, 4, 9, 16, 25, 36, 49]",
        "49",
        "Hello, world!",
        "18",
        "16",
        "true",
        "true",
    ]),
]


@pytest.mark.parametrize("filename,expected", GOLDEN)
@pytest.mark.parametrize("roundtrip", [False, True], ids=["direct", "hyb"])
def test_golden(filename, expected, roundtrip):
    path = os.path.join(EXAMPLES_DIR, filename)
    assert run_file(path, roundtrip=roundtrip) == expected
