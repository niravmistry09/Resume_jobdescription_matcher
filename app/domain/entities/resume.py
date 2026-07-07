from dataclasses import dataclass


@dataclass(frozen=True)
class Resume:
    raw_text: str
    candidate_name: str | None = None

