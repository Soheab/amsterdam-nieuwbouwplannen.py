from __future__ import annotations

import msgspec

__all__ = ("ItemLinks", "Link", "PageLinks", "SelfLink")


class Link(msgspec.Struct, frozen=True, kw_only=True):
    """A HAL link. ``href`` is ``:obj:`None``` for an absent next/previous page.

    Attributes
    ----------
    href: :class:`str` | :obj:`None`
        URL targeted by the link.
    title: :class:`str` | :obj:`None`
        Human-readable label supplied by the API.
    """

    href: str | None = None
    title: str | None = None


class SelfLink(msgspec.Struct, frozen=True, kw_only=True):
    """The ``self`` link of a single record.

    Attributes
    ----------
    href: :class:`str`
        URL targeted by the link.
    title: :class:`str` | :obj:`None`
        Human-readable label supplied by the API.
    id: :class:`int` | :obj:`None`
        Unique identifier of the housing plan.
    """

    href: str
    title: str | None = None
    id: int | None = None


class ItemLinks(msgspec.Struct, frozen=True, kw_only=True):
    """``_links`` of a single record.

    Attributes
    ----------
    schema: :class:`str` | :obj:`None`
        Schema URL supplied for the record.
    self_: :class:`~amsterdam_nieuwbouwplannen.models.SelfLink` | :obj:`None`
        Link to the current resource.
    """

    schema: str | None = None
    self_: SelfLink | None = msgspec.field(default=None, name="self")


class PageLinks(msgspec.Struct, frozen=True, kw_only=True):
    """``_links`` of a list response.

    Attributes
    ----------
    self_: :class:`~amsterdam_nieuwbouwplannen.models.Link` | :obj:`None`
        Link to the current resource.
    next: :class:`~amsterdam_nieuwbouwplannen.models.Link` | :obj:`None`
        Link to the next page, if available.
    previous: :class:`~amsterdam_nieuwbouwplannen.models.Link` | :obj:`None`
        Link to the previous page, if available.
    """

    self_: Link | None = msgspec.field(default=None, name="self")
    next: Link | None = None
    previous: Link | None = None
