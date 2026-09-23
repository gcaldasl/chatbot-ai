import httpx
import pytest

from app.domain.exceptions import ChatCompletionError, EmbeddingProviderError
from app.providers.chat_completion import OpenAIChatCompletionProvider
from app.providers.embeddings import OpenAIEmbeddingProvider


@pytest.mark.asyncio
async def test_embedding_provider_raises_when_api_key_missing():
    provider = OpenAIEmbeddingProvider(api_key=None, model="text-embedding-3-small")

    with pytest.raises(EmbeddingProviderError, match="OPENAI_API_KEY"):
        await provider.embed(["hello"])


@pytest.mark.asyncio
async def test_embedding_provider_returns_vectors_ordered_by_index():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-key"
        body = request.read()
        assert b'"model":"text-embedding-3-small"' in body
        # Deliberately out of order, to verify the provider re-sorts by index.
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 1, "embedding": [0.2]},
                    {"index": 0, "embedding": [0.1]},
                ]
            },
        )

    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        model="text-embedding-3-small",
        transport=httpx.MockTransport(handler),
    )

    embeddings = await provider.embed(["first", "second"])

    assert embeddings == [[0.1], [0.2]]


@pytest.mark.asyncio
async def test_embedding_provider_raises_with_status_and_body_on_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="array too long: max 2048 items")

    provider = OpenAIEmbeddingProvider(
        api_key="test-key", model="text-embedding-3-small", transport=httpx.MockTransport(handler)
    )

    with pytest.raises(EmbeddingProviderError, match="400"):
        await provider.embed(["x"] * 3000)


@pytest.mark.asyncio
async def test_chat_completion_provider_raises_when_api_key_missing():
    provider = OpenAIChatCompletionProvider(api_key=None, model="gpt-5.6-luna")

    with pytest.raises(ChatCompletionError, match="OPENAI_API_KEY"):
        await provider.complete([{"role": "user", "content": "oi"}])


@pytest.mark.asyncio
async def test_chat_completion_provider_returns_message_content():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"role": "assistant", "content": "42 [1]"}}]},
        )

    provider = OpenAIChatCompletionProvider(
        api_key="test-key", model="gpt-5.6-luna", transport=httpx.MockTransport(handler)
    )

    answer = await provider.complete([{"role": "user", "content": "qual a resposta?"}])

    assert answer == "42 [1]"


@pytest.mark.asyncio
async def test_chat_completion_provider_raises_with_status_and_body_on_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="invalid api key")

    provider = OpenAIChatCompletionProvider(
        api_key="bad-key", model="gpt-5.6-luna", transport=httpx.MockTransport(handler)
    )

    with pytest.raises(ChatCompletionError, match="401"):
        await provider.complete([{"role": "user", "content": "oi"}])
