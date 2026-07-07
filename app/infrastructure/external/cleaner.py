from __future__ import annotations

import re
import unicodedata


class TextCleaner:
    """Normalize extracted resume and job description text."""

    _HEADER_PATTERNS = (
        r"^\s*page\s+\d+(\s+of\s+\d+)?\s*$",
        r"^\s*confidential\s*$",
        r"^\s*resume\s*$",
        r"^\s*curriculum\s+vitae\s*$",
    )
    _SPECIAL_CHARACTER_PATTERN = re.compile(r"[^A-Za-z0-9\s.,:;!?@#%&()/'\"+\-]")

    def clean(self, text: str) -> str:
        normalized = self._normalize_unicode(text)
        normalized = self._normalize_line_breaks(normalized)
        normalized = self._remove_special_characters(normalized)
        normalized = self._normalize_whitespace(normalized)
        normalized = self._remove_headers(normalized)
        normalized = self._remove_repeated_blank_lines(normalized)
        return normalized.strip()

    def _normalize_unicode(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKC", text)
        return normalized.replace("\x00", " ")

    def _normalize_line_breaks(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _remove_special_characters(self, text: str) -> str:
        return self._SPECIAL_CHARACTER_PATTERN.sub(" ", text)

    def _normalize_whitespace(self, text: str) -> str:
        lines = []
        for line in text.split("\n"):
            compact_line = re.sub(r"[ \t\f\v]+", " ", line).strip()
            lines.append(compact_line)
        return "\n".join(lines)

    def _remove_headers(self, text: str) -> str:
        cleaned_lines = []
        previous_line = ""

        for line in text.split("\n"):
            if self._is_header_or_footer(line):
                continue
            if line and line == previous_line and len(line) <= 80:
                continue
            cleaned_lines.append(line)
            if line:
                previous_line = line

        return "\n".join(cleaned_lines)

    def _is_header_or_footer(self, line: str) -> bool:
        compact = line.strip()
        if not compact:
            return False

        return any(
            re.match(pattern, compact, flags=re.IGNORECASE)
            for pattern in self._HEADER_PATTERNS
        )

    def _remove_repeated_blank_lines(self, text: str) -> str:
        return re.sub(r"\n{3,}", "\n\n", text)


default_text_cleaner = TextCleaner()


def clean_text(text: str) -> str:
    return default_text_cleaner.clean(text)

