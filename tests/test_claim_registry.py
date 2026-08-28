from app.models import Critique, Revision, RevisionDecision
from app.orchestration.claim_registry import ClaimRegistry


def test_challenged_claim_can_be_partially_revised() -> None:
    registry = ClaimRegistry()
    claim = registry.register(
        "beck",
        {
            "claim": "Avoidance may be maintained by anticipated judgment.",
            "epistemic_type": "HYPOTHESIS",
            "supporting_case_evidence": ["The person reported fear of judgment."],
            "confidence": "medium",
        },
    )
    registry.challenge(Critique(1, "skinner", "beck", claim.claim_id, "Possible", "No contingency data", [], "Learning history"))
    registry.apply_revision(
        Revision(
            1,
            "beck",
            claim.claim_id,
            RevisionDecision.PARTIALLY_REVISE,
            "Anticipated judgment is one tentative maintaining factor.",
            claim.supporting_case_evidence,
            "Alternative mechanisms remain possible.",
            "No contingency data",
        )
    )
    assert claim.status.value == "revised"
    assert claim.revision_history[0]["decision"] == "PARTIALLY_REVISE"
