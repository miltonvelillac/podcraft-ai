import base64

import pytest

from document_mcp_server.utils.payload_encoding import decode_base64_content


def test_decode_base64_content_returns_bytes() -> None:
    content = base64.b64encode(b"hello").decode("ascii")

    result = decode_base64_content(content)

    assert result == b"hello"


def test_decode_base64_content_rejects_invalid_base64() -> None:
    with pytest.raises(ValueError, match="Content must be valid base64"):
        decode_base64_content("not base64")
