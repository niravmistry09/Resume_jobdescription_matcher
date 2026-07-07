import pytest

from app.core.exceptions import SimilarityCalculationError
from app.infrastructure.external.similarity_service import SimilarityService


def test_calculate_returns_cosine_similarity_and_percentage() -> None:
    service = SimilarityService()

    result = service.calculate([1.0, 0.0], [1.0, 0.0])

    assert result.cosine_similarity == 1.0
    assert result.percentage == 100.0
    assert result.to_dict() == {
        "cosine_similarity": 1.0,
        "percentage": 100.0,
    }


def test_calculate_detects_opposite_embeddings() -> None:
    service = SimilarityService()

    result = service.calculate([1.0, 0.0], [-1.0, 0.0])

    assert result.cosine_similarity == -1.0
    assert result.percentage == 0.0


def test_calculate_rejects_dimension_mismatch() -> None:
    service = SimilarityService()

    with pytest.raises(SimilarityCalculationError):
        service.calculate([1.0, 0.0], [1.0])


def test_calculate_rejects_empty_embeddings() -> None:
    service = SimilarityService()

    with pytest.raises(SimilarityCalculationError):
        service.calculate([], [1.0])
