from __future__ import annotations

import builtins
import inspect
import os
from os.path import expanduser, expandvars
from pathlib import Path
from typing import TypeVar, cast

import wrapt
from dotenv import load_dotenv
from typing_extensions import override

from arc_v2_util.errors import ConstantTypeError

T = TypeVar("T")

_ = load_dotenv()


class Constant(wrapt.BaseObjectProxy[T]):
    """A typed constant that proxies its resolved native value.

    The constant name is inferred from the variable receiving the instance.
    If an environment variable with that name exists, its value is converted
    to the declared or inferred type. Otherwise, ``default`` is used.

    When ``type`` is supplied, ``default`` must already have that type unless
    ``auto_conversion=True``. Automatic conversion requires an explicit type.

    The object behaves like its wrapped value for common operations while
    retaining ``name``, ``default``, ``type``, ``value``, and ``to_path()``.
    For example::

        PORT = Constant(default="8080", type=int, auto_conversion=True)
        server.start(PORT + 1)
        print(PORT.name, PORT.default, PORT.value)

    Because this is a proxy, it cannot pass *every* exact native-type check.
    For example, ``type(PORT) is int`` remains false, although
    ``isinstance(PORT, int)`` is supported by wrapt's object proxy.
    """

    _self_name: str
    _self_default: T
    _self_type: type[T]

    def __init__(
        self,
        *,
        default: T,
        type: type[T] | None = None,
        auto_conversion: bool = False,
    ) -> None:
        name = self._find_name()

        if auto_conversion and type is None:
            raise ConstantTypeError(
                f"Constant {name!r} requires an explicit type "
                "when auto_conversion=True.",
                hint="Provide type=int, type=str, or another target type.",
            )

        if type is not None and not isinstance(default, type):
            if not auto_conversion:
                raise ConstantTypeError(
                    f"Constant {name!r} has an invalid default: "
                    f"default is {builtins.type(default).__name__}, "
                    f"but explicitly declared type is {type.__name__}.",
                    hint=(
                        f"Make the default a {type.__name__}, or enable "
                        "auto_conversion=True."
                    ),
                )

            try:
                default = type(default)  # pyright: ignore[reportCallIssue]
            except (ValueError, TypeError, OverflowError) as exc:
                raise ConstantTypeError(
                    f"Cannot convert the default of Constant "
                    f"{name!r} to {type.__name__}: {exc}",
                    hint=(f"Provide a value that can be converted to {type.__name__}."),
                ) from exc

        target_type = type or builtins.type(default)

        # The _self_ prefix tells wrapt to store these on the proxy itself
        # instead of forwarding assignments to the wrapped native value.
        self._self_name = name
        self._self_default = default
        self._self_type = target_type

        # Initialise the base proxy with the fully resolved native value.
        # Calling _resolve() before super().__init__ is safe because it uses
        # only the metadata stored above, not __wrapped__.
        super().__init__(self._resolve())

    @property
    def name(self) -> str:
        """Name of the variable receiving this constant."""
        return self._self_name

    @property
    def default(self) -> T:
        """Default value after any configured automatic conversion."""
        return self._self_default

    @property
    def type(self) -> type[T]:
        """Type used to convert environment variable values."""
        return self._self_type

    @property
    def value(self) -> T:
        """Resolved native value; available for explicit access when needed."""
        return cast(T, self.__wrapped__)

    def _find_name(self) -> str:
        frame = inspect.currentframe()

        if frame is None or frame.f_back is None or frame.f_back.f_back is None:
            raise RuntimeError("Could not determine Constant name")

        caller = frame.f_back.f_back

        try:
            context = inspect.getframeinfo(caller).code_context
            if not context:
                raise RuntimeError("Could not determine Constant name")

            line = context[0].strip()
            name = line.split("=", 1)[0].strip()

            if not name.isidentifier():
                raise RuntimeError(f"Could not determine Constant name from {line!r}")

            return name
        finally:
            del frame

    def _resolve(self) -> T:
        raw = os.getenv(self.name)
        if raw is None:
            return self.default
        return self._convert(raw)

    def _convert(self, value: str) -> T:
        if self.type is bool:
            converted = value.strip().lower() in {"1", "true", "yes", "on"}
        else:
            try:
                converted = self.type(value)  # pyright: ignore[reportCallIssue]
            except (TypeError, ValueError, OverflowError) as exc:
                raise ConstantTypeError(
                    f"Invalid value for constant {self.name!r}: "
                    f"{value!r} cannot be converted to {self.type.__name__}.",
                    hint=(
                        f"Use {self.name}.value to access the resolved value, "
                        f"or explicitly cast it with {self.type.__name__}({self.name})."
                    ),
                ) from exc

        if not isinstance(converted, self.type):
            raise ConstantTypeError(
                f"Invalid value for constant {self.name!r}: "
                f"expected type {self.type.__name__}, "
                f"but got {builtins.type(converted).__name__}."
            )

        return cast(T, converted)

    @override
    def __str__(self) -> str:
        return str(self.value)

    @override
    def __repr__(self) -> str:
        return repr(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    def __int__(self) -> int:
        return int(self.value)  # pyright: ignore[reportArgumentType]

    def __float__(self) -> float:
        return float(self.value)  # pyright: ignore[reportArgumentType]

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, wrapt.BaseObjectProxy):
            other = other.__wrapped__
        return self.value == other

    @override
    def __hash__(self) -> int:
        return hash(self.value)

    def to_path(self, expand: bool = True) -> Path:
        """Convert a string constant to ``Path``, optionally expanding it."""
        if not isinstance(self.value, str):
            raise ConstantTypeError("Only type string can be converted to path!")

        path_value = cast(str, self.value)
        if expand:
            path_value = expandvars(expanduser(path_value))
        return Path(path_value)
