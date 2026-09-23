from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextChunker:
    """Naive fixed-size split with overlap, in characters (not tokens)."""

    chunk_size: int = 1000
    overlap: int = 150

    def chunk(self, text: str) -> list[str]:
        chunks: list[str] = []
        start = 0
        while start < len(text):
            piece = text[start : start + self.chunk_size].strip()
            if piece:
                chunks.append(piece)
            start += self.chunk_size - self.overlap
        return chunks
