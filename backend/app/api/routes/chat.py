import uuid

from fastapi import APIRouter, HTTPException

from app.api.dependencies import ChatServiceDep
from app.api.schemas import ChatRequest, ChatResponse
from app.domain.exceptions import (
    ChatCompletionError,
    DocumentNotFoundError,
    DocumentNotReadyError,
    DocumentProcessingFailedError,
    EmbeddingProviderError,
)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, chat_service: ChatServiceDep) -> ChatResponse:
    try:
        document_id = uuid.UUID(request.document_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Document not found. Upload a document first.") from None

    try:
        answer = await chat_service.answer(document_id, request.message)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DocumentNotReadyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except DocumentProcessingFailedError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (EmbeddingProviderError, ChatCompletionError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(answer=answer.text, sources=answer.sources)
