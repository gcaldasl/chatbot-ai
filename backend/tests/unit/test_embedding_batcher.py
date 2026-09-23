import pytest

from app.services.embedding_batcher import BatchEmbedder
from tests.unit.fakes import FakeEmbeddingProvider


@pytest.mark.asyncio
async def test_embeds_a_short_list_in_a_single_call():
    provider = FakeEmbeddingProvider()
    embedder = BatchEmbedder(provider, batch_size=200)

    embeddings = await embedder.embed_all(["a", "bb", "ccc"])

    assert len(provider.calls) == 1
    assert len(embeddings) == 3


@pytest.mark.asyncio
async def test_splits_a_long_list_into_batches_of_the_configured_size():
    provider = FakeEmbeddingProvider()
    embedder = BatchEmbedder(provider, batch_size=200)
    texts = [f"chunk-{i}" for i in range(539)]

    embeddings = await embedder.embed_all(texts)

    assert [len(call) for call in provider.calls] == [200, 200, 139]
    assert len(embeddings) == 539


@pytest.mark.asyncio
async def test_preserves_input_order_across_batches():
    provider = FakeEmbeddingProvider(dimensions=1)
    embedder = BatchEmbedder(provider, batch_size=2)

    embeddings = await embedder.embed_all(["a", "bb", "ccc", "dddd", "e"])

    # FakeEmbeddingProvider encodes each text's length as its embedding.
    assert embeddings == [[1.0], [2.0], [3.0], [4.0], [1.0]]


@pytest.mark.asyncio
async def test_empty_input_makes_no_calls():
    provider = FakeEmbeddingProvider()
    embedder = BatchEmbedder(provider, batch_size=200)

    embeddings = await embedder.embed_all([])

    assert embeddings == []
    assert provider.calls == []
