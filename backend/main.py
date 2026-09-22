import io
import os
import uuid

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
MAX_DOCUMENT_CHARS = 12000

app = FastAPI(title="Agente de Conhecimento API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

documents: dict[str, dict] = {}


class ChatRequest(BaseModel):
    document_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str


def extract_text(filename: str, content: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return content.decode("utf-8", errors="ignore")


@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith((".txt", ".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported.")

    content = await file.read()
    text = extract_text(file.filename, content).strip()
    if not text:
        raise HTTPException(status_code=422, detail="Could not extract text from the document.")

    document_id = str(uuid.uuid4())
    documents[document_id] = {"filename": file.filename, "text": text}
    return {"id": document_id, "filename": file.filename, "characters": len(text)}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    document = documents.get(request.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found. Upload a document first.")

    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured on the server.")

    context = document["text"][:MAX_DOCUMENT_CHARS]
    messages = [
        {
            "role": "system",
            "content": (
                "You answer questions using only the document below. "
                "If the answer isn't in the document, say you don't know. "
                "Reply in the same language the question was asked in.\n\n"
                f"Document:\n{context}"
            ),
        },
        {"role": "user", "content": request.message},
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": OPENAI_MODEL, "messages": messages},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="LLM request failed.")

    answer = response.json()["choices"][0]["message"]["content"]
    return ChatResponse(answer=answer)
