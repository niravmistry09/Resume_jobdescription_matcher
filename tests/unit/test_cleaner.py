from app.infrastructure.external.cleaner import clean_text


def test_clean_text_normalizes_whitespace_and_blank_lines() -> None:
    raw_text = "  Python\t\tDeveloper\r\n\r\n\r\nFastAPI    Engineer  "

    assert clean_text(raw_text) == "Python Developer\n\nFastAPI Engineer"


def test_clean_text_removes_common_headers() -> None:
    raw_text = "Resume\nPage 1 of 2\nNirav Shah\nConfidential\nPython Developer"

    assert clean_text(raw_text) == "Nirav Shah\nPython Developer"


def test_clean_text_removes_special_characters() -> None:
    raw_text = "Skills: Python ★ FastAPI • SQL ✅"

    assert clean_text(raw_text) == "Skills: Python FastAPI SQL"


def test_clean_text_removes_repeated_short_lines() -> None:
    raw_text = "Nirav Shah\nNirav Shah\nExperience\nBuilt APIs"

    assert clean_text(raw_text) == "Nirav Shah\nExperience\nBuilt APIs"
