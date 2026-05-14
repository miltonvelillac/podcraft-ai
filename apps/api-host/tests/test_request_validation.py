import pytest
from fastapi import HTTPException

from api_host.api.request_validation import reject_unknown_fields


def test_reject_unknown_fields_allows_known_fields() -> None:
    reject_unknown_fields(
        received_fields=["file", "style"],
        allowed_fields={"file", "style", "voice"},
        field_group_name="form field",
    )


def test_reject_unknown_fields_rejects_unknown_fields() -> None:
    with pytest.raises(HTTPException) as exc_info:
        reject_unknown_fields(
            received_fields=["file", "target-duration"],
            allowed_fields={"file", "target_duration"},
            field_group_name="form field",
        )

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "Unknown form field(s): target-duration. Allowed form fields: file, target_duration."
    )
