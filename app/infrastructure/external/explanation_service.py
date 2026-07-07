from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Protocol

from app.core.exceptions import ExplanationGenerationError, MissingGeminiAPIKeyError


ExplanationPayload = dict[str, Any]


class GeminiInteractions(Protocol):
    def create(self, *, model: str, input: str, generation_config: dict[str, Any]):
        """Create a Gemini interaction."""


class GeminiClient(Protocol):
    interactions: GeminiInteractions


class ExplanationService:
    """Generate human-readable resume match explanations using Gemini."""

    def __init__(
        self,
        client: GeminiClient | None = None,
        model_name: str | None = None,
        prompt_template_path: Path | None = None,
    ) -> None:
        self._client = client
        self._model_name = model_name
        self._prompt_template_path = (
            prompt_template_path
            or Path(__file__).resolve().parents[2]
            / "prompts"
            / "resume_explanation_prompt.txt"
        )

    def generate(self, scoring_output: dict[str, Any]) -> ExplanationPayload:
        prompt = self._build_prompt(scoring_output)
        client = self._get_client()
        model_name = self._model_name or self._default_model_name()

        try:
            interaction = self._create_interaction(
                client=client,
                model_name=model_name,
                prompt=prompt,
            )
        except Exception as exc:
            raise ExplanationGenerationError(
                "Gemini explanation generation failed."
            ) from exc

        raw_text = getattr(interaction, "output_text", None)
        if not raw_text:
            raise ExplanationGenerationError("Gemini returned an empty explanation.")

        return self._parse_response(raw_text)

    def _build_prompt(self, scoring_output: dict[str, Any]) -> str:
        template = self._prompt_template_path.read_text(encoding="utf-8")
        scoring_json = json.dumps(scoring_output, ensure_ascii=False, indent=2)
        return template.format(scoring_output=scoring_json)

    def _create_interaction(
        self,
        client: GeminiClient,
        model_name: str,
        prompt: str,
    ):
        generation_config = {
            "temperature": 0.2,
            "response_mime_type": "application/json",
        }
        try:
            return client.interactions.create(
                model=model_name,
                input=prompt,
                generation_config=generation_config,
            )
        except TypeError:
            return client.interactions.create(
                model=model_name,
                input=prompt,
                generation_config={"temperature": 0.2},
            )

    def _get_client(self) -> GeminiClient:
        if self._client is not None:
            return self._client

        api_key = self._default_api_key()
        if not api_key:
            raise MissingGeminiAPIKeyError("GEMINI_API_KEY is required.")

        from google import genai

        self._client = genai.Client(api_key=api_key)
        return self._client

    def _parse_response(self, raw_text: str) -> ExplanationPayload:
        payload_text = self._extract_json_text(raw_text)
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            raise ExplanationGenerationError(
                "Gemini response was not valid JSON."
            ) from exc

        return self._validate_payload(payload)

    def _extract_json_text(self, raw_text: str) -> str:
        stripped = raw_text.strip()
        fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, re.DOTALL)
        if fenced_match:
            return fenced_match.group(1).strip()

        object_match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if object_match:
            return object_match.group(0).strip()

        return stripped

    def _validate_payload(self, payload: Any) -> ExplanationPayload:
        if not isinstance(payload, dict):
            raise ExplanationGenerationError("Gemini response JSON must be an object.")

        required_fields = {
            "explanation": str,
            "strengths": list,
            "weaknesses": list,
            "suggestions": list,
        }
        for field, expected_type in required_fields.items():
            if field not in payload or not isinstance(payload[field], expected_type):
                raise ExplanationGenerationError(
                    f"Gemini response missing valid '{field}' field."
                )

        return {
            "explanation": payload["explanation"].strip(),
            "strengths": self._clean_list(payload["strengths"]),
            "weaknesses": self._clean_list(payload["weaknesses"]),
            "suggestions": self._clean_list(payload["suggestions"]),
        }

    def _clean_list(self, values: list[Any]) -> list[str]:
        return [str(value).strip() for value in values if str(value).strip()]

    def _default_model_name(self) -> str:
        from app.core.config import settings

        return settings.gemini_model

    def _default_api_key(self) -> str | None:
        from app.core.config import settings

        return settings.gemini_api_key
