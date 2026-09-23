import asyncpg
from pgvector.asyncpg import register_vector


class Database:
    """Owns the connection pool's lifecycle and schema. Schema changes are
    plain additive `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` statements run
    on startup rather than a migration tool — a deliberate choice while the
    project stays a single-developer prototype (see CLAUDE.md)."""

    def __init__(self, dsn: str, embedding_dimensions: int):
        self._dsn = dsn
        self._embedding_dimensions = embedding_dimensions
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        # A plain connection first: the vector extension must exist before any
        # pooled connection can register its type codec via `init=`, or that
        # registration fails on a database that has never seen it before.
        conn = await asyncpg.connect(self._dsn)
        try:
            await self._migrate(conn)
        finally:
            await conn.close()

        self.pool = await asyncpg.create_pool(self._dsn, init=register_vector)

    async def disconnect(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def _migrate(self, conn: asyncpg.Connection) -> None:
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
        await conn.execute(
            "ALTER TABLE documents ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'ready'"
        )
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
                embedding VECTOR({self._embedding_dimensions}) NOT NULL
            )
            """
        )
