from abc import ABC, abstractmethod
from typing import TypedDict

import httpx

from app.domain.exceptions import ChatCompletionError


class ChatMessage(TypedDict):
    role: str
    content: str


class ChatCompletionProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[ChatMessage]) -> str: ...


class OpenAIChatCompletionProvider(ChatCompletionProvider):
    CHAT_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(
        self,
        api_key: str | None,
        model: str,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._transport = transport

    async def complete(self, messages: list[ChatMessage]) -> str:
        if not self._api_key:
            raise ChatCompletionError("OPENAI_API_KEY is not configured on the server.")

        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                self.CHAT_URL,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self._model, "messages": messages},
            )

        if response.status_code != 200:
            raise ChatCompletionError(f"LLM request failed: {response.status_code} {response.text[:300]}")

        return response.json()["choices"][0]["message"]["content"]
