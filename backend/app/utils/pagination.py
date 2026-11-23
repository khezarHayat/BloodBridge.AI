"""
Pagination utilities.

Provides a pagination parameters class and helper function for
building paginated queries against Supabase tables.
"""

from typing import Optional

from fastapi import Query


class PaginationParams:
    """
    Reusable pagination parameters extracted from query string.

    Usage as a FastAPI dependency:
        @router.get("/items")
        async def list_items(pagination: PaginationParams = Depends()):
            ...
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
        limit: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    ):
        self.page = page
        self.limit = limit

    @property
    def offset(self) -> int:
        """Calculate the database offset from page and limit."""
        return (self.page - 1) * self.limit

    @property
    def range_start(self) -> int:
        """Start index for Supabase range query (0-indexed)."""
        return self.offset

    @property
    def range_end(self) -> int:
        """End index for Supabase range query (inclusive)."""
        return self.offset + self.limit - 1


def paginate_response(
    data: list,
    total: int,
    page: int,
    limit: int,
    items_key: Optional[str] = None,
) -> dict:
    """
    Build a standardized pagination response dict.

    Args:
        data: The list of items for the current page.
        total: Total count of matching items across all pages.
        page: The current page number.
        limit: Items per page.
        items_key: Optional custom key for the items list.

    Returns:
        Dictionary with pagination metadata and items mapped to standard keys.
    """
    has_more = (page * limit) < total
    res = {
        "items": data,
        "data": data,
        "requests": data,
        "blood_banks": data,
        "batches": data,
        "donors": data,
        "notifications": data,
        "users": data,
        "logs": data,
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": has_more,
    }
    if items_key:
        res[items_key] = data
    return res


def get_count_from_response(response) -> int:
    """
    Safely extract the total count from a Supabase response.

    Supabase returns the count in the response when using
    .select("*", count="exact"). This helper safely extracts it.

    Args:
        response: The Supabase query response object.

    Returns:
        The total count, or 0 if not available.
    """
    if hasattr(response, "count") and response.count is not None:
        return response.count
    if response.data:
        return len(response.data)
    return 0
