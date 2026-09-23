import uuid

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.api.dependencies import DocumentIngestionServiceDep, DocumentRepositoryDep, SettingsDep
from app.api.schemas import DocumentStatusResponse, UploadDocumentResponse

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = (".txt", ".pdf")


@router.post("", status_code=202, response_model=UploadDocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    ingestion_service: DocumentIngestionServiceDep,
    settings: SettingsDep,
    file: UploadFile = File(...),
) -> UploadDocumentResponse:
    if not file.filename or not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported.")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File is too large.")

    document_id = uuid.uuid4()
    await ingestion_service.create_pending(document_id, file.filename)
    background_tasks.add_task(ingestion_service.process, document_id, file.filename, content)

    return UploadDocumentResponse(id=str(document_id), filename=file.filename, status="processing")


@router.get("/{document_id}", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: uuid.UUID,
    document_repository: DocumentRepositoryDep,
) -> DocumentStatusResponse:
    document = await document_repository.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    return DocumentStatusResponse(
        id=str(document.id),
        filename=document.filename,
        status=document.status.value,
        characters=document.characters,
        chunks=document.chunk_count,
        error=document.error,
    )
