from __future__ import annotations

import re
from typing import Any


LENS_FOCUS = {
    "freud": ("conflict and defensive patterns", "unconscious explanations require developmental evidence"),
    "jung": ("persona, complexes, and symbolic meaning", "symbolism remains interpretive"),
    "skinner": ("observable antecedents and consequences", "private motives are not directly observed"),
    "rogers": ("self-concept, congruence, and conditions of worth", "subjective experience is underreported"),
    "beck": ("situations, thoughts, emotions, and behavior", "automatic thoughts were not directly reported"),
    "bowlby": ("relationship and proximity patterns", "attachment style cannot be determined from this case"),
    "frankl": ("meaning, values, and existential tension", "values and meaning were not explicitly elicited"),
    "ellis": ("activating events, beliefs, and consequences", "rigid beliefs need direct evidence"),
}


class MockProvider:
    """Deterministic educational provider used by tests and credential-free demos."""

    async def generate(
        self,
        *,
        task: str,
        prompt: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        del prompt
        handler = getattr(self, f"_{task}", None)
        if handler is None:
            raise ValueError(f"Unsupported mock task: {task}")
        return handler(context)

    def _intake(self, context: dict[str, Any]) -> dict[str, Any]:
        content = str(context["case"]["content"])
        sentences = [part.strip(" -\n") for part in re.split(r"(?<=[.!?])\s+|\n+", content) if part.strip()]
        facts = sentences[:5]
        lower = content.lower()
        risks = []
        for label, terms in {
            "possible self-harm content": ("self-harm", "self harm", "tự hại"),
            "possible suicidal content": ("suicide", "suicidal", "tự sát"),
            "possible violence content": ("violence", "violent", "bạo lực"),
            "possible immediate danger": ("immediate danger", "nguy hiểm tức thời"),
        }.items():
            if any(term in lower for term in terms):
                risks.append(label)
        missing = ["duration and timeline", "the person's own account", "broader context"]
        if len(content.split()) < 40:
            missing.insert(0, "more detailed case information")
        return {
            "case_summary": " ".join(sentences[:2]),
            "observable_facts": facts,
            "reported_experiences": [],
            "behaviors": facts,
            "relationships": [],
            "contextual_factors": [],
            "timeline": [],
            "missing_information": missing,
            "ambiguities": ["The case does not establish causation."],
            "risk_flags": risks,
        }

    def _analysis(self, context: dict[str, Any]) -> dict[str, Any]:
        key = str(context["agent"])
        focus, limitation = LENS_FOCUS[key]
        observations = list(context["intake"].get("observable_facts", []))[:2]
        evidence = observations[:1]
        return {
            "case_observations_used": observations,
            "primary_interpretation": f"This lens explores {focus} as one possible account.",
            "possible_causal_mechanisms": [f"A pattern involving {focus} may be maintaining the reported difficulty."],
            "alternative_hypotheses": ["Situational stressors may offer a simpler explanation."],
            "missing_information": list(context["intake"].get("missing_information", []))[:2],
            "explains_well": f"It organizes observations around {focus}.",
            "explains_poorly": limitation,
            "claims": [
                {
                    "claim": f"The observed pattern may be understood through {focus}.",
                    "epistemic_type": "HYPOTHESIS",
                    "supporting_case_evidence": evidence,
                    "confidence": "medium" if evidence else "low",
                }
            ],
            "confidence": "medium",
        }

    def _critique(self, context: dict[str, Any]) -> dict[str, Any]:
        target = context["target_claim"]
        evidence = list(target.get("supporting_case_evidence", []))
        return {
            "agreement": "The claim is framed as a possibility rather than a fact.",
            "challenge": "The proposed mechanism is not uniquely established by the available evidence.",
            "case_evidence": evidence,
            "counter_hypothesis": "Contextual or observable learning factors may explain the same pattern.",
        }

    def _revision(self, context: dict[str, Any]) -> dict[str, Any]:
        claim = context["claim"]
        return {
            "decision": "PARTIALLY_REVISE",
            "claim": str(claim["claim"]) + " This remains tentative and is not the only explanation.",
            "evidence": list(claim.get("supporting_case_evidence", [])),
            "concise_rationale": "The critique identifies plausible alternative mechanisms.",
            "counterargument_considered": str(context["challenges"][0]["challenge"]),
        }

    def _validation(self, context: dict[str, Any]) -> dict[str, Any]:
        claim = context["claim"]
        text = str(claim["claim"])
        evidence = list(claim.get("supporting_case_evidence", []))
        unsafe_certainty = bool(re.search(r"\b(has|suffers from)\s+(major depressive disorder|[a-z ]+ disorder)\b", text, re.I))
        return {
            "epistemic_type": "HYPOTHESIS" if unsafe_certainty else claim["epistemic_type"],
            "case_evidence": evidence,
            "missing_evidence": [] if evidence else ["No direct case evidence was linked."],
            "confidence": "low" if unsafe_certainty or not evidence else claim["confidence"],
            "overreach_risk": "high" if unsafe_certainty else "low",
            "contradictions": [],
            "notes": "Diagnostic certainty is not permitted." if unsafe_certainty else "Uncertainty is retained.",
        }

    def _synthesis(self, context: dict[str, Any]) -> dict[str, Any]:
        validations = context["validation_results"]
        unsupported = [item["claim"] for item in validations if item["overreach_risk"] == "high"]
        return {
            "consensus": ["The case supports multiple plausible interpretations."],
            "disagreements": ["Lenses differ in the mechanisms they prioritize."],
            "complementary_perspectives": ["Observable, cognitive, relational, and meaning-focused accounts can be compared."],
            "unsupported_claims": unsupported,
            "unresolved_hypotheses": [item["claim"] for item in validations if item["confidence"] != "high"],
            "evidence_needed": list(context.get("unresolved_questions", [])),
            "reflection_questions": [
                "Which lens relied most on directly observable evidence?",
                "Which lens relied most on inference?",
                "Was the largest disagreement about evidence or theory?",
                "What additional evidence would most change the debate?",
                "Which two lenses appear complementary?",
                "Which claim changed most during the debate?",
            ],
        }
