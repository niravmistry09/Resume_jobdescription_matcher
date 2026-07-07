from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.core.exceptions import ScoringCalculationError


@dataclass(frozen=True)
class ScoringWeights:
    skill_score_weight: float = 0.6
    semantic_score_weight: float = 0.4


@dataclass(frozen=True)
class ScoringResult:
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]
    skill_overlap_score: float
    semantic_similarity_score: float
    final_score: float
    weights: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ScoringService:
    """Calculate exact skill overlap, semantic similarity, and weighted final score."""

    def __init__(self, weights: ScoringWeights | None = None) -> None:
        self._weights = weights or self._default_weights()
        self._validate_weights(self._weights)

    def calculate(
        self,
        resume_skills: list[str],
        job_description_skills: list[str],
        semantic_similarity_score: float,
    ) -> ScoringResult:
        semantic_score = self._bound_score(semantic_similarity_score)
        resume_skill_map = self._normalize_skill_map(resume_skills)
        jd_skill_map = self._normalize_skill_map(job_description_skills)

        resume_skill_keys = set(resume_skill_map)
        jd_skill_keys = set(jd_skill_map)
        matched_keys = resume_skill_keys & jd_skill_keys
        missing_keys = jd_skill_keys - resume_skill_keys
        extra_keys = resume_skill_keys - jd_skill_keys

        matched_skills = self._ordered_names(matched_keys, jd_skill_map)
        missing_skills = self._ordered_names(missing_keys, jd_skill_map)
        extra_skills = self._ordered_names(extra_keys, resume_skill_map)
        skill_overlap_score = self._calculate_skill_overlap_score(
            matched_count=len(matched_skills),
            required_count=len(jd_skill_keys),
        )

        normalized_weights = self._normalized_weights()
        final_score = (
            skill_overlap_score * normalized_weights.skill_score_weight
            + semantic_score * normalized_weights.semantic_score_weight
        )

        return ScoringResult(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            extra_skills=extra_skills,
            skill_overlap_score=round(skill_overlap_score, 2),
            semantic_similarity_score=round(semantic_score, 2),
            final_score=round(self._bound_score(final_score), 2),
            weights={
                "skill_score_weight": normalized_weights.skill_score_weight,
                "semantic_score_weight": normalized_weights.semantic_score_weight,
            },
        )

    def _calculate_skill_overlap_score(
        self,
        matched_count: int,
        required_count: int,
    ) -> float:
        if required_count == 0:
            return 0.0
        return (matched_count / required_count) * 100.0

    def _normalize_skill_map(self, skills: list[str]) -> dict[str, str]:
        normalized: dict[str, str] = {}
        for skill in skills:
            clean_skill = skill.strip()
            if not clean_skill:
                continue
            normalized.setdefault(clean_skill.casefold(), clean_skill)
        return normalized

    def _ordered_names(self, skill_keys: set[str], skill_map: dict[str, str]) -> list[str]:
        return sorted((skill_map[key] for key in skill_keys), key=str.lower)

    def _normalized_weights(self) -> ScoringWeights:
        total = self._weights.skill_score_weight + self._weights.semantic_score_weight
        if total <= 0:
            raise ScoringCalculationError("Scoring weights must be greater than zero.")
        return ScoringWeights(
            skill_score_weight=round(self._weights.skill_score_weight / total, 4),
            semantic_score_weight=round(self._weights.semantic_score_weight / total, 4),
        )

    def _validate_weights(self, weights: ScoringWeights) -> None:
        if weights.skill_score_weight < 0 or weights.semantic_score_weight < 0:
            raise ScoringCalculationError("Scoring weights cannot be negative.")
        if weights.skill_score_weight + weights.semantic_score_weight == 0:
            raise ScoringCalculationError("At least one scoring weight must be positive.")

    def _bound_score(self, score: float) -> float:
        return max(0.0, min(100.0, float(score)))

    def _default_weights(self) -> ScoringWeights:
        from app.core.config import settings

        return ScoringWeights(
            skill_score_weight=settings.skill_score_weight,
            semantic_score_weight=settings.semantic_score_weight,
        )

