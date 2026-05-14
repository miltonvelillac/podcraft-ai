from document_mcp_server.tools.clean_text import clean_extracted_text


def test_clean_extracted_text_normalizes_whitespace() -> None:
    result = clean_extracted_text("  line one\t\tline two\n\n\n\n line three\x00 ")

    assert result == "line one line two\n\nline three"
