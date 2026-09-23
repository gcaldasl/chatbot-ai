import asyncio
import uuid

from app.domain.exceptions import ChunkingError, TextExtractionError
from app.repositories.base import ChunkRepository, DocumentRepository
from app.services.chunking import TextChunker
from app.services.embedding_batcher import BatchEmbedder
from app.services.text_extraction import DocumentTextExtractor


class DocumentIngestionService:
    """Turns an uploaded file into searchable chunks: extract text, split it,
    embed it, and store it. `process` is designed to run as a background task
    — after the upload response is already sent — and never raises: any
    failure is caught and recorded on the document row instead of dying
    silently.

    Note on atomicity: chunk insertion and marking the document READY are two
    separate repository calls, not one transaction spanning both
    repositories. A crash between them would leave orphaned chunks and a
    document stuck at PROCESSING — the same class of failure already accepted
    for a mid-task process crash (see CLAUDE.md). A Unit-of-Work spanning both
    repositories would close that gap but isn't justified at this scale.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        text_extractor: DocumentTextExtractor,
        chunker: TextChunker,
        embedder: BatchEmbedder,
    ):
        self._documents = document_repository
        self._chunks = chunk_repository
        self._text_extractor = text_extractor
        self._chunker = chunker
        self._embedder = embedder

    async def create_pending(self, document_id: uuid.UUID, filename: str) -> None:
        await self._documents.create(document_id, filename)

    async def process(self, document_id: uuid.UUID, filename: str, content: bytes) -> None:
        try:
            text = (await asyncio.to_thread(self._text_extractor.extract, filename, content)).strip()
            if not text:
                raise TextExtractionError("Could not extract text from the document.")

            chunks = self._chunker.chunk(text)
            if not chunks:
                raise ChunkingError("Could not split the document into chunks.")

            embeddings = await self._embedder.embed_all(chunks)

            await self._chunks.insert_many(document_id, chunks, embeddings)
            await self._documents.mark_ready(document_id, characters=len(text), chunk_count=len(chunks))
        except Exception as exc:
            await self._documents.mark_failed(document_id, str(exc) or exc.__class__.__name__)
