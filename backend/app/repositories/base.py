import uuid
from abc import ABC, abstractmethod

from app.domain.models import Chunk, Document


class DocumentRepository(ABC):
    @abstractmethod
    async def create(self, document_id: uuid.UUID, filename: str) -> None:
        """Insert a new document row with status PROCESSING."""

    @abstractmethod
    async def get(self, document_id: uuid.UUID) -> Document | None: ...

    @abstractmethod
    async def mark_ready(self, document_id: uuid.UUID, characters: int, chunk_count: int) -> None: ...

    @abstractmethod
    async def mark_failed(self, document_id: uuid.UUID, error: str) -> None: ...


class ChunkRepository(ABC):
    @abstractmethod
    async def insert_many(
        self, document_id: uuid.UUID, contents: list[str], embeddings: list[list[float]]
    ) -> None: ...

    @abstractmethod
    async def search_similar(
        self, document_id: uuid.UUID, query_embedding: list[float], top_k: int
    ) -> list[Chunk]:
        """Nearest chunks to `query_embedding` by cosine distance, for this document only."""
