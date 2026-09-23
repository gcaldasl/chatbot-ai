import io
from abc import ABC, abstractmethod

from pypdf import PdfReader

from app.domain.exceptions import UnsupportedFileTypeError


class TextExtractor(ABC):
    """One strategy for pulling plain text out of a file's raw bytes."""

    @abstractmethod
    def supports(self, filename: str) -> bool: ...

    @abstractmethod
    def extract(self, content: bytes) -> str: ...


class PlainTextExtractor(TextExtractor):
    def supports(self, filename: str) -> bool:
        return filename.lower().endswith(".txt")

    def extract(self, content: bytes) -> str:
        return content.decode("utf-8", errors="ignore")


class PdfTextExtractor(TextExtractor):
    def supports(self, filename: str) -> bool:
        return filename.lower().endswith(".pdf")

    def extract(self, content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)


class DocumentTextExtractor:
    """Dispatches to the first supporting TextExtractor strategy, then
    sanitizes the result: Postgres TEXT columns reject embedded NUL bytes
    outright, and pypdf can emit them for PDFs with corrupted/custom font
    encodings (the same PDFs that log "fontTools is required..." warnings)."""

    def __init__(self, extractors: list[TextExtractor] | None = None):
        self._extractors = (
            extractors if extractors is not None else [PlainTextExtractor(), PdfTextExtractor()]
        )

    def extract(self, filename: str, content: bytes) -> str:
        for extractor in self._extractors:
            if extractor.supports(filename):
                return extractor.extract(content).replace("\x00", "")
        raise UnsupportedFileTypeError(f"No text extractor available for '{filename}'.")
