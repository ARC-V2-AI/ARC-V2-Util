import os
from pathlib import Path

import pytest

from arc_v2_util.constants import Constant
from arc_v2_util.errors import ConstantTypeError


def test_defaults_and_inferred_types() -> None:
    port = Constant(default=3882)
    debug = Constant(default=False)
    name = Constant(default="arc")
    rate = Constant(default=2.5)

    assert port.value == 3882
    assert isinstance(port.value, int)

    assert debug.value is False
    assert isinstance(debug.value, bool)

    assert name.value == "arc"
    assert isinstance(name.value, str)

    assert rate.value == 2.5
    assert isinstance(rate.value, float)


def test_environment_override() -> None:
    os.environ["PORT_ENV_TEST"] = "9999"

    try:
        PORT_ENV_TEST = Constant(default=3882)

        assert PORT_ENV_TEST.name == "PORT_ENV_TEST"
        assert PORT_ENV_TEST.value == 9999
        assert isinstance(PORT_ENV_TEST.value, int)
    finally:
        del os.environ["PORT_ENV_TEST"]


def test_boolean_parsing() -> None:
    os.environ["DEBUG_ENV_TEST"] = "true"

    try:
        DEBUG_ENV_TEST = Constant(default=False)
        assert bool(DEBUG_ENV_TEST) is True
    finally:
        del os.environ["DEBUG_ENV_TEST"]


def test_boolean_false_parsing() -> None:
    os.environ["DEBUG_ENV_TEST_FALSE"] = "0"

    try:
        DEBUG_ENV_TEST_FALSE = Constant(default=True)
        assert DEBUG_ENV_TEST_FALSE.value is False
    finally:
        del os.environ["DEBUG_ENV_TEST_FALSE"]


def test_explicit_matching_type() -> None:
    count = Constant(default=42, type=int)

    assert count.value == 42
    assert isinstance(count.value, int)


def test_explicit_type_mismatch() -> None:
    with pytest.raises(ConstantTypeError):
        STRING_INT_FAIL = Constant(default="42", type=int)

    with pytest.raises(ConstantTypeError):
        INT_STRING_FAIL = Constant(default=42, type=str)

    with pytest.raises(ConstantTypeError):
        FLOAT_INT_FAIL = Constant(default=2.5, type=int)


def test_to_path() -> None:
    os.environ["PATH_ENV_TEST"] = "~/arc/$TEST_DIR"
    os.environ["TEST_DIR"] = "memory"

    try:
        PATH_ENV_TEST = Constant(default="~/arc/$TEST_DIR")

        path = PATH_ENV_TEST.to_path()

        assert path == Path.home() / "arc" / "memory"
    finally:
        del os.environ["PATH_ENV_TEST"]
        del os.environ["TEST_DIR"]
