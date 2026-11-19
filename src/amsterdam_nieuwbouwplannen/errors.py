from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.problem import ProblemDetails

__all__ = (
    "BadRequest",
    "Forbidden",
    "HTTPException",
    "NieuwbouwplannenError",
    "NotFound",
    "RateLimited",
    "ServerError",
    "Unauthorized",
)


class NieuwbouwplannenError(Exception):
    """Base exception of this library."""


class HTTPException(NieuwbouwplannenError):
    """The API answered with a non-2xx status.

    Attributes
    ----------
    status: :class:`int`
        HTTP response status code.
    problem: :class:`~amsterdam_nieuwbouwplannen.ProblemDetails` | :obj:`None`
        Decoded API problem details, if available.
    body: :class:`bytes`
        Raw HTTP response body.
    """

    def __init__(self, status: int, problem: ProblemDetails | None, body: bytes) -> None:
        """Build the exception message from the response status and problem.

        Parameters
        ----------
        status: :class:`int`
            HTTP response status code.
        problem: :class:`~amsterdam_nieuwbouwplannen.ProblemDetails` | :obj:`None`
            Decoded API problem details, if available.
        body: :class:`bytes`
            Raw HTTP response body.
        """

        self.status: int = status
        self.problem: ProblemDetails | None = problem
        self.body: bytes = body
        message = f"{status}"
        if problem is not None:
            if problem.title:
                message += f" {problem.title}"
            if isinstance(problem.detail, str) and problem.detail:
                message += f": {problem.detail}"
        super().__init__(message)


class BadRequest(HTTPException):
    """Report an invalid request, usually a filter or field name.

    See :attr:`~amsterdam_nieuwbouwplannen.ProblemDetails.invalid_params` for rejected parameters.
    """


class Unauthorized(HTTPException):
    """401, the access token is missing or invalid."""


class Forbidden(HTTPException):
    """403, the token lacks the scope for this table (``BB/WB/GO/STAN`` / ``BB/WB/GO/UITG``)."""


class NotFound(HTTPException):
    """404, no record with that id."""


class RateLimited(HTTPException):
    """429, too many requests."""


class ServerError(HTTPException):
    """5xx."""
