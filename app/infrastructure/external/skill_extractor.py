from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import spacy

from app.infrastructure.external.cleaner import TextCleaner


SkillMatch = dict[str, str]
StructuredSkills = dict[str, Any]


@dataclass(frozen=True)
class SkillDefinition:
    category: str
    name: str
    aliases: tuple[str, ...]


class SkillExtractor:
    """Deterministic skill extractor based on spaCy tokenization, regex, and skills.json."""

    def __init__(
        self,
        skills_path: Path | None = None,
        text_cleaner: TextCleaner | None = None,
    ) -> None:
        self._skills_path = skills_path or Path(__file__).with_name("skills.json")
        self._text_cleaner = text_cleaner or TextCleaner()
        self._nlp = spacy.blank("en")
        self._skills = self._load_skills()
        self._patterns = self._compile_patterns(self._skills)

    def extract(self, text: str) -> StructuredSkills:
        cleaned_text = self._text_cleaner.clean(text)
        doc = self._nlp(cleaned_text)
        searchable_text = self._build_searchable_text(cleaned_text, doc)

        categories: dict[str, list[SkillMatch]] = {
            category: [] for category in self._categories()
        }
        seen: set[tuple[str, str]] = set()

        for skill in self._skills:
            for pattern, alias in self._patterns[skill.name]:
                match = pattern.search(searchable_text)
                if not match:
                    continue

                dedupe_key = (skill.category, skill.name.lower())
                if dedupe_key in seen:
                    break

                categories[skill.category].append(
                    {
                        "name": skill.name,
                        "matched_text": match.group(0),
                        "matched_alias": alias,
                        "source": "skills.json+regex+spacy",
                    }
                )
                seen.add(dedupe_key)
                break

        for category in categories:
            categories[category].sort(key=lambda item: item["name"].lower())

        all_skills = [
            item["name"]
            for category in categories.values()
            for item in category
        ]

        return {
            "skills": categories,
            "all_skills": sorted(all_skills, key=str.lower),
            "counts": {
                "total": len(all_skills),
                **{
                    category: len(matches)
                    for category, matches in categories.items()
                },
            },
        }

    def _load_skills(self) -> list[SkillDefinition]:
        with self._skills_path.open("r", encoding="utf-8") as skills_file:
            raw_skills: dict[str, list[dict[str, Any]]] = json.load(skills_file)

        definitions: list[SkillDefinition] = []
        for category, entries in raw_skills.items():
            for entry in entries:
                name = entry["name"]
                aliases = tuple(dict.fromkeys([name, *entry.get("aliases", [])]))
                definitions.append(
                    SkillDefinition(
                        category=category,
                        name=name,
                        aliases=aliases,
                    )
                )
        return definitions

    def _compile_patterns(
        self,
        skills: list[SkillDefinition],
    ) -> dict[str, list[tuple[re.Pattern[str], str]]]:
        compiled: dict[str, list[tuple[re.Pattern[str], str]]] = {}
        for skill in skills:
            compiled[skill.name] = [
                (self._compile_alias_pattern(alias), alias)
                for alias in sorted(skill.aliases, key=len, reverse=True)
            ]
        return compiled

    def _compile_alias_pattern(self, alias: str) -> re.Pattern[str]:
        escaped = re.escape(alias.strip())
        flexible_separator = escaped.replace(r"\ ", r"[\s\-/_.]+")
        return re.compile(
            rf"(?<![A-Za-z0-9+#.]){flexible_separator}(?![A-Za-z0-9+#.])",
            flags=re.IGNORECASE,
        )

    def _build_searchable_text(self, cleaned_text: str, doc: spacy.tokens.Doc) -> str:
        token_text = " ".join(token.text for token in doc if not token.is_space)
        return f"{cleaned_text}\n{token_text}"

    def _categories(self) -> list[str]:
        return list(dict.fromkeys(skill.category for skill in self._skills))
