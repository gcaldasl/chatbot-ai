from abc import ABC, abstractmethod

import httpx

from app.domain.exceptions import EmbeddingProviderError


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a single batch. Callers must keep `texts` under the
        provider's per-request array/token limits — see BatchEmbedder for
        embedding arbitrarily long lists."""


class OpenAIEmbeddingProvider(EmbeddingProvider):
    EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"

    def __init__(
        self,
        api_key: str | None,
        model: str,
        timeout: float = 120.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._transport = transport

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not self._api_key:
            raise EmbeddingProviderError("OPENAI_API_KEY is not configured on the server.")

        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                self.EMBEDDINGS_URL,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self._model, "input": texts},
            )

        if response.status_code != 200:
            raise EmbeddingProviderError(
                f"Embedding request failed: {response.status_code} {response.text[:300]}"
            )

        data = response.json()["data"]
        return [item["embedding"] for item in sorted(data, key=lambda item: item["index"])]
