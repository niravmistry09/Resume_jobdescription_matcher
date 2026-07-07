from app.infrastructure.external.skill_extractor import SkillExtractor


def test_extract_returns_structured_skills() -> None:
    extractor = SkillExtractor()

    result = extractor.extract(
        "Built REST APIs with Python, FastAPI, PostgreSQL, Docker, AWS, "
        "Pandas, scikit-learn, and strong communication."
    )

    assert result["counts"]["total"] >= 8
    assert "Python" in result["all_skills"]
    assert "FastAPI" in result["all_skills"]
    assert "Communication" in result["all_skills"]


def test_extract_matches_aliases() -> None:
    extractor = SkillExtractor()

    result = extractor.extract("Experience with k8s, GCP, sklearn, and mongo db.")

    assert "Kubernetes" in result["all_skills"]
    assert "Google Cloud" in result["all_skills"]
    assert "scikit-learn" in result["all_skills"]
    assert "MongoDB" in result["all_skills"]
