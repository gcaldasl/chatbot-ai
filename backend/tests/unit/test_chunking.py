from app.services.chunking import TextChunker


def test_empty_text_yields_no_chunks():
    assert TextChunker().chunk("") == []


def test_short_text_is_a_single_chunk():
    assert TextChunker(chunk_size=1000, overlap=150).chunk("hello world") == ["hello world"]


def test_splits_long_text_with_expected_sizes_and_overlap():
    text = "a" * 2500
    chunks = TextChunker(chunk_size=1000, overlap=150).chunk(text)

    assert len(chunks) == 3
    assert [len(c) for c in chunks] == [1000, 1000, 800]


def test_no_chunk_exceeds_chunk_size():
    chunker = TextChunker(chunk_size=1000, overlap=150)
    for chunk in chunker.chunk("b" * 5000):
        assert len(chunk) <= 1000


def test_whitespace_only_regions_are_dropped():
    text = "word " * 400  # long enough to span multiple windows, mostly whitespace-padded
    chunks = TextChunker(chunk_size=50, overlap=10).chunk(text)

    assert all(chunk == chunk.strip() and chunk for chunk in chunks)
