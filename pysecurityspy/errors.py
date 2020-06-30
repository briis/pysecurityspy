"""Define package errors."""


class SecuritySpyError(Exception):
    """Define a base error."""

    pass


class InvalidCredentials(SecuritySpyError):
    """Define an error related to invalid or missing Credentials."""

    pass


class RequestError(SecuritySpyError):
    """Define an error related to invalid requests."""

    pass

class ResultError(SecuritySpyError):
    """Define an error related to the result returned from a request."""

    pass
