from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.models import Synthesis
from app.utils.prompts import PromptRepository


class SynthesizerAgent(BaseAgent):
    role_name = "synthesizer"

    async def synthesize(self, context: dict[str, Any], prompts: PromptRepository) -> Synthesis:
        payload = await self.call("synthesis", prompts.compose(None, "system/synthesizer.md", context), context)
        payload.setdefault("missing_participants", list(context.get("failed_agents", {})))
        return Synthesis(**payload)
