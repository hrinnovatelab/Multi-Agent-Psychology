from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

from app.agents import IntakeAgent, SynthesizerAgent, EpistemicValidatorAgent, build_psychology_agents
from app.config import AppConfig
from app.models import DebateState, OutputMode, RunEvent
from app.orchestration.claim_registry import ClaimRegistry
from app.orchestration.debate import DebateEngine
from app.orchestration.router import OutputPaths, route_outputs
from app.providers.base import LLMProvider, ProviderError
from app.utils.prompts import PromptRepository
from app.utils.time import iso_now, local_now


@dataclass(frozen=True, slots=True)
class RunResult:
    state: DebateState
    outputs: OutputPaths


async def run_critique(
    *,
    case,
    config: AppConfig,
    provider: LLMProvider,
    mode: OutputMode | None = None,
    rounds: int | None = None,
    root: Path = Path("."),
) -> RunResult:
    selected_mode = mode or config.output.mode
    selected_rounds = rounds if rounds is not None else config.debate.rounds
    if selected_rounds < 1:
        raise ValueError("rounds must be at least 1")
    prompts = PromptRepository(root / "prompts")
    agents = build_psychology_agents(config.agents, provider, config.runtime.retries)
    state = DebateState(
        run_id=f"RUN-{uuid.uuid4().hex[:12]}",
        case=case,
        enabled_agents=list(agents),
    )
    state.events.append(RunEvent("RUN_STARTED", iso_now(), {"mode": selected_mode.value, "rounds": selected_rounds}))
    checkpoint_dir = root / "checkpoints"
    try:
        intake_agent = IntakeAgent(provider, config.runtime.retries)
        state.events.append(RunEvent("CASE_PARSED", iso_now(), {"case": case.name}))
        state.intake = await intake_agent.run(case, prompts)
        state.unresolved_questions = list(state.intake.missing_information)
        state.events.append(RunEvent("INTAKE_COMPLETED", iso_now(), {"risk_flags": state.intake.risk_flags}))
        _checkpoint(checkpoint_dir, state, "intake")

        frozen_case = asdict(case)
        frozen_intake = asdict(state.intake)
        tasks = []
        agent_keys = list(agents)
        for key in agent_keys:
            state.events.append(RunEvent("AGENT_STARTED", iso_now(), {"agent": key, "phase": "independent"}))
            tasks.append(agents[key].analyze(frozen_case, frozen_intake, prompts))
        if config.debate.parallel_independent_analysis:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for task in tasks:
                try:
                    results.append(await task)
                except Exception as exc:
                    results.append(exc)
        for key, result in zip(agent_keys, results, strict=True):
            if isinstance(result, BaseException):
                state.failed_agents[key] = str(result)
            else:
                state.analyses[key] = result
                state.events.append(RunEvent("AGENT_COMPLETED", iso_now(), {"agent": key, "phase": "independent"}))
        if len(state.analyses) < 2:
            raise ProviderError("Fewer than two psychology agents completed independent analysis")
        if state.failed_agents:
            agents = {key: agent for key, agent in agents.items() if key in state.analyses}
            state.enabled_agents = list(agents)

        registry = ClaimRegistry(state.claim_registry)
        for key in state.enabled_agents:
            for payload in state.analyses[key].claims:
                claim = registry.register(key, payload)
                state.events.append(RunEvent("CLAIM_CREATED", iso_now(), {"claim_id": claim.claim_id, "agent": key}))
        _checkpoint(checkpoint_dir, state, "independent")

        debate = DebateEngine(agents, prompts, config.debate.allow_agent_revision)
        for round_number in range(1, selected_rounds + 1):
            await debate.run_one_round(state, round_number, registry)
            _checkpoint(checkpoint_dir, state, f"round-{round_number}")

        validator = EpistemicValidatorAgent(provider, config.runtime.retries)
        state.events.append(RunEvent("VALIDATION_STARTED", iso_now()))
        validations = await asyncio.gather(
            *(validator.validate(claim, prompts) for claim in registry.claims.values())
        )
        state.validation_results.extend(validations)
        state.events.append(RunEvent("VALIDATION_COMPLETED", iso_now(), {"claims": len(validations)}))
        _checkpoint(checkpoint_dir, state, "validation")

        synthesizer = SynthesizerAgent(provider, config.runtime.retries)
        synthesis_context = {
            "case": state.to_dict()["case"],
            "analyses": state.to_dict()["analyses"],
            "claim_registry": state.to_dict()["claim_registry"],
            "validation_results": state.to_dict()["validation_results"],
            "unresolved_questions": state.unresolved_questions,
            "failed_agents": state.failed_agents,
        }
        state.synthesis = await synthesizer.synthesize(synthesis_context, prompts)
        state.events.append(RunEvent("SYNTHESIS_COMPLETED", iso_now()))
        _checkpoint(checkpoint_dir, state, "synthesis")

        outputs = route_outputs(
            state,
            selected_mode,
            local_now(),
            root,
            save_markdown=config.logging.save_markdown,
            save_json=config.logging.save_json_trace,
        )
        written = [str(path) for path in asdict(outputs).values() if path]
        state.events.append(RunEvent("OUTPUT_WRITTEN", iso_now(), {"paths": written}))
        state.events.append(RunEvent("RUN_COMPLETED", iso_now()))
        if outputs.json_trace:
            outputs.json_trace.write_text(
                json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
            )
        _checkpoint(checkpoint_dir, state, "completed")
        return RunResult(state, outputs)
    except Exception as exc:
        state.events.append(RunEvent("RUN_FAILED", iso_now(), {"error": str(exc)}))
        _checkpoint(checkpoint_dir, state, "failed")
        raise


def _checkpoint(directory: Path, state: DebateState, stage: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{state.run_id}-{stage}.json"
    path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
