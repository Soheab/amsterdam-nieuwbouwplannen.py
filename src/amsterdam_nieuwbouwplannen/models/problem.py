from __future__ import annotations

import msgspec

__all__ = ("InvalidParam", "ProblemDetails")


class InvalidParam(msgspec.Struct, frozen=True, kw_only=True):
    """Describe a request parameter rejected by the API.

    Attributes
    ----------
    type: :class:`str` | :obj:`None`
        Type identifier supplied by the API.
    name: :class:`str` | :obj:`None`
        API name of the rejected parameter.
    reason: :class:`str` | :obj:`None`
        Explanation of why the parameter was rejected.
    """

    type: str | None = None
    name: str | None = None
    reason: str | None = None


class ProblemDetails(msgspec.Struct, frozen=True, kw_only=True):
    """RFC 7807 ``application/problem+json`` error body returned by the DSO-API.

    Attributes
    ----------
    type: :class:`str` | :obj:`None`
        Type identifier supplied by the API.
    title: :class:`str` | :obj:`None`
        Human-readable label supplied by the API.
    status: :class:`int` | :obj:`None`
        HTTP response status code.
    detail: :class:`str` | :class:`dict` | :class:`list`[:class:`object`] | :obj:`None`
        Detailed error information supplied by the API.
    instance: :class:`str` | :obj:`None`
        Identifier for this occurrence of the problem.
    code: :class:`str` | :obj:`None`
        Application-specific error code.
    invalid_params: :class:`list`[:class:`InvalidParam`] | :obj:`None`
        Parameters the API rejected.
    x_validation_errors: :class:`dict` | :class:`list`[:class:`object`] | :obj:`None`
        Additional validation errors supplied by the API.
    """

    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | dict[str, object] | list[object] | None = None
    instance: str | None = None
    code: str | None = None
    invalid_params: list[InvalidParam] | None = msgspec.field(default=None, name="invalid-params")
    x_validation_errors: dict[str, object] | list[object] | None = msgspec.field(
        default=None, name="x-validation-errors"
    )
