from __future__ import annotations

from typing import Any

from app.providers.base import LLMProvider, ProviderError


class BaseAgent:
    def __init__(self, provider: LLMProvider, retries: int) -> None:
        self.provider = provider
        self.retries = retries

    async def call(self, task: str, prompt: str, context: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for _ in range(self.retries + 1):
            try:
                return await self.provider.generate(task=task, prompt=prompt, context=context)
            except Exception as exc:
                last_error = exc
        raise ProviderError(f"Task '{task}' failed after {self.retries + 1} attempt(s): {last_error}")
