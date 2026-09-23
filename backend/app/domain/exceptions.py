"""Errors raised by the service layer. These carry no HTTP knowledge — the
API layer (app/api/routes/*) is solely responsible for translating them into
HTTP responses, so services stay testable and reusable outside FastAPI."""

import uuid

from app.domain.models import DocumentStatus


class DomainError(Exception):
    """Base class for expected, recoverable application errors."""


class UnsupportedFileTypeError(DomainError):
    pass


class TextExtractionError(DomainError):
    pass


class ChunkingError(DomainError):
    pass


class DocumentNotFoundError(DomainError):
    def __init__(self, document_id: uuid.UUID):
        self.document_id = document_id
        super().__init__("Document not found. Upload a document first.")


class DocumentNotReadyError(DomainError):
    def __init__(self, status: DocumentStatus):
        self.status = status
        super().__init__("Document is still being processed.")


class DocumentProcessingFailedError(DomainError):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class EmbeddingProviderError(DomainError):
    pass


class ChatCompletionError(DomainError):
    pass
