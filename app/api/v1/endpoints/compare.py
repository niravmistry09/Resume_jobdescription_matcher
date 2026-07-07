from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.dependencies import get_compare_resume_use_case
from app.application.use_cases.compare_resume import (
    CompareResumeInput,
    CompareResumeUseCase,
)
from app.core.exceptions import (
    FileParsingError,
    ResumeMatcherError,
)
from app.schemas.compare import (
    CompareResponse,
    ExplanationResponse,
    ExtractedSkillsResponse,
    ScoreBreakdownResponse,
)

router = APIRouter()


@router.post(
    "/compare",
    response_model=CompareResponse,
    summary="Compare resume and job description files",
)
async def compare_resume_to_job_description(
    resume: UploadFile = File(...),
    job_description: UploadFile | None = File(default=None),
    job_description_text: str = Form(default=""),
    use_case: CompareResumeUseCase = Depends(get_compare_resume_use_case),
) -> CompareResponse:
    if not job_description and not job_description_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload a job description file or paste job description text.",
        )

    if job_description_text.strip():
        job_description_bytes = job_description_text.encode("utf-8")
        job_description_filename = "job_description.txt"
    else:
        job_description_bytes = await job_description.read()  # type: ignore[union-attr]
        job_description_filename = job_description.filename or ""  # type: ignore[union-attr]

    try:
        result = use_case.execute(
            CompareResumeInput(
                resume_bytes=await resume.read(),
                resume_filename=resume.filename or "",
                job_description_bytes=job_description_bytes,
                job_description_filename=job_description_filename,
            )
        )
    except FileParsingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ResumeMatcherError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume comparison failed.",
        ) from exc

    scoring_result = result.scoring
    explanation = (
        ExplanationResponse(**result.explanation)
        if result.explanation is not None
        else None
    )
    suggestions = (
        explanation.suggestions
        if explanation is not None
        else [
            f"Add or highlight experience with {skill}."
            for skill in scoring_result.missing_skills[:5]
        ]
    )

    return CompareResponse(
        final_score=scoring_result.final_score,
        matched_skills=scoring_result.matched_skills,
        missing_skills=scoring_result.missing_skills,
        extra_skills=scoring_result.extra_skills,
        suggestions=suggestions,
        extracted_skills=ExtractedSkillsResponse(
            resume=result.resume_skills,
            job_description=result.job_description_skills,
        ),
        score_breakdown=ScoreBreakdownResponse(
            skill_overlap_score=scoring_result.skill_overlap_score,
            semantic_similarity_score=scoring_result.semantic_similarity_score,
            final_score=scoring_result.final_score,
            weights=scoring_result.weights,
        ),
        explanation=explanation,
        warnings=result.warnings,
    )
