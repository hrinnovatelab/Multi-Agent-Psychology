from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class EpistemicType(str, Enum):
    FACT = "FACT"
    INTERPRETATION = "INTERPRETATION"
    ASSUMPTION = "ASSUMPTION"
    HYPOTHESIS = "HYPOTHESIS"
    RECOMMENDATION = "RECOMMENDATION"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ClaimStatus(str, Enum):
    ACTIVE = "active"
    CHALLENGED = "challenged"
    REVISED = "revised"
    WITHDRAWN = "withdrawn"
    DISPUTED = "disputed"
    CONVERGED = "converged"


class RevisionDecision(str, Enum):
    DEFEND = "DEFEND"
    REVISE = "REVISE"
    PARTIALLY_REVISE = "PARTIALLY_REVISE"
    WITHDRAW_CLAIM = "WITHDRAW_CLAIM"


class OutputMode(str, Enum):
    ANALYSE = "analyse"
    CONSULTING = "consulting"
    BOTH = "both"


@dataclass(slots=True)
class CaseRecord:
    name: str
    title: str
    content: str
    source_path: str


@dataclass(slots=True)
class IntakeResult:
    case_name: str
    case_summary: str
    observable_facts: list[str] = field(default_factory=list)
    reported_experiences: list[str] = field(default_factory=list)
    behaviors: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    contextual_factors: list[str] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    ambiguities: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AgentAnalysis:
    agent: str
    lens: str
    case_observations_used: list[str]
    primary_interpretation: str
    possible_causal_mechanisms: list[str]
    alternative_hypotheses: list[str]
    missing_information: list[str]
    explains_well: str
    explains_poorly: str
    claims: list[dict[str, Any]]
    confidence: Confidence = Confidence.MEDIUM


@dataclass(slots=True)
class Critique:
    round_number: int
    critic_agent: str
    target_agent: str
    claim_id: str
    agreement: str
    challenge: str
    case_evidence: list[str]
    counter_hypothesis: str


@dataclass(slots=True)
class Revision:
    round_number: int
    agent: str
    claim_id: str
    decision: RevisionDecision
    claim: str
    evidence: list[str]
    concise_rationale: str
    counterargument_considered: str


@dataclass(slots=True)
class Claim:
    claim_id: str
    agent: str
    round_created: int
    claim: str
    epistemic_type: EpistemicType
    supporting_case_evidence: list[str]
    challenged_by: list[str] = field(default_factory=list)
    challenges: list[dict[str, Any]] = field(default_factory=list)
    revision_history: list[dict[str, Any]] = field(default_factory=list)
    status: ClaimStatus = ClaimStatus.ACTIVE
    confidence: Confidence = Confidence.MEDIUM


@dataclass(slots=True)
class ValidationResult:
    claim_id: str
    claim: str
    agent: str
    epistemic_type: EpistemicType
    case_evidence: list[str]
    missing_evidence: list[str]
    confidence: Confidence
    overreach_risk: str
    contradictions: list[str]
    notes: str


@dataclass(slots=True)
class Synthesis:
    consensus: list[str]
    disagreements: list[str]
    complementary_perspectives: list[str]
    unsupported_claims: list[str]
    unresolved_hypotheses: list[str]
    evidence_needed: list[str]
    reflection_questions: list[str]
    missing_participants: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RunEvent:
    event: str
    timestamp: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DebateState:
    run_id: str
    case: CaseRecord
    enabled_agents: list[str]
    round_number: int = 0
    intake: IntakeResult | None = None
    analyses: dict[str, AgentAnalysis] = field(default_factory=dict)
    critiques: list[Critique] = field(default_factory=list)
    revisions: list[Revision] = field(default_factory=list)
    claim_registry: dict[str, Claim] = field(default_factory=dict)
    unresolved_questions: list[str] = field(default_factory=list)
    validation_results: list[ValidationResult] = field(default_factory=list)
    synthesis: Synthesis | None = None
    events: list[RunEvent] = field(default_factory=list)
    failed_agents: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(asdict(self))


def _to_primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _to_primitive(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_primitive(item) for item in value]
    return value
