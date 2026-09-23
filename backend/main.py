import asyncio
import io
import os
import uuid
from contextlib import asynccontextmanager

import asyncpg
import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pgvector.asyncpg import register_vector
from pydantic import BaseModel
from pypdf import PdfReader

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = 1536
EMBEDDING_BATCH_SIZE = 200
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://zuraio:zuraio@localhost:5432/zuraio")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 5
MAX_UPLOAD_BYTES = 100 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY,
                filename TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        await conn.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'ready'")
        await conn.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS characters INT")
        await conn.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS chunk_count INT")
        await conn.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS error TEXT")
        await conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                chunk_index INT NOT NULL,
                content TEXT NOT NULL,
                embedding VECTOR({EMBEDDING_DIMENSIONS}) NOT NULL
            )
            """
        )
    finally:
        await conn.close()

    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL, init=register_vector)
    yield
    await app.state.db_pool.close()


app = FastAPI(title="Agente de Conhecimento API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    document_id: str
    message: str


class Source(BaseModel):
    index: int
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


def extract_text(filename: str, content: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = content.decode("utf-8", errors="ignore")

    return text.replace("\x00", "")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a single batch. Callers must keep `texts` under OpenAI's per-request
    array/token limits — use embed_in_batches for arbitrarily long lists."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured on the server.")

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            OPENAI_EMBEDDINGS_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": EMBEDDING_MODEL, "input": texts},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Embedding request failed: {response.status_code} {response.text[:300]}",
        )

    data = response.json()["data"]
    return [item["embedding"] for item in sorted(data, key=lambda item: item["index"])]


async def embed_in_batches(texts: list[str]) -> list[list[float]]:
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start : start + EMBEDDING_BATCH_SIZE]
        embeddings.extend(await embed_texts(batch))
    return embeddings


async def process_document(document_id: uuid.UUID, filename: str, content: bytes) -> None:
    """Runs after the upload response is already sent. Extraction is offloaded to a
    thread (pypdf is blocking/CPU-bound); embeddings are requested in batches so a
    large document can't exceed OpenAI's per-request array/token limits."""
    pool: asyncpg.Pool = app.state.db_pool
    try:
        text = (await asyncio.to_thread(extract_text, filename, content)).strip()
        if not text:
            raise ValueError("Could not extract text from the document.")

        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("Could not split the document into chunks.")

        embeddings = await embed_in_batches(chunks)

        async with pool.acquire() as conn, conn.transaction():
            await conn.executemany(
                "INSERT INTO chunks (document_id, chunk_index, content, embedding) VALUES ($1, $2, $3, $4)",
                [
                    (document_id, index, chunk, embedding)
                    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ],
            )
            await conn.execute(
                """
                UPDATE documents
                SET status = 'ready', characters = $2, chunk_count = $3, error = NULL
                WHERE id = $1
                """,
                document_id,
                len(text),
                len(chunks),
            )
    except Exception as exc:
        message = exc.detail if isinstance(exc, HTTPException) else str(exc)
        message = message or exc.__class__.__name__
        await pool.execute(
            "UPDATE documents SET status = 'failed', error = $2 WHERE id = $1",
            document_id,
            str(message)[:500],
        )


@app.post("/api/documents", status_code=202)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith((".txt", ".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported.")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large.")

    document_id = uuid.uuid4()
    pool: asyncpg.Pool = app.state.db_pool
    await pool.execute(
        "INSERT INTO documents (id, filename, status) VALUES ($1, $2, 'processing')",
        document_id,
        file.filename,
    )

    background_tasks.add_task(process_document, document_id, file.filename, content)

    return {"id": str(document_id), "filename": file.filename, "status": "processing"}


@app.get("/api/documents/{document_id}")
async def get_document(document_id: uuid.UUID):
    pool: asyncpg.Pool = app.state.db_pool
    row = await pool.fetchrow(
        "SELECT id, filename, status, characters, chunk_count, error FROM documents WHERE id = $1",
        document_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    return {
        "id": str(row["id"]),
        "filename": row["filename"],
        "status": row["status"],
        "characters": row["characters"],
        "chunks": row["chunk_count"],
        "error": row["error"],
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        document_id = uuid.UUID(request.document_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Document not found. Upload a document first.")

    pool: asyncpg.Pool = app.state.db_pool
    document = await pool.fetchrow("SELECT status, error FROM documents WHERE id = $1", document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found. Upload a document first.")
    if document["status"] == "processing":
        raise HTTPException(status_code=409, detail="Document is still being processed.")
    if document["status"] == "failed":
        raise HTTPException(status_code=422, detail=document["error"] or "Document processing failed.")

    [question_embedding] = await embed_texts([request.message])

    rows = await pool.fetch(
        """
        SELECT content FROM chunks
        WHERE document_id = $1
        ORDER BY embedding <=> $2
        LIMIT $3
        """,
        document_id,
        question_embedding,
        TOP_K,
    )
    sources = [Source(index=i + 1, excerpt=row["content"]) for i, row in enumerate(rows)]
    context = "\n\n".join(f"[{source.index}] {source.excerpt}" for source in sources)

    messages = [
        {
            "role": "system",
            "content": (
                "You answer questions using only the numbered excerpts below, retrieved from "
                "the uploaded document. Cite the excerpt number(s) you relied on inline, right "
                "after the relevant part of your answer, like [1] or [2][3]. If the answer "
                "isn't in the excerpts, say you don't know and cite nothing. Reply in the same "
                "language the question was asked in.\n\n"
                f"Excerpts:\n{context}"
            ),
        },
        {"role": "user", "content": request.message},
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            OPENAI_CHAT_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": OPENAI_MODEL, "messages": messages},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="LLM request failed.")

    answer = response.json()["choices"][0]["message"]["content"]
    return ChatResponse(answer=answer, sources=sources)
