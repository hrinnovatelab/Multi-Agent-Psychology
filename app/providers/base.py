from __future__ import annotations

from typing import Any, Protocol


class ProviderError(RuntimeError):
    """Raised when a model provider cannot return a usable response."""


class LLMProvider(Protocol):
    async def generate(
        self,
        *,
        task: str,
        prompt: str,
        context: dict[str, Any],
    ) -> dict[str, Any]: ...
