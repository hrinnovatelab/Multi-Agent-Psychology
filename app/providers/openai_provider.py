from __future__ import annotations

import json
import os
from typing import Any

from app.providers.base import ProviderError


class OpenAIProvider:
    """Thin OpenAI Responses API adapter; it contains no workflow policy."""

    def __init__(self, model: str, temperature: float, max_output_tokens: int) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OPENAI_API_KEY is not set. Use --provider mock for an offline run.")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ProviderError("The 'openai' package is not installed") from exc
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    async def generate(
        self,
        *,
        task: str,
        prompt: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        del context
        try:
            response = await self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": "Return one valid JSON object only. Do not include hidden reasoning.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
            )
            payload = json.loads(response.output_text)
        except Exception as exc:  # SDK exceptions are intentionally translated here.
            raise ProviderError(f"OpenAI task '{task}' failed: {exc}") from exc
        if not isinstance(payload, dict):
            raise ProviderError(f"OpenAI task '{task}' did not return a JSON object")
        return payload
