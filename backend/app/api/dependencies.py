from typing import Annotated

import asyncpg
from fastapi import Depends, Request

from app.config import Settings, get_settings
from app.providers.chat_completion import OpenAIChatCompletionProvider
from app.providers.embeddings import OpenAIEmbeddingProvider
from app.repositories.postgres import PostgresChunkRepository, PostgresDocumentRepository
from app.services.chat_service import ChatService
from app.services.chunking import TextChunker
from app.services.document_ingestion import DocumentIngestionService
from app.services.embedding_batcher import BatchEmbedder
from app.services.text_extraction import DocumentTextExtractor

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool


PoolDep = Annotated[asyncpg.Pool, Depends(get_db_pool)]


def get_document_repository(pool: PoolDep) -> PostgresDocumentRepository:
    return PostgresDocumentRepository(pool)


def get_chunk_repository(pool: PoolDep) -> PostgresChunkRepository:
    return PostgresChunkRepository(pool)


DocumentRepositoryDep = Annotated[PostgresDocumentRepository, Depends(get_document_repository)]
ChunkRepositoryDep = Annotated[PostgresChunkRepository, Depends(get_chunk_repository)]


def get_embedding_provider(settings: SettingsDep) -> OpenAIEmbeddingProvider:
    return OpenAIEmbeddingProvider(api_key=settings.openai_api_key, model=settings.embedding_model)


def get_chat_provider(settings: SettingsDep) -> OpenAIChatCompletionProvider:
    return OpenAIChatCompletionProvider(api_key=settings.openai_api_key, model=settings.openai_model)


EmbeddingProviderDep = Annotated[OpenAIEmbeddingProvider, Depends(get_embedding_provider)]
ChatProviderDep = Annotated[OpenAIChatCompletionProvider, Depends(get_chat_provider)]


def get_document_ingestion_service(
    document_repository: DocumentRepositoryDep,
    chunk_repository: ChunkRepositoryDep,
    embedding_provider: EmbeddingProviderDep,
    settings: SettingsDep,
) -> DocumentIngestionService:
    return DocumentIngestionService(
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        text_extractor=DocumentTextExtractor(),
        chunker=TextChunker(chunk_size=settings.chunk_size, overlap=settings.chunk_overlap),
        embedder=BatchEmbedder(embedding_provider, batch_size=settings.embedding_batch_size),
    )


def get_chat_service(
    document_repository: DocumentRepositoryDep,
    chunk_repository: ChunkRepositoryDep,
    embedding_provider: EmbeddingProviderDep,
    chat_provider: ChatProviderDep,
    settings: SettingsDep,
) -> ChatService:
    return ChatService(
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        embedding_provider=embedding_provider,
        chat_provider=chat_provider,
        top_k=settings.top_k,
    )


DocumentIngestionServiceDep = Annotated[DocumentIngestionService, Depends(get_document_ingestion_service)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
