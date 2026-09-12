class ConstantTypeError(TypeError):
    """Raised when a Constant value does not match its declared type."""

    def __init__(
        self,
        message: str,
        *,
        hint: str | None = None,
    ) -> None:
        if hint is not None:
            message = f"{message}\nHint: {hint}"

        super().__init__(message)


class ARCUtilError(Exception):
    pass


class RetryError(ARCUtilError):
    pass
