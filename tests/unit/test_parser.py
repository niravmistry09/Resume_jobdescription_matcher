import pytest

from app.core.exceptions import (
    EmptyFileError,
    InvalidFileError,
    TextExtractionError,
    UnsupportedFileTypeError,
)
from app.infrastructure.external.parser import DocumentParser


def test_extract_plain_text_returns_clean_text() -> None:
    parser = DocumentParser()

    text = parser.extract_text(b" Hello,\r\n\r\n\r\n  FastAPI\tworld! ", "resume.txt")

    assert text == "Hello,\n\nFastAPI world!"


def test_empty_file_raises_exception() -> None:
    parser = DocumentParser()

    with pytest.raises(EmptyFileError):
        parser.extract_text(b"", "resume.txt")


def test_unsupported_extension_raises_exception() -> None:
    parser = DocumentParser()

    with pytest.raises(UnsupportedFileTypeError):
        parser.extract_text(b"hello", "resume.docx")


def test_invalid_pdf_signature_raises_exception() -> None:
    parser = DocumentParser()

    with pytest.raises(InvalidFileError):
        parser.extract_text(b"not a pdf", "resume.pdf")


def test_blank_text_raises_exception() -> None:
    parser = DocumentParser()

    with pytest.raises(TextExtractionError):
        parser.extract_text(b" \n\t ", "resume.txt")
