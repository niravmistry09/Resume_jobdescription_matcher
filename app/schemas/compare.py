from pydantic import BaseModel, Field


class ExtractedSkillsResponse(BaseModel):
    resume: list[str] = Field(default_factory=list)
    job_description: list[str] = Field(default_factory=list)


class ScoreBreakdownResponse(BaseModel):
    skill_overlap_score: float
    semantic_similarity_score: float
    final_score: float
    weights: dict[str, float]


class ExplanationResponse(BaseModel):
    explanation: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class CompareResponse(BaseModel):
    final_score: float
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    extra_skills: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    extracted_skills: ExtractedSkillsResponse
    score_breakdown: ScoreBreakdownResponse
    explanation: ExplanationResponse | None = None
    warnings: list[str] = Field(default_factory=list)

