from __future__ import annotations

from dataclasses import asdict, dataclass
from numbers import Real
from typing import Sequence

from app.core.exceptions import SimilarityCalculationError


Embedding = Sequence[float]


@dataclass(frozen=True)
class SimilarityResult:
    cosine_similarity: float
    percentage: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


class SimilarityService:
    """Calculate semantic similarity between resume and job description embeddings."""

    def calculate(
        self,
        resume_embedding: Embedding,
        job_description_embedding: Embedding,
    ) -> SimilarityResult:
        self._validate_embeddings(resume_embedding, job_description_embedding)

        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(
            [list(resume_embedding)],
            [list(job_description_embedding)],
        )
        cosine_score = float(similarity_matrix[0][0])
        bounded_score = max(-1.0, min(1.0, cosine_score))

        return SimilarityResult(
            cosine_similarity=round(bounded_score, 6),
            percentage=round(((bounded_score + 1.0) / 2.0) * 100.0, 2),
        )

    def calculate_percentage(
        self,
        resume_embedding: Embedding,
        job_description_embedding: Embedding,
    ) -> float:
        return self.calculate(resume_embedding, job_description_embedding).percentage

    def _validate_embeddings(
        self,
        resume_embedding: Embedding,
        job_description_embedding: Embedding,
    ) -> None:
        if not resume_embedding:
            raise SimilarityCalculationError("Resume embedding cannot be empty.")
        if not job_description_embedding:
            raise SimilarityCalculationError("Job description embedding cannot be empty.")
        if len(resume_embedding) != len(job_description_embedding):
            raise SimilarityCalculationError(
                "Resume and job description embeddings must have the same dimensions."
            )
        if not self._is_numeric_embedding(resume_embedding):
            raise SimilarityCalculationError("Resume embedding must contain only numbers.")
        if not self._is_numeric_embedding(job_description_embedding):
            raise SimilarityCalculationError(
                "Job description embedding must contain only numbers."
            )

    def _is_numeric_embedding(self, embedding: Embedding) -> bool:
        return all(isinstance(value, Real) for value in embedding)

