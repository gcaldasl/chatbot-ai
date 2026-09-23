from app.providers.embeddings import EmbeddingProvider


class BatchEmbedder:
    """Splits an arbitrarily long list of texts into batches an
    EmbeddingProvider can safely handle in one request. This is what keeps a
    1000+ chunk document from exceeding OpenAI's per-request array/token
    limits (the original cause of a 502 on large uploads)."""

    def __init__(self, provider: EmbeddingProvider, batch_size: int = 200):
        self._provider = provider
        self._batch_size = batch_size

    async def embed_all(self, texts: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start : start + self._batch_size]
            embeddings.extend(await self._provider.embed(batch))
        return embeddings
