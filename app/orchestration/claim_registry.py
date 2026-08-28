from __future__ import annotations

from app.agents.psychology import normalize_claim_payload
from app.models import Claim, ClaimStatus, Confidence, Critique, EpistemicType, Revision, RevisionDecision
from app.safety import sanitize_educational_text


class ClaimRegistry:
    def __init__(self, claims: dict[str, Claim] | None = None) -> None:
        self.claims = claims if claims is not None else {}

    def register(self, agent: str, payload: dict, round_created: int = 0) -> Claim:
        text, epistemic_type, evidence, confidence = normalize_claim_payload(payload)
        text, safety_flags = sanitize_educational_text(text)
        if safety_flags:
            epistemic_type = EpistemicType.HYPOTHESIS
            confidence = Confidence.LOW
        claim_id = f"CLM-{len(self.claims) + 1:03d}"
        claim = Claim(
            claim_id=claim_id,
            agent=agent,
            round_created=round_created,
            claim=text,
            epistemic_type=epistemic_type,
            supporting_case_evidence=evidence,
            confidence=confidence,
        )
        self.claims[claim_id] = claim
        return claim

    def challenge(self, critique: Critique) -> None:
        claim = self.claims[critique.claim_id]
        if critique.critic_agent not in claim.challenged_by:
            claim.challenged_by.append(critique.critic_agent)
        claim.challenges.append(
            {
                "round": critique.round_number,
                "critic_agent": critique.critic_agent,
                "challenge": critique.challenge,
                "case_evidence": critique.case_evidence,
            }
        )
        claim.status = ClaimStatus.CHALLENGED

    def apply_revision(self, revision: Revision) -> None:
        claim = self.claims[revision.claim_id]
        safe_text, safety_flags = sanitize_educational_text(revision.claim)
        claim.revision_history.append(
            {
                "round": revision.round_number,
                "decision": revision.decision.value,
                "previous_claim": claim.claim,
                "revised_claim": safe_text,
                "evidence": revision.evidence,
                "concise_rationale": revision.concise_rationale,
                "counterargument_considered": revision.counterargument_considered,
                "safety_flags": safety_flags,
            }
        )
        if revision.decision is RevisionDecision.WITHDRAW_CLAIM:
            claim.status = ClaimStatus.WITHDRAWN
        elif revision.decision in {RevisionDecision.REVISE, RevisionDecision.PARTIALLY_REVISE}:
            claim.claim = safe_text
            claim.supporting_case_evidence = revision.evidence
            claim.status = ClaimStatus.REVISED
        else:
            claim.status = ClaimStatus.DISPUTED if claim.challenged_by else ClaimStatus.ACTIVE
