"""Reusable pagination utilities for list endpoints."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


# -------------- schemas --------------
class PaginatedListResponse(BaseModel, Generic[T]):
    """Generic wrapper returned by every paginated list endpoint."""

    items: list[T]
    total_count: int
    has_more: bool
    page: int
    items_per_page: int


# -------------- helpers --------------
def compute_offset(page: int, items_per_page: int) -> int:
    """Convert a 1-based page number into a database offset."""
    return (page - 1) * items_per_page


def paginated_response(
    *,
    crud_data: list[Any],
    total_count: int,
    page: int,
    items_per_page: int,
) -> dict[str, Any]:
    """Build a dict that matches the ``PaginatedListResponse`` schema.

    Parameters
    ----------
    crud_data:
        The list of rows returned by the CRUD ``get_multi`` call.
    total_count:
        Total number of rows matching the query (before pagination).
    page:
        Current page number (1-based).
    items_per_page:
        Maximum items per page.
    """
    return {
        "items": crud_data,
        "total_count": total_count,
        "has_more": (page * items_per_page) < total_count,
        "page": page,
        "items_per_page": items_per_page,
    }


