import uuid

import pytest

from app.domain.exceptions import (
    DocumentNotFoundError,
    DocumentNotReadyError,
    DocumentProcessingFailedError,
)
from app.domain.models import Chunk, Document, DocumentStatus
from app.services.chat_service import ChatService
from tests.unit.fakes import (
    FakeChatCompletionProvider,
    FakeChunkRepository,
    FakeDocumentRepository,
    FakeEmbeddingProvider,
)


def make_service(
    document: Document | None,
    search_results: list[Chunk] | None = None,
    chat_response: str = "the answer [1]",
):
    documents = FakeDocumentRepository()
    if document is not None:
        documents.documents[document.id] = document
    chunks = FakeChunkRepository(search_results=search_results)
    embedding_provider = FakeEmbeddingProvider()
    chat_provider = FakeChatCompletionProvider(response=chat_response)
    service = ChatService(
        document_repository=documents,
        chunk_repository=chunks,
        embedding_provider=embedding_provider,
        chat_provider=chat_provider,
        top_k=5,
    )
    return service, documents, chunks, embedding_provider, chat_provider


@pytest.mark.asyncio
async def test_raises_when_document_does_not_exist():
    service, *_ = make_service(document=None)

    with pytest.raises(DocumentNotFoundError):
        await service.answer(uuid.uuid4(), "What is this about?")


@pytest.mark.asyncio
async def test_raises_when_document_is_still_processing():
    document_id = uuid.uuid4()
    document = Document(id=document_id, filename="x.txt", status=DocumentStatus.PROCESSING)
    service, *_ = make_service(document=document)

    with pytest.raises(DocumentNotReadyError):
        await service.answer(document_id, "What is this about?")


@pytest.mark.asyncio
async def test_raises_with_stored_reason_when_document_processing_failed():
    document_id = uuid.uuid4()
    document = Document(
        id=document_id, filename="x.txt", status=DocumentStatus.FAILED, error="Could not extract text."
    )
    service, *_ = make_service(document=document)

    with pytest.raises(DocumentProcessingFailedError) as exc_info:
        await service.answer(document_id, "What is this about?")
    assert exc_info.value.reason == "Could not extract text."


@pytest.mark.asyncio
async def test_returns_answer_with_numbered_sources_matching_retrieved_chunks():
    document_id = uuid.uuid4()
    document = Document(id=document_id, filename="x.txt", status=DocumentStatus.READY)
    retrieved = [
        Chunk(chunk_index=3, content="Aurora foi lançado em 2021."),
        Chunk(chunk_index=0, content="Zuraio foi fundada em 2020."),
    ]
    service, documents, chunks, embedder, chat_provider = make_service(
        document=document, search_results=retrieved, chat_response="Em 2021. [1]"
    )

    answer = await service.answer(document_id, "Quando o Aurora foi lançado?")

    assert answer.text == "Em 2021. [1]"
    assert [s.index for s in answer.sources] == [1, 2]
    assert [s.excerpt for s in answer.sources] == [c.content for c in retrieved]


@pytest.mark.asyncio
async def test_embeds_the_question_and_searches_within_the_right_document():
    document_id = uuid.uuid4()
    document = Document(id=document_id, filename="x.txt", status=DocumentStatus.READY)
    service, documents, chunks, embedder, _ = make_service(document=document, search_results=[])

    await service.answer(document_id, "minha pergunta")

    assert embedder.calls == [["minha pergunta"]]
    assert len(chunks.search_calls) == 1
    searched_document_id, _query_embedding, top_k = chunks.search_calls[0]
    assert searched_document_id == document_id
    assert top_k == 5


@pytest.mark.asyncio
async def test_prompts_the_chat_model_with_numbered_excerpts_and_the_question():
    document_id = uuid.uuid4()
    document = Document(id=document_id, filename="x.txt", status=DocumentStatus.READY)
    retrieved = [Chunk(chunk_index=0, content="a senha é 42")]
    service, *_rest, chat_provider = make_service(document=document, search_results=retrieved)

    await service.answer(document_id, "qual a senha?")

    [messages] = chat_provider.calls
    assert messages[0]["role"] == "system"
    assert "[1] a senha é 42" in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "qual a senha?"}
