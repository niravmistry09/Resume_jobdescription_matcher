from __future__ import annotations

import io
from pathlib import Path

import fitz
import pdfplumber

from app.core.exceptions import (
    CorruptedPDFError,
    EmptyFileError,
    InvalidFileError,
    TextExtractionError,
    UnsupportedFileTypeError,
)
from app.domain.entities.resume import Resume
from app.infrastructure.external.cleaner import TextCleaner


class DocumentParser:
    """Extract clean text from PDF and plain text files."""

    _PDF_EXTENSION = ".pdf"
    _TEXT_EXTENSIONS = {".txt", ".text"}
    _SUPPORTED_EXTENSIONS = {_PDF_EXTENSION, *_TEXT_EXTENSIONS}

    def __init__(self, text_cleaner: TextCleaner | None = None) -> None:
        self._text_cleaner = text_cleaner or TextCleaner()

    async def parse(self, file_bytes: bytes, filename: str) -> Resume:
        text = self.extract_text(file_bytes=file_bytes, filename=filename)
        return Resume(raw_text=text)

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        self._validate_file(file_bytes=file_bytes, filename=filename)

        extension = self._extension_for(filename)
        if extension == self._PDF_EXTENSION:
            return self._extract_pdf_text(file_bytes)
        if extension in self._TEXT_EXTENSIONS:
            return self._extract_plain_text(file_bytes)

        raise UnsupportedFileTypeError(
            "Only PDF and plain text files are supported."
        )

    def _validate_file(self, file_bytes: bytes, filename: str) -> None:
        if not filename or not filename.strip():
            raise InvalidFileError("A filename is required.")
        if not file_bytes:
            raise EmptyFileError("The uploaded file is empty.")

        extension = self._extension_for(filename)
        if extension not in self._SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                "Only PDF and plain text files are supported."
            )

    def _extract_pdf_text(self, file_bytes: bytes) -> str:
        if not file_bytes.startswith(b"%PDF"):
            raise InvalidFileError("The uploaded file is not a valid PDF.")

        extraction_errors: list[Exception] = []

        try:
            text = self._extract_pdf_text_with_pdfplumber(file_bytes)
            if text:
                return text
        except Exception as exc:  # pdfplumber raises several PDF-library exceptions.
            extraction_errors.append(exc)

        try:
            text = self._extract_pdf_text_with_pymupdf(file_bytes)
            if text:
                return text
        except Exception as exc:  # PyMuPDF uses broad exceptions for damaged PDFs.
            extraction_errors.append(exc)

        if extraction_errors:
            raise CorruptedPDFError(
                "The PDF could not be read. It may be corrupted or encrypted."
            ) from extraction_errors[-1]

        raise TextExtractionError("No extractable text was found in the PDF.")

    def _extract_pdf_text_with_pdfplumber(self, file_bytes: bytes) -> str:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page_text = [page.extract_text() or "" for page in pdf.pages]
        return self._clean_text("\n".join(page_text))

    def _extract_pdf_text_with_pymupdf(self, file_bytes: bytes) -> str:
        page_text: list[str] = []
        with fitz.open(stream=file_bytes, filetype="pdf") as document:
            if document.needs_pass:
                raise CorruptedPDFError("Encrypted PDFs are not supported.")
            for page in document:
                page_text.append(page.get_text("text"))
        return self._clean_text("\n".join(page_text))

    def _extract_plain_text(self, file_bytes: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return self._ensure_text(file_bytes.decode(encoding))
            except UnicodeDecodeError:
                continue

        raise InvalidFileError("The uploaded text file could not be decoded.")

    def _ensure_text(self, text: str) -> str:
        cleaned = self._clean_text(text)
        if not cleaned:
            raise TextExtractionError("No extractable text was found in the file.")
        return cleaned

    def _clean_text(self, text: str) -> str:
        return self._text_cleaner.clean(text)

    def _extension_for(self, filename: str) -> str:
        return Path(filename).suffix.lower()
