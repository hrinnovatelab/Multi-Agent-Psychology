from __future__ import annotations

from dataclasses import asdict

from app.agents.base import BaseAgent
from app.models import Claim, Confidence, EpistemicType, ValidationResult
from app.utils.prompts import PromptRepository


class EpistemicValidatorAgent(BaseAgent):
    async def validate(self, claim: Claim, prompts: PromptRepository) -> ValidationResult:
        context = {"claim": asdict(claim)}
        payload = await self.call("validation", prompts.compose(None, "system/validator.md", context), context)
        payload["epistemic_type"] = EpistemicType(payload["epistemic_type"].upper())
        payload["confidence"] = Confidence(payload["confidence"].lower())
        return ValidationResult(claim.claim_id, claim.claim, claim.agent, **payload)
