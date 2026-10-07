from __future__ import annotations

import builtins
import inspect
import os
from os.path import expanduser, expandvars
from pathlib import Path
from typing import Any, Generic, TypeVar, cast

from dotenv import load_dotenv
from typing_extensions import override

from arc_v2_util.errors import ConstantTypeError

T = TypeVar("T")

_ = load_dotenv()


class Constant(Generic[T]):
    default: T
    type: type[T]
    name: str
    value: T

    def __init__(
        self,
        *,
        default: T,
        type: type[T] | None = None,
    ) -> None:
        self.name = self._find_name()
        self.default = default

        if type is not None and not isinstance(default, type):
            raise ConstantTypeError(
                f"Constant {self.name!r} has an invalid default: "
                f"default is {builtins.type(default).__name__}, "
                f"but explicitly declared type is {type.__name__}.",
                hint=(
                    f"Make the default a {type.__name__}, or remove "
                    f"type={type.__name__} and let Constant infer the type."
                ),
            )

        self.type = type or builtins.type(default)
        self.value = self._resolve()

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
            except (TypeError, ValueError) as exc:
                raise ConstantTypeError(
                    f"Invalid value for constant {self.name!r}: "
                    f"{value!r} cannot be converted to {self.type.__name__}.",
                    hint=(
                        f"Use {self.name}.value to access the resolved value, "
                        f"or explicitly cast it with "
                        f"{self.type.__name__}({self.name})."
                    ),
                ) from exc
        if not isinstance(converted, self.type):
            raise ConstantTypeError(
                f"Invalid value for constant {self.name!r}: "
                f"expected type {self.type.__name__}, "
                f"but got {type(converted).__name__}."
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
        return self.value == other

    @override
    def __hash__(self) -> int:
        return hash(self.value)

    def __getattr__(self, name: str) -> Any:  # pyright: ignore[reportExplicitAny, reportAny]
        return getattr(self.value, name)  # pyright: ignore[reportAny]

    def to_path(self, expand: bool = True) -> Path:
        if not isinstance(self.value, str):
            raise ConstantTypeError("Only type string can be converted to path!")

        _path = cast(str, self.value)

        if expand:
            _path = expandvars(expanduser(_path))

        return Path(_path)
