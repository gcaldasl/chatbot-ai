from pydantic import BaseModel


class ChatRequest(BaseModel):
    document_id: str
    message: str


class Source(BaseModel):
    index: int
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


class UploadDocumentResponse(BaseModel):
    id: str
    filename: str
    status: str


class DocumentStatusResponse(BaseModel):
    id: str
    filename: str
    status: str
    characters: int | None
    chunks: int | None
    error: str | None
