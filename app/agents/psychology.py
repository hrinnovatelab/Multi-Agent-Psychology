from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.agents.base import BaseAgent
from app.config import AgentSettings
from app.models import (
    AgentAnalysis,
    Claim,
    Confidence,
    Critique,
    EpistemicType,
    Revision,
    RevisionDecision,
)
from app.utils.prompts import PromptRepository


class PsychologyAgent(BaseAgent):
    def __init__(
        self,
        key: str,
        display_name: str,
        prompt_path: str,
        provider: Any,
        retries: int,
    ) -> None:
        super().__init__(provider, retries)
        self.key = key
        self.display_name = display_name
        self.prompt_path = prompt_path

    async def analyze(self, case: dict[str, Any], intake: dict[str, Any], prompts: PromptRepository) -> AgentAnalysis:
        context = {"agent": self.key, "case": case, "intake": intake}
        payload = await self.call(
            "analysis",
            prompts.compose(self.prompt_path, "debate/independent_analysis.md", context),
            context,
        )
        payload["confidence"] = Confidence(payload.get("confidence", "medium"))
        return AgentAnalysis(agent=self.key, lens=self.display_name, **payload)

    async def critique(
        self,
        target_agent: str,
        claim: Claim,
        round_number: int,
        state_snapshot: dict[str, Any],
        prompts: PromptRepository,
    ) -> Critique:
        context = {
            "agent": self.key,
            "target_agent": target_agent,
            "target_claim": asdict(claim),
            "round_number": round_number,
            "state_available_through_round": round_number - 1,
            "state": state_snapshot,
        }
        payload = await self.call(
            "critique",
            prompts.compose(self.prompt_path, "debate/critique_round.md", context),
            context,
        )
        return Critique(round_number, self.key, target_agent, claim.claim_id, **payload)

    async def revise(
        self,
        claim: Claim,
        challenges: list[Critique],
        round_number: int,
        prompts: PromptRepository,
    ) -> Revision:
        context = {
            "agent": self.key,
            "round_number": round_number,
            "claim": asdict(claim),
            "challenges": [asdict(item) for item in challenges],
        }
        payload = await self.call(
            "revision",
            prompts.compose(self.prompt_path, "debate/revision_round.md", context),
            context,
        )
        payload["decision"] = RevisionDecision(payload["decision"])
        return Revision(round_number, self.key, claim.claim_id, **payload)


def build_psychology_agents(
    settings: tuple[AgentSettings, ...],
    provider: Any,
    retries: int,
    prompts: PromptRepository | None = None,
) -> dict[str, PsychologyAgent]:
    agents: dict[str, PsychologyAgent] = {}
    for item in settings:
        if not item.enabled:
            continue
        if prompts is not None:
            prompts.read(item.prompt_path)
        agents[item.key] = PsychologyAgent(
            item.key,
            item.display_name,
            item.prompt_path,
            provider,
            retries,
        )
    return agents


def normalize_claim_payload(payload: dict[str, Any]) -> tuple[str, EpistemicType, list[str], Confidence]:
    return (
        str(payload["claim"]),
        EpistemicType(payload.get("epistemic_type", "HYPOTHESIS").upper()),
        [str(item) for item in payload.get("supporting_case_evidence", [])],
        Confidence(payload.get("confidence", "medium").lower()),
    )
