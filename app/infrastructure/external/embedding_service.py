from __future__ import annotations

from threading import Lock
from typing import ClassVar, Protocol


class SentenceTransformerModel(Protocol):
    def encode(
        self,
        sentences: str | list[str],
        *,
        batch_size: int,
        normalize_embeddings: bool,
        convert_to_numpy: bool,
        show_progress_bar: bool,
    ):
        """Encode text into vector embeddings."""


class EmbeddingService:
    """Generate sentence embeddings with a process-wide cached model."""

    _model: ClassVar[SentenceTransformerModel | None] = None
    _model_name: ClassVar[str | None] = None
    _model_lock: ClassVar[Lock] = Lock()

    def __init__(
        self,
        model_name: str | None = None,
        batch_size: int = 32,
        normalize_embeddings: bool = True,
    ) -> None:
        self._model_name_for_instance = model_name or self._default_model_name()
        self._batch_size = batch_size
        self._normalize_embeddings = normalize_embeddings

    def embed_text(self, text: str) -> list[float]:
        embeddings = self.embed_texts([text])
        return embeddings[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        cleaned_texts = [text.strip() for text in texts if text and text.strip()]
        if not cleaned_texts:
            return []

        model = self._get_model()
        encoded = model.encode(
            cleaned_texts,
            batch_size=self._batch_size,
            normalize_embeddings=self._normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return self._to_python_lists(encoded)

    @classmethod
    def reset_cached_model(cls) -> None:
        cls._model = None
        cls._model_name = None

    def _get_model(self) -> SentenceTransformerModel:
        cls = type(self)
        if cls._model is not None and cls._model_name == self._model_name_for_instance:
            return cls._model

        with cls._model_lock:
            if cls._model is None or cls._model_name != self._model_name_for_instance:
                cls._model = self._load_model(self._model_name_for_instance)
                cls._model_name = self._model_name_for_instance
        return cls._model

    def _load_model(self, model_name: str) -> SentenceTransformerModel:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_name)

    def _default_model_name(self) -> str:
        from app.core.config import settings

        return settings.embedding_model

    def _to_python_lists(self, encoded) -> list[list[float]]:
        if hasattr(encoded, "tolist"):
            return encoded.tolist()
        return [list(vector) for vector in encoded]
