from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.exceptions import ExplanationGenerationError, MissingGeminiAPIKeyError
from app.infrastructure.external.embedding_service import EmbeddingService
from app.infrastructure.external.explanation_service import ExplanationService
from app.infrastructure.external.parser import DocumentParser
from app.infrastructure.external.scoring_service import ScoringResult, ScoringService
from app.infrastructure.external.similarity_service import SimilarityService
from app.infrastructure.external.skill_extractor import SkillExtractor


@dataclass(frozen=True)
class CompareResumeInput:
    resume_bytes: bytes
    resume_filename: str
    job_description_bytes: bytes
    job_description_filename: str


@dataclass(frozen=True)
class CompareResumeResult:
    resume_skills: list[str]
    job_description_skills: list[str]
    scoring: ScoringResult
    explanation: dict[str, Any] | None
    warnings: list[str]


class CompareResumeUseCase:
    def __init__(
        self,
        parser: DocumentParser,
        skill_extractor: SkillExtractor,
        embedding_service: EmbeddingService,
        similarity_service: SimilarityService,
        scoring_service: ScoringService,
        explanation_service: ExplanationService,
    ) -> None:
        self._parser = parser
        self._skill_extractor = skill_extractor
        self._embedding_service = embedding_service
        self._similarity_service = similarity_service
        self._scoring_service = scoring_service
        self._explanation_service = explanation_service

    def execute(self, input_data: CompareResumeInput) -> CompareResumeResult:
        resume_text = self._parser.extract_text(
            file_bytes=input_data.resume_bytes,
            filename=input_data.resume_filename,
        )
        job_description_text = self._parser.extract_text(
            file_bytes=input_data.job_description_bytes,
            filename=input_data.job_description_filename,
        )

        resume_skill_output = self._skill_extractor.extract(resume_text)
        job_description_skill_output = self._skill_extractor.extract(job_description_text)
        resume_skills = resume_skill_output["all_skills"]
        job_description_skills = job_description_skill_output["all_skills"]

        resume_embedding, job_description_embedding = self._embedding_service.embed_texts(
            [resume_text, job_description_text]
        )
        semantic_result = self._similarity_service.calculate(
            resume_embedding=resume_embedding,
            job_description_embedding=job_description_embedding,
        )
        scoring_result = self._scoring_service.calculate(
            resume_skills=resume_skills,
            job_description_skills=job_description_skills,
            semantic_similarity_score=semantic_result.percentage,
        )

        warnings: list[str] = []
        explanation: dict[str, Any] | None = None
        try:
            explanation = self._explanation_service.generate(scoring_result.to_dict())
        except MissingGeminiAPIKeyError:
            warnings.append("Gemini explanation skipped because GEMINI_API_KEY is not set.")
        except ExplanationGenerationError as exc:
            warnings.append(f"Gemini explanation skipped: {exc}")

        return CompareResumeResult(
            resume_skills=resume_skills,
            job_description_skills=job_description_skills,
            scoring=scoring_result,
            explanation=explanation,
            warnings=warnings,
        )

