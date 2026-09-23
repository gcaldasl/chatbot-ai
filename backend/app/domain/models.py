import uuid
from dataclasses import dataclass
from enum import StrEnum


class DocumentStatus(StrEnum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Document:
    """A document known to the system. `characters`/`chunk_count` are only
    populated once `status` is READY; `error` only once it is FAILED."""

    id: uuid.UUID
    filename: str
    status: DocumentStatus
    characters: int | None = None
    chunk_count: int | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class Chunk:
    """A stored chunk of a document's text, as retrieved by similarity search."""

    chunk_index: int
    content: str
