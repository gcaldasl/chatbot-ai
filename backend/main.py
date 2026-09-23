"""Entrypoint kept at the repo root so `uv run uvicorn main:app` and the
Dockerfile's CMD keep working unchanged. All actual code lives in app/."""

from app.main import app

__all__ = ["app"]
