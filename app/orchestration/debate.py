from __future__ import annotations

import asyncio
from copy import deepcopy

from app.agents.psychology import PsychologyAgent
from app.models import ClaimStatus, DebateState
from app.orchestration.claim_registry import ClaimRegistry
from app.utils.prompts import PromptRepository
from app.utils.time import iso_now


class DebateEngine:
    def __init__(
        self,
        agents: dict[str, PsychologyAgent],
        prompts: PromptRepository,
        allow_agent_revision: bool = True,
    ) -> None:
        self.agents = agents
        self.prompts = prompts
        self.allow_agent_revision = allow_agent_revision

    async def run(self, state: DebateState, rounds: int, registry: ClaimRegistry) -> None:
        for round_number in range(1, rounds + 1):
            await self.run_one_round(state, round_number, registry)

    async def run_one_round(
        self, state: DebateState, round_number: int, registry: ClaimRegistry
    ) -> None:
        participants = list(self.agents)
        state.events.append(_event("ROUND_STARTED", round=round_number))
        frozen = deepcopy(state.to_dict())
        tasks = []
        task_agents = []
        for index, critic_key in enumerate(participants):
            target_key = participants[(index + 1) % len(participants)]
            target_claim = next(
                (
                    claim
                    for claim in registry.claims.values()
                    if claim.agent == target_key and claim.status is not ClaimStatus.WITHDRAWN
                ),
                None,
            )
            if target_claim is not None:
                task_agents.append(critic_key)
                tasks.append(
                    self.agents[critic_key].critique(
                        target_key, target_claim, round_number, frozen, self.prompts
                    )
                )
        results = await asyncio.gather(*tasks, return_exceptions=True)
        critiques = []
        for critic_key, result in zip(task_agents, results, strict=True):
            if isinstance(result, BaseException):
                state.failed_agents[critic_key] = str(result)
            else:
                critiques.append(result)
        for critique in critiques:
            state.critiques.append(critique)
            registry.challenge(critique)
            state.events.append(_event("CLAIM_CHALLENGED", claim_id=critique.claim_id, round=round_number))

        if critiques and self.allow_agent_revision:
            revision_tasks = []
            revision_agents = []
            for claim in list(registry.claims.values()):
                challenges = [item for item in critiques if item.claim_id == claim.claim_id]
                if challenges:
                    revision_agents.append(claim.agent)
                    revision_tasks.append(
                        self.agents[claim.agent].revise(claim, challenges, round_number, self.prompts)
                    )
            results = await asyncio.gather(*revision_tasks, return_exceptions=True)
            revisions = []
            for agent_key, result in zip(revision_agents, results, strict=True):
                if isinstance(result, BaseException):
                    state.failed_agents[agent_key] = str(result)
                else:
                    revisions.append(result)
            for revision in revisions:
                state.revisions.append(revision)
                registry.apply_revision(revision)
                event_name = (
                    "CLAIM_WITHDRAWN"
                    if revision.decision.value == "WITHDRAW_CLAIM"
                    else "CLAIM_REVISED"
                )
                state.events.append(_event(event_name, claim_id=revision.claim_id, round=round_number))
        state.round_number = round_number


def _event(name: str, **details):
    from app.models import RunEvent

    return RunEvent(name, iso_now(), details)
