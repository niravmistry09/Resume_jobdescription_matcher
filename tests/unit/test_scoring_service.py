import pytest

from app.core.exceptions import ScoringCalculationError
from app.infrastructure.external.scoring_service import (
    ScoringService,
    ScoringWeights,
)


def test_scoring_service_calculates_weighted_score() -> None:
    service = ScoringService(
        weights=ScoringWeights(skill_score_weight=0.6, semantic_score_weight=0.4)
    )

    result = service.calculate(
        resume_skills=["Python", "FastAPI", "Docker"],
        job_description_skills=["Python", "FastAPI", "Kubernetes"],
        semantic_similarity_score=80.0,
    )

    assert result.matched_skills == ["FastAPI", "Python"]
    assert result.missing_skills == ["Kubernetes"]
    assert result.extra_skills == ["Docker"]
    assert result.skill_overlap_score == 66.67
    assert result.semantic_similarity_score == 80.0
    assert result.final_score == 72.0


def test_scoring_service_normalizes_weights() -> None:
    service = ScoringService(
        weights=ScoringWeights(skill_score_weight=3.0, semantic_score_weight=1.0)
    )

    result = service.calculate(
        resume_skills=["Python"],
        job_description_skills=["Python"],
        semantic_similarity_score=0.0,
    )

    assert result.final_score == 75.0
    assert result.weights == {
        "skill_score_weight": 0.75,
        "semantic_score_weight": 0.25,
    }


def test_scoring_service_rejects_invalid_weights() -> None:
    with pytest.raises(ScoringCalculationError):
        ScoringService(
            weights=ScoringWeights(skill_score_weight=-1.0, semantic_score_weight=1.0)
        )
