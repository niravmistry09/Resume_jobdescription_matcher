from app.application.use_cases.compare_resume import CompareResumeUseCase
from app.infrastructure.external.embedding_service import EmbeddingService
from app.infrastructure.external.explanation_service import ExplanationService
from app.infrastructure.external.parser import DocumentParser
from app.infrastructure.external.scoring_service import ScoringService
from app.infrastructure.external.similarity_service import SimilarityService
from app.infrastructure.external.skill_extractor import SkillExtractor


def get_compare_resume_use_case() -> CompareResumeUseCase:
    return CompareResumeUseCase(
        parser=DocumentParser(),
        skill_extractor=SkillExtractor(),
        embedding_service=EmbeddingService(),
        similarity_service=SimilarityService(),
        scoring_service=ScoringService(),
        explanation_service=ExplanationService(),
    )

