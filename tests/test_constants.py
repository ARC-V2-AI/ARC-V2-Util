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


def test_explicit_type_mismatch_without_auto_conversion() -> None:
    with pytest.raises(ConstantTypeError):
        STRING_INT_FAIL = Constant(default="42", type=int)

    with pytest.raises(ConstantTypeError):
        INT_STRING_FAIL = Constant(default=42, type=str)

    with pytest.raises(ConstantTypeError):
        FLOAT_INT_FAIL = Constant(default=2.5, type=int)


def test_auto_conversion_of_default() -> None:
    STRING_TO_INT = Constant(default="42", type=int, auto_conversion=True)
    INT_TO_STRING = Constant(default=42, type=str, auto_conversion=True)
    FLOAT_TO_INT = Constant(default=2.5, type=int, auto_conversion=True)

    assert STRING_TO_INT.default == 42
    assert STRING_TO_INT.value == 42
    assert isinstance(STRING_TO_INT.value, int)

    assert INT_TO_STRING.default == "42"
    assert INT_TO_STRING.value == "42"
    assert isinstance(INT_TO_STRING.value, str)

    assert FLOAT_TO_INT.default == 2
    assert FLOAT_TO_INT.value == 2
    assert isinstance(FLOAT_TO_INT.value, int)


def test_auto_conversion_still_converts_environment_override() -> None:
    os.environ["AUTO_CONVERT_PORT_TEST"] = "9000"

    try:
        AUTO_CONVERT_PORT_TEST = Constant(
            default="8080", type=int, auto_conversion=True
        )

        assert AUTO_CONVERT_PORT_TEST.default == 8080
        assert AUTO_CONVERT_PORT_TEST.value == 9000
        assert isinstance(AUTO_CONVERT_PORT_TEST.value, int)
    finally:
        del os.environ["AUTO_CONVERT_PORT_TEST"]


def test_auto_conversion_requires_explicit_type() -> None:
    with pytest.raises(ConstantTypeError, match="requires an explicit type"):
        AUTO_CONVERSION_NO_TYPE = Constant(default="42", auto_conversion=True)


def test_auto_conversion_invalid_default_raises_constant_type_error() -> None:
    with pytest.raises(ConstantTypeError, match="Cannot convert the default"):
        INVALID_AUTO_CONVERSION = Constant(
            default="not-an-int", type=int, auto_conversion=True
        )


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


def test_constant_behaves_like_wrapped_native_value() -> None:
    PORT = Constant(default=8080, type=int)
    APP_NAME = Constant(default="arc")
    DEBUG = Constant(default=True)

    assert PORT + 1 == 8081
    assert PORT > 1000
    assert isinstance(PORT, int)
    assert str(PORT) == "8080"
    assert repr(PORT) == "8080"
    assert bool(DEBUG) is True
    assert APP_NAME.upper() == "ARC"
    assert APP_NAME == "arc"


def test_proxy_preserves_constant_metadata_and_helpers() -> None:
    APP_NAME = Constant(default="arc", type=str)
    DATA_PATH = Constant(default="~/arc-data", type=str)

    assert APP_NAME.name == "APP_NAME"
    assert APP_NAME.default == "arc"
    assert APP_NAME.type is str
    assert APP_NAME.value == "arc"
    assert DATA_PATH.to_path(expand=False) == Path("~/arc-data")
    assert DATA_PATH.to_path() == Path.home() / "arc-data"
