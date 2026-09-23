import uuid

import asyncpg

from app.domain.models import Chunk, Document, DocumentStatus
from app.repositories.base import ChunkRepository, DocumentRepository


class PostgresDocumentRepository(DocumentRepository):
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def create(self, document_id: uuid.UUID, filename: str) -> None:
        await self._pool.execute(
            "INSERT INTO documents (id, filename, status) VALUES ($1, $2, $3)",
            document_id,
            filename,
            DocumentStatus.PROCESSING.value,
        )

    async def get(self, document_id: uuid.UUID) -> Document | None:
        row = await self._pool.fetchrow(
            "SELECT id, filename, status, characters, chunk_count, error FROM documents WHERE id = $1",
            document_id,
        )
        if row is None:
            return None

        return Document(
            id=row["id"],
            filename=row["filename"],
            status=DocumentStatus(row["status"]),
            characters=row["characters"],
            chunk_count=row["chunk_count"],
            error=row["error"],
        )

    async def mark_ready(self, document_id: uuid.UUID, characters: int, chunk_count: int) -> None:
        await self._pool.execute(
            """
            UPDATE documents
            SET status = $2, characters = $3, chunk_count = $4, error = NULL
            WHERE id = $1
            """,
            document_id,
            DocumentStatus.READY.value,
            characters,
            chunk_count,
        )

    async def mark_failed(self, document_id: uuid.UUID, error: str) -> None:
        await self._pool.execute(
            "UPDATE documents SET status = $2, error = $3 WHERE id = $1",
            document_id,
            DocumentStatus.FAILED.value,
            error[:500],
        )


class PostgresChunkRepository(ChunkRepository):
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def insert_many(
        self, document_id: uuid.UUID, contents: list[str], embeddings: list[list[float]]
    ) -> None:
        async with self._pool.acquire() as conn, conn.transaction():
            await conn.executemany(
                "INSERT INTO chunks (document_id, chunk_index, content, embedding) VALUES ($1, $2, $3, $4)",
                [
                    (document_id, index, content, embedding)
                    for index, (content, embedding) in enumerate(zip(contents, embeddings, strict=True))
                ],
            )

    async def search_similar(
        self, document_id: uuid.UUID, query_embedding: list[float], top_k: int
    ) -> list[Chunk]:
        rows = await self._pool.fetch(
            """
            SELECT chunk_index, content FROM chunks
            WHERE document_id = $1
            ORDER BY embedding <=> $2
            LIMIT $3
            """,
            document_id,
            query_embedding,
            top_k,
        )
        return [Chunk(chunk_index=row["chunk_index"], content=row["content"]) for row in rows]
