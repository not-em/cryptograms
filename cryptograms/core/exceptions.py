"""Custom exceptions for cryptogram solving."""


class CryptogramError(Exception):
    """Base exception for cryptogram-related errors."""

    pass


class InvalidPuzzleError(CryptogramError):
    """Raised when a puzzle is malformed or invalid."""

    pass


class UnsolvableError(CryptogramError):
    """Raised when no valid solution can be found."""

    pass
