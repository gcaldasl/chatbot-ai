"""In-memory test doubles for the repository/provider interfaces, so
services can be unit tested without a real database or network access."""

import uuid
from dataclasses import replace

from app.domain.models import Chunk, Document, DocumentStatus
from app.providers.chat_completion import ChatCompletionProvider, ChatMessage
from app.providers.embeddings import EmbeddingProvider
from app.repositories.base import ChunkRepository, DocumentRepository


class FakeDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self.documents: dict[uuid.UUID, Document] = {}
        self.mark_ready_calls: list[tuple[uuid.UUID, int, int]] = []
        self.mark_failed_calls: list[tuple[uuid.UUID, str]] = []

    async def create(self, document_id: uuid.UUID, filename: str) -> None:
        self.documents[document_id] = Document(
            id=document_id, filename=filename, status=DocumentStatus.PROCESSING
        )

    async def get(self, document_id: uuid.UUID) -> Document | None:
        return self.documents.get(document_id)

    async def mark_ready(self, document_id: uuid.UUID, characters: int, chunk_count: int) -> None:
        self.mark_ready_calls.append((document_id, characters, chunk_count))
        document = self.documents[document_id]
        self.documents[document_id] = replace(
            document,
            status=DocumentStatus.READY,
            characters=characters,
            chunk_count=chunk_count,
            error=None,
        )

    async def mark_failed(self, document_id: uuid.UUID, error: str) -> None:
        self.mark_failed_calls.append((document_id, error))
        document = self.documents[document_id]
        self.documents[document_id] = replace(document, status=DocumentStatus.FAILED, error=error)


class FakeChunkRepository(ChunkRepository):
    def __init__(self, search_results: list[Chunk] | None = None) -> None:
        self.inserted: list[tuple[uuid.UUID, list[str], list[list[float]]]] = []
        self.search_calls: list[tuple[uuid.UUID, list[float], int]] = []
        self._search_results = search_results or []

    async def insert_many(
        self, document_id: uuid.UUID, contents: list[str], embeddings: list[list[float]]
    ) -> None:
        self.inserted.append((document_id, contents, embeddings))

    async def search_similar(
        self, document_id: uuid.UUID, query_embedding: list[float], top_k: int
    ) -> list[Chunk]:
        self.search_calls.append((document_id, query_embedding, top_k))
        return self._search_results


class FakeEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 3) -> None:
        self.calls: list[list[str]] = []
        self._dimensions = dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        return [[float(len(text))] * self._dimensions for text in texts]


class FakeChatCompletionProvider(ChatCompletionProvider):
    def __init__(self, response: str = "fake answer") -> None:
        self.calls: list[list[ChatMessage]] = []
        self._response = response

    async def complete(self, messages: list[ChatMessage]) -> str:
        self.calls.append(list(messages))
        return self._response
