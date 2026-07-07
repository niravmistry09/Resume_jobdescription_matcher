from dataclasses import dataclass


@dataclass(frozen=True)
class JobDescription:
    raw_text: str
    title: str | None = None

