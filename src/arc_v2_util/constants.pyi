from pathlib import Path
from typing import TypeVar

from wrapt import BaseObjectProxy

T = TypeVar("T")


class Constant(BaseObjectProxy[T]):
    @property
    def name(self) -> str: ...

    @property
    def default(self) -> T: ...

    @property
    def type(self) -> type[T]: ...

    @property
    def value(self) -> T: ...

    def __init__(
        self,
        *,
        default: T,
        type: type[T] | None = ..., 
        auto_conversion: bool = ...,
    ) -> None: ...

    def to_path(self, expand: bool = ...) -> Path: ...
