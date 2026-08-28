from __future__ import annotations

from dataclasses import asdict

from app.agents.base import BaseAgent
from app.models import CaseRecord, IntakeResult
from app.utils.prompts import PromptRepository


class IntakeAgent(BaseAgent):
    role_name = "intake"

    async def run(self, case: CaseRecord, prompts: PromptRepository) -> IntakeResult:
        context = {"case": asdict(case)}
        payload = await self.call("intake", prompts.compose(None, "system/intake.md", context), context)
        return IntakeResult(case_name=case.name, **payload)
