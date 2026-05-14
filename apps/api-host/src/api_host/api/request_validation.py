from collections.abc import Collection, Iterable

from fastapi import HTTPException, status


def reject_unknown_fields(
    received_fields: Iterable[str],
    allowed_fields: Collection[str],
    field_group_name: str,
) -> None:
    unknown_fields = sorted(set(received_fields) - set(allowed_fields))
    if not unknown_fields:
        return

    allowed = ", ".join(sorted(allowed_fields))
    unknown = ", ".join(unknown_fields)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unknown {field_group_name}(s): {unknown}. Allowed {field_group_name}s: {allowed}.",
    )
