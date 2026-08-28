from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app.models import OutputMode


class ConfigurationError(ValueError):
    """Raised when runtime configuration cannot be used safely."""


@dataclass(frozen=True, slots=True)
class LLMSettings:
    provider: str
    model: str
    temperature: float
    max_output_tokens: int


@dataclass(frozen=True, slots=True)
class DebateSettings:
    rounds: int
    max_agents: int
    parallel_independent_analysis: bool
    cross_critique_strategy: str
    allow_agent_revision: bool


@dataclass(frozen=True, slots=True)
class OutputSettings:
    mode: OutputMode
    include_raw_agent_outputs: bool
    include_epistemic_map: bool
    include_debate_transcript: bool
    include_final_summary: bool


@dataclass(frozen=True, slots=True)
class SafetySettings:
    educational_only: bool
    prohibit_clinical_diagnosis: bool
    prohibit_medication_advice: bool
    flag_crisis_content: bool


@dataclass(frozen=True, slots=True)
class LoggingSettings:
    save_markdown: bool
    save_json_trace: bool


@dataclass(frozen=True, slots=True)
class RuntimeSettings:
    retries: int


@dataclass(frozen=True, slots=True)
class AgentSettings:
    key: str
    display_name: str
    enabled: bool


@dataclass(frozen=True, slots=True)
class AppConfig:
    llm: LLMSettings
    debate: DebateSettings
    output: OutputSettings
    safety: SafetySettings
    logging: LoggingSettings
    runtime: RuntimeSettings
    agents: tuple[AgentSettings, ...]


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Cannot read configuration {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigurationError(f"Configuration {path} must contain a YAML mapping")
    return value


def load_config(
    settings_path: Path = Path("config/settings.yaml"),
    agents_path: Path = Path("config/agents.yaml"),
) -> AppConfig:
    raw = _read_yaml(settings_path)
    raw_agents = _read_yaml(agents_path).get("agents")
    if not isinstance(raw_agents, dict) or not raw_agents:
        raise ConfigurationError("agents.yaml must define a non-empty 'agents' mapping")
    try:
        llm = LLMSettings(**raw["llm"])
        debate = DebateSettings(**raw["debate"])
        output_raw = dict(raw["output"])
        output_raw["mode"] = OutputMode(output_raw["mode"])
        output = OutputSettings(**output_raw)
        safety = SafetySettings(**raw["safety"])
        logging = LoggingSettings(**raw["logging"])
        runtime = RuntimeSettings(**raw["runtime"])
        agents = tuple(
            AgentSettings(
                key=str(key),
                enabled=bool(value.get("enabled", True)),
                display_name=str(value.get("display_name", key)),
            )
            for key, value in raw_agents.items()
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(f"Invalid configuration: {exc}") from exc

    if debate.rounds < 1:
        raise ConfigurationError("debate.rounds must be at least 1")
    if debate.max_agents < 2:
        raise ConfigurationError("debate.max_agents must be at least 2")
    if debate.cross_critique_strategy != "round_robin":
        raise ConfigurationError("Only debate.cross_critique_strategy='round_robin' is supported")
    enabled_count = sum(agent.enabled for agent in agents)
    if enabled_count < 2:
        raise ConfigurationError("At least two psychology agents must be enabled")
    if enabled_count > debate.max_agents:
        raise ConfigurationError("Enabled agent count exceeds debate.max_agents")
    if runtime.retries < 0:
        raise ConfigurationError("runtime.retries cannot be negative")
    if not 0 <= llm.temperature <= 2:
        raise ConfigurationError("llm.temperature must be between 0 and 2")
    if llm.max_output_tokens < 1:
        raise ConfigurationError("llm.max_output_tokens must be positive")
    if llm.provider not in {"openai", "mock"}:
        raise ConfigurationError("llm.provider must be 'openai' or 'mock'")
    return AppConfig(llm, debate, output, safety, logging, runtime, agents)
