from __future__ import annotations

from app.models import DebateState
from app.safety import educational_safety_note, sanitize_educational_text


def _items(values: list[str], empty: str = "Not established from the case.") -> str:
    if not values:
        return f"- {empty}"
    return "\n".join(f"- {sanitize_educational_text(str(item))[0]}" for item in values)


def render_log(state: DebateState) -> str:
    intake = state.intake
    synthesis = state.synthesis
    assert intake is not None and synthesis is not None
    sections = [
        "# Psychology Multi-Agent Critique",
        "## Run Metadata",
        f"- Run ID: `{state.run_id}`\n- Case: {state.case.title}\n- Debate rounds: {state.round_number}\n- Agents: {', '.join(state.enabled_agents)}",
        "## Original Case",
        state.case.content,
        "## Structured Intake",
        intake.case_summary,
        "## Missing Information",
        _items(intake.missing_information),
        "# Independent Analyses",
    ]
    for analysis in state.analyses.values():
        sections.extend(
            [
                f"## {analysis.lens}",
                f"**Observations used**\n{_items(analysis.case_observations_used)}\n\n"
                f"**Primary interpretation**\n{sanitize_educational_text(analysis.primary_interpretation)[0]}\n\n"
                f"**Alternatives**\n{_items(analysis.alternative_hypotheses)}\n\n"
                f"**Limit**\n{analysis.explains_poorly}",
            ]
        )
    for round_number in range(1, state.round_number + 1):
        sections.extend([f"# Debate Round {round_number}", "## Critiques"])
        for item in [c for c in state.critiques if c.round_number == round_number]:
            sections.append(
                f"### {item.critic_agent} → {item.target_agent} / {item.claim_id}\n"
                f"Agreement: {item.agreement}\n\nChallenge: {item.challenge}\n\n"
                f"Counter-hypothesis: {item.counter_hypothesis}"
            )
        sections.append("## Revisions")
        for item in [r for r in state.revisions if r.round_number == round_number]:
            sections.append(
                f"### {item.agent} / {item.claim_id}: {item.decision.value}\n"
                f"{sanitize_educational_text(item.claim)[0]}\n\nRationale: {item.concise_rationale}"
            )
    sections.extend(["# Claim Evolution"])
    for claim in state.claim_registry.values():
        sections.append(
            f"## {claim.claim_id} — {claim.agent}\nInitial round: {claim.round_created}; "
            f"Final status: **{claim.status.value}**\n\n{claim.claim}\n\n"
            f"Challenges: {len(claim.challenges)}; revisions: {len(claim.revision_history)}"
        )
    sections.extend(
        [
            "# Epistemic Validation",
            *[
                f"- **{v.claim_id}** [{v.epistemic_type.value}, {v.confidence.value}] "
                f"{sanitize_educational_text(v.claim)[0]} — {v.notes}"
                for v in state.validation_results
            ],
            "# Consensus",
            _items(synthesis.consensus),
            "# Major Disagreements",
            _items(synthesis.disagreements),
            "# Missing Evidence",
            _items(synthesis.evidence_needed),
            "# Unresolved Hypotheses",
            _items(synthesis.unresolved_hypotheses),
            "# Final Synthesis",
            _items(synthesis.complementary_perspectives),
            "# Reflection Questions",
            "\n".join(f"{i}. {q}" for i, q in enumerate(synthesis.reflection_questions, 1)),
            "# Educational Safety Note",
            educational_safety_note(intake.risk_flags),
        ]
    )
    return "\n\n".join(sections) + "\n"


def render_analyse(state: DebateState) -> str:
    intake = state.intake
    synthesis = state.synthesis
    assert intake is not None and synthesis is not None
    rows = []
    for item in state.analyses.values():
        evidence = "; ".join(item.case_observations_used) or "None linked"
        rows.append(
            f"| {item.lens} | {item.primary_interpretation} | {evidence} | "
            f"{item.missing_information[0] if item.missing_information else 'None stated'} | {item.explains_poorly} |"
        )
    claim_evolution = [
        f"- **{c.claim_id} ({c.agent})**: {c.status.value}; {len(c.challenges)} challenge(s), "
        f"{len(c.revision_history)} revision(s)."
        for c in state.claim_registry.values()
    ]
    epistemic = [
        f"- **{v.claim_id}** — {v.epistemic_type.value}, confidence {v.confidence.value}, "
        f"overreach risk {v.overreach_risk}."
        for v in state.validation_results
    ]
    sections = [
        f"# Case Analysis — {state.case.title}",
        "## 1. Case Framing",
        intake.case_summary,
        "## 2. Facts Available",
        _items(intake.observable_facts),
        "## 3. Missing Information",
        _items(intake.missing_information),
        "## 4. Perspectives by Psychological School",
        "\n\n".join(f"### {a.lens}\n{a.primary_interpretation}" for a in state.analyses.values()),
        "## 5. Comparative Matrix",
        "| Lens | Main Explanation | Evidence Used | Key Evidence Gap | Limitation |\n|---|---|---|---|---|\n" + "\n".join(rows),
        "## 6. Competing Hypotheses",
        _items(synthesis.unresolved_hypotheses),
        "## 7. Causal Interpretations",
        _items([m for a in state.analyses.values() for m in a.possible_causal_mechanisms]),
        "## 8. Areas of Agreement",
        _items(synthesis.consensus),
        "## 9. Areas of Disagreement",
        _items(synthesis.disagreements),
        "## 10. Claim Evolution",
        "\n".join(claim_evolution),
        "## 11. Epistemic Map",
        "\n".join(epistemic),
        "## 12. What Cannot Be Concluded",
        _items(synthesis.unsupported_claims or ["No diagnosis or definitive psychological cause can be concluded."]),
        "## 13. Questions for Further Study",
        _items(synthesis.reflection_questions),
        "## 14. Learning Takeaways",
        _items(synthesis.complementary_perspectives),
        "## Educational Safety Note",
        educational_safety_note(intake.risk_flags),
    ]
    return "\n\n".join(sections) + "\n"


def render_consulting(state: DebateState) -> str:
    intake = state.intake
    synthesis = state.synthesis
    assert intake is not None and synthesis is not None
    lens_questions = [f"Examine with {a.lens}: {a.explains_well}" for a in state.analyses.values()]
    exercises = [
        "Re-label three claims as fact, interpretation, assumption, hypothesis, or recommendation.",
        "Identify the claim that changed most and reconstruct its evidence trail.",
        "Choose one disagreement and list evidence that could discriminate the hypotheses.",
    ]
    sections = [
        f"# Educational Consultation — {state.case.title}",
        "## 1. Important Areas to Explore",
        _items(synthesis.evidence_needed),
        "## 2. Questions to Ask Before Drawing Conclusions",
        _items(intake.missing_information + intake.ambiguities),
        "## 3. Alternative Interpretations Worth Testing",
        _items(synthesis.unresolved_hypotheses),
        "## 4. What Each Psychological Lens Suggests Examining",
        _items(lens_questions),
        "## 5. Potential Blind Spots",
        _items([a.explains_poorly for a in state.analyses.values()]),
        "## 6. Evidence Needed to Distinguish Hypotheses",
        _items(synthesis.evidence_needed),
        "## 7. Suggested Learning Exercises",
        _items(exercises),
        "## 8. When Professional Assessment May Be Appropriate",
        "Professional assessment may be appropriate when distress, impairment, risk, or diagnostic questions require qualified evaluation.",
        "## 9. Limits of This Analysis",
        educational_safety_note(intake.risk_flags),
    ]
    return "\n\n".join(sections) + "\n"
