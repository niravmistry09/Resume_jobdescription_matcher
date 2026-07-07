from app.infrastructure.external.embedding_service import EmbeddingService


class FakeEmbeddingModel:
    def __init__(self) -> None:
        self.calls = 0

    def encode(
        self,
        sentences,
        *,
        batch_size,
        normalize_embeddings,
        convert_to_numpy,
        show_progress_bar,
    ):
        self.calls += 1
        return [[float(index), 1.0] for index, _ in enumerate(sentences)]


class TestEmbeddingService(EmbeddingService):
    load_count = 0
    fake_model = FakeEmbeddingModel()

    def _load_model(self, model_name: str):
        type(self).load_count += 1
        return type(self).fake_model


def test_embedding_service_loads_model_once() -> None:
    TestEmbeddingService.reset_cached_model()
    TestEmbeddingService.load_count = 0

    first_service = TestEmbeddingService(model_name="fake-model")
    second_service = TestEmbeddingService(model_name="fake-model")

    assert first_service.embed_text("Python developer") == [0.0, 1.0]
    assert second_service.embed_text("FastAPI developer") == [0.0, 1.0]
    assert TestEmbeddingService.load_count == 1


def test_embedding_service_embeds_batch_and_ignores_blank_text() -> None:
    TestEmbeddingService.reset_cached_model()

    service = TestEmbeddingService(model_name="fake-model", batch_size=8)

    assert service.embed_texts(["Python", " ", "FastAPI"]) == [[0.0, 1.0], [1.0, 1.0]]
