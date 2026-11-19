from __future__ import annotations

from typing import Any

import msgspec

from .links import PageLinks

__all__ = ("Page", "PageInfo")


class PageInfo(msgspec.Struct, frozen=True, kw_only=True, rename="camel"):
    """The ``page`` object. Totals are only filled when ``count=:obj:`True``` is requested.

    Attributes
    ----------
    number: :class:`int`
        One-based number of the current page.
    size: :class:`int`
        Configured page size.
    total_elements: :class:`int` | :obj:`None`
        Number of matching records when a count was requested.
    total_pages: :class:`int` | :obj:`None`
        Number of matching pages when a count was requested.
    """

    number: int
    size: int
    total_elements: int | None = None
    total_pages: int | None = None


def _empty_embedded() -> dict[str, list[Any]]:
    return {}


class Page[T](msgspec.Struct, frozen=True, kw_only=True):
    """A paginated list response.

    Attributes
    ----------
    links: :class:`~amsterdam_nieuwbouwplannen.models.PageLinks`
        Hypermedia links returned with the response.
    embedded: :class:`dict`[:class:`str`, :class:`list`[:obj:`T`]]
        Records grouped by their table name.
    page: :class:`~amsterdam_nieuwbouwplannen.PageInfo` | :obj:`None`
        Pagination metadata, if present.

    Notes
    -----
    The API embeds records under their dataset table name. Use :attr:`items` to read a flat list.
    """

    links: PageLinks = msgspec.field(default_factory=PageLinks, name="_links")
    embedded: dict[str, list[T]] = msgspec.field(default_factory=_empty_embedded, name="_embedded")
    page: PageInfo | None = None

    @property
    def items(self) -> list[T]:
        """All records on this page.

        Returns
        -------
        :class:`list`[:obj:`T`]
            Records flattened across the embedded table entries.
        """

        return [item for records in self.embedded.values() for item in records]

    @property
    def next_url(self) -> str | None:
        """Absolute URL of the next page, if any.

        Returns
        -------
        :class:`str` | :obj:`None`
            Next page URL, or :obj:`None` on the last page.
        """

        return self.links.next.href if self.links.next else None

    @property
    def previous_url(self) -> str | None:
        """Absolute URL of the previous page, if any.

        Returns
        -------
        :class:`str` | :obj:`None`
            Previous page URL, or :obj:`None` on the first page.
        """

        return self.links.previous.href if self.links.previous else None

    @property
    def has_next(self) -> bool:
        """Check whether the page links to a subsequent page.

        Returns
        -------
        :class:`bool`
            :obj:`True` when a next page URL is present.
        """

        return self.next_url is not None

    def __len__(self) -> int:
        """Count the records on this page.

        Returns
        -------
        :class:`int`
            Number of records in the embedded data.
        """

        return sum(len(records) for records in self.embedded.values())
