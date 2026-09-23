import uuid
from dataclasses import dataclass

from app.api.schemas import Source
from app.domain.exceptions import (
    DocumentNotFoundError,
    DocumentNotReadyError,
    DocumentProcessingFailedError,
)
from app.domain.models import DocumentStatus
from app.providers.chat_completion import ChatCompletionProvider, ChatMessage
from app.providers.embeddings import EmbeddingProvider
from app.repositories.base import ChunkRepository, DocumentRepository

SYSTEM_PROMPT_TEMPLATE = (
    "You answer questions using only the numbered excerpts below, retrieved from "
    "the uploaded document. Cite the excerpt number(s) you relied on inline, right "
    "after the relevant part of your answer, like [1] or [2][3]. If the answer "
    "isn't in the excerpts, say you don't know and cite nothing. Reply in the same "
    "language the question was asked in.\n\nExcerpts:\n{context}"
)


@dataclass(frozen=True, slots=True)
class Answer:
    text: str
    sources: list[Source]


class ChatService:
    """Answers a question about a document via retrieval-augmented generation:
    embed the question, fetch the nearest stored chunks, and ask the chat
    model to answer using only those excerpts."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        embedding_provider: EmbeddingProvider,
        chat_provider: ChatCompletionProvider,
        top_k: int = 5,
    ):
        self._documents = document_repository
        self._chunks = chunk_repository
        self._embeddings = embedding_provider
        self._chat = chat_provider
        self._top_k = top_k

    async def answer(self, document_id: uuid.UUID, question: str) -> Answer:
        document = await self._documents.get(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        if document.status is DocumentStatus.PROCESSING:
            raise DocumentNotReadyError(document.status)
        if document.status is DocumentStatus.FAILED:
            raise DocumentProcessingFailedError(document.error or "Document processing failed.")

        [question_embedding] = await self._embeddings.embed([question])
        chunks = await self._chunks.search_similar(document_id, question_embedding, self._top_k)

        sources = [Source(index=i + 1, excerpt=chunk.content) for i, chunk in enumerate(chunks)]
        context = "\n\n".join(f"[{source.index}] {source.excerpt}" for source in sources)

        messages: list[ChatMessage] = [
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(context=context)},
            {"role": "user", "content": question},
        ]
        answer_text = await self._chat.complete(messages)

        return Answer(text=answer_text, sources=sources)
