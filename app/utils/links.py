def pagination_links(base_url: str, offset: int, limit: int, total: int, **filters) -> dict:
    """Build next/prev pagination links, ignoring None filters."""
    filter_params = "&".join(
        f"{key}={value}" for key, value in filters.items() if value is not None
    )

    base = (
        f"{base_url}?limit={limit}&{filter_params}"
        if filter_params
        else f"{base_url}?limit={limit}"
    )

    has_next = offset + limit < total
    has_prev = offset > 0

    links: dict[str, str | None] = {
        "self": f"{base}&offset={offset}",
        "next": f"{base}&offset={offset + limit}" if has_next else None,
        "prev": f"{base}&offset={max(offset - limit, 0)}" if has_prev else None,
    }

    return links
