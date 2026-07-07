import pytest

from app.core.exceptions import ExplanationGenerationError
from app.infrastructure.external.explanation_service import ExplanationService


class FakeInteraction:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class FakeInteractions:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.last_input = ""

    def create(self, *, model: str, input: str, generation_config: dict):
        self.last_input = input
        return FakeInteraction(self.output_text)


class FakeGeminiClient:
    def __init__(self, output_text: str) -> None:
        self.interactions = FakeInteractions(output_text)


def test_generate_returns_structured_explanation() -> None:
    client = FakeGeminiClient(
        """
        ```json
        {
          "explanation": "Strong match with a few cloud gaps.",
          "strengths": ["Python", "FastAPI"],
          "weaknesses": ["Kubernetes"],
          "suggestions": ["Add deployment metrics."]
        }
        ```
        """
    )
    service = ExplanationService(client=client, model_name="fake-model")

    result = service.generate(
        {
            "final_score": 82,
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Kubernetes"],
        }
    )

    assert result == {
        "explanation": "Strong match with a few cloud gaps.",
        "strengths": ["Python", "FastAPI"],
        "weaknesses": ["Kubernetes"],
        "suggestions": ["Add deployment metrics."],
    }
    assert '"final_score": 82' in client.interactions.last_input


def test_generate_rejects_invalid_json() -> None:
    service = ExplanationService(
        client=FakeGeminiClient("not json"),
        model_name="fake-model",
    )

    with pytest.raises(ExplanationGenerationError):
        service.generate({"final_score": 50})
