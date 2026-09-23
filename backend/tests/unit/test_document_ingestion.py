import uuid

import pytest

from app.domain.models import DocumentStatus
from app.services.chunking import TextChunker
from app.services.document_ingestion import DocumentIngestionService
from app.services.embedding_batcher import BatchEmbedder
from app.services.text_extraction import DocumentTextExtractor, TextExtractor
from tests.unit.fakes import FakeChunkRepository, FakeDocumentRepository, FakeEmbeddingProvider


class StaticTextExtractor(TextExtractor):
    """Always returns the same text, regardless of input — lets tests avoid
    depending on real PDF/text parsing."""

    def __init__(self, text: str):
        self._text = text

    def supports(self, filename: str) -> bool:
        return True

    def extract(self, content: bytes) -> str:
        return self._text


def make_service(text: str, chunk_size: int = 1000, overlap: int = 150, batch_size: int = 200):
    documents = FakeDocumentRepository()
    chunks = FakeChunkRepository()
    embedding_provider = FakeEmbeddingProvider()
    service = DocumentIngestionService(
        document_repository=documents,
        chunk_repository=chunks,
        text_extractor=DocumentTextExtractor(extractors=[StaticTextExtractor(text)]),
        chunker=TextChunker(chunk_size=chunk_size, overlap=overlap),
        embedder=BatchEmbedder(embedding_provider, batch_size=batch_size),
    )
    return service, documents, chunks, embedding_provider


@pytest.mark.asyncio
async def test_create_pending_inserts_a_processing_document():
    service, documents, _, _ = make_service(text="irrelevant")
    document_id = uuid.uuid4()

    await service.create_pending(document_id, "report.txt")

    document = await documents.get(document_id)
    assert document is not None
    assert document.status is DocumentStatus.PROCESSING


@pytest.mark.asyncio
async def test_process_marks_document_ready_with_correct_counts():
    service, documents, chunks, embedder = make_service(text="a" * 2500, chunk_size=1000, overlap=150)
    document_id = uuid.uuid4()
    await service.create_pending(document_id, "report.txt")

    await service.process(document_id, "report.txt", b"irrelevant bytes")

    document = await documents.get(document_id)
    assert document.status is DocumentStatus.READY
    assert document.characters == 2500
    assert document.chunk_count == 3
    assert len(chunks.inserted) == 1
    assert len(chunks.inserted[0][1]) == 3  # 3 chunk contents stored


@pytest.mark.asyncio
async def test_process_batches_embeddings_for_large_documents():
    # 539 chunks worth of text at chunk_size=1000/overlap=150 (step 850) —
    # the exact shape that used to exceed OpenAI's per-request limits.
    text = "x" * 457501
    service, documents, _, embedder = make_service(text=text, chunk_size=1000, overlap=150, batch_size=200)
    document_id = uuid.uuid4()
    await service.create_pending(document_id, "big.txt")

    await service.process(document_id, "big.txt", b"irrelevant")

    document = await documents.get(document_id)
    assert document.status is DocumentStatus.READY
    assert [len(call) for call in embedder.calls] == [200, 200, 139]


@pytest.mark.asyncio
async def test_process_marks_failed_when_extraction_yields_no_text():
    service, documents, chunks, _ = make_service(text="   ")  # whitespace only -> empty after strip
    document_id = uuid.uuid4()
    await service.create_pending(document_id, "empty.txt")

    await service.process(document_id, "empty.txt", b"")

    document = await documents.get(document_id)
    assert document.status is DocumentStatus.FAILED
    assert document.error == "Could not extract text from the document."
    assert chunks.inserted == []


@pytest.mark.asyncio
async def test_process_marks_failed_and_records_message_on_unexpected_exception():
    class ExplodingChunkRepository(FakeChunkRepository):
        async def insert_many(self, document_id, contents, embeddings):
            raise RuntimeError('invalid byte sequence for encoding "UTF8": 0x00')

    documents = FakeDocumentRepository()
    chunks = ExplodingChunkRepository()
    service = DocumentIngestionService(
        document_repository=documents,
        chunk_repository=chunks,
        text_extractor=DocumentTextExtractor(extractors=[StaticTextExtractor("some real text")]),
        chunker=TextChunker(chunk_size=1000, overlap=150),
        embedder=BatchEmbedder(FakeEmbeddingProvider(), batch_size=200),
    )
    document_id = uuid.uuid4()
    await service.create_pending(document_id, "doc.txt")

    await service.process(document_id, "doc.txt", b"")

    document = await documents.get(document_id)
    assert document.status is DocumentStatus.FAILED
    assert document.error == 'invalid byte sequence for encoding "UTF8": 0x00'
