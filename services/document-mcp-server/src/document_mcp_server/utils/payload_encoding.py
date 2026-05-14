import base64
import binascii


def decode_base64_content(content_base64: str) -> bytes:
    try:
        return base64.b64decode(content_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Content must be valid base64.") from exc
