from __future__ import annotations

import datetime
from collections.abc import Mapping, Sequence
from typing import TypeGuard

import msgspec

from ._types.sort import Sort
from .enums import SortOrder, Stadsdeel

__all__ = ("QueryParams", "build_filters", "build_list_params", "format_value", "wire_names")

type QueryParams = list[tuple[str, str]]


def wire_names(model: type[msgspec.Struct]) -> dict[str, str]:
    return {f.name: f.encode_name for f in msgspec.structs.fields(model)}


def _is_sequence(value: object) -> TypeGuard[Sequence[object]]:
    return isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray)


def _is_operator_mapping(value: object) -> TypeGuard[Mapping[str, object]]:
    return isinstance(value, Mapping)


def format_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime.date):
        return value.isoformat()
    if _is_sequence(value):
        return ",".join(format_value(item) for item in value)
    return str(value)


def _filter_items(filters: msgspec.Struct | Mapping[str, object]) -> list[tuple[str, object]]:
    if isinstance(filters, msgspec.Struct):
        return [
            (field.encode_name, value)
            for field in msgspec.structs.fields(type(filters))
            if (value := getattr(filters, field.name)) is not None
        ]
    return list(filters.items())


def merge_filters(
    defaults: Mapping[str, object],
    filters: msgspec.Struct | Mapping[str, object] | None,
) -> Mapping[str, object]:
    return defaults if filters is None else {**defaults, **dict(_filter_items(filters))}


def build_filters(
    filters: msgspec.Struct | Mapping[str, object], names: Mapping[str, str]
) -> QueryParams:
    params: QueryParams = []
    items = dict(_filter_items(filters))
    for key, value in items.items():
        if key == "stadsdeel" and isinstance(value, Stadsdeel):
            if "stadsdeel_code" in items or "stadsdeelCode" in items:
                raise ValueError("Use either stadsdeel or stadsdeel_code.")
            params.append((names.get("stadsdeel_code", "stadsdeelCode"), value.code))
            continue
        api_name = names.get(key, key)
        if isinstance(value, msgspec.Struct) or _is_operator_mapping(value):
            for operator, operand in _filter_items(value):
                param = api_name if operator == "eq" else f"{api_name}[{operator}]"
                params.append((param, format_value(operand)))
        else:
            params.append((api_name, format_value(value)))
    return params


def build_list_params[KeyT: str](
    *,
    names: Mapping[str, str],
    filters: msgspec.Struct | Mapping[str, object] | None = None,
    page: int | None = None,
    page_size: int | None = None,
    sort: Mapping[KeyT, SortOrder] | Sequence[KeyT | Sort[KeyT]] | None = None,
    fields: Sequence[KeyT] | Sequence[str] | None = None,
    count: bool = False,
    format: str | None = None,
) -> QueryParams:
    params: QueryParams = []
    if filters:
        params.extend(build_filters(filters, names))
    if page is not None:
        params.append(("page", str(page)))
    if page_size is not None:
        params.append(("_pageSize", str(page_size)))
    if sort:
        keys: list[str]
        if isinstance(sort, Mapping):
            keys = [
                f"-{names.get(key, key)}" if order == "desc" else names.get(key, key)
                for key, order in sort.items()
            ]
        else:
            keys = []
            for key in sort:
                if isinstance(key, Sort):
                    name = names.get(key.field, key.field)
                    keys.append(f"-{name}" if key.order == SortOrder.DESC else name)
                else:
                    keys.append(names.get(key, key))
        params.append(("_sort", ",".join(keys)))
    if fields:
        selected = [names.get(field, field) for field in fields]
        # ``id`` is required to decode a record.
        if "id" not in selected:
            selected.insert(0, "id")
        params.append(("_fields", ",".join(selected)))
    if count:
        params.append(("_count", "true"))
    if format is not None:
        params.append(("_format", format))
    return params
